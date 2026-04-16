"""
Analysis Workflow — LangGraph.
Called once per claim by the Orchestrator.
Routes by verifiability, then executes the appropriate analysis branch.

Input:  Claim + child_results
Output: AnalyzedClaim
"""
from typing_extensions import TypedDict
from langgraph.graph import StateGraph, START, END
from models import Claim, AnalyzedClaim
from nodes.generate_queries import generate_queries
from nodes.synthesizer import synthesize
from nodes.brave_search import brave_search
from nodes.rank_and_select import rank_and_select
from nodes.fetch_extract import fetch_and_extract
from nodes.reflection import reflect


# =================== Internal State ===========================================

class AnalysisState(TypedDict, total=False):
    # Copied from the input Claim at invocation
    claim_id: int
    idea: str
    verifiability: str          # "B", "C", "D"
    type: str                   # "factual", "statistical", "quote", "event", "causal", "comparative", "predictive", "opinion"
    role: str                   # "thesis", "supporting", "counterargument"
    supports: list[int]
    child_results: list[dict]

    country: str                # ISO code: "FR", "US", "INT", etc.

    # L2 intermediate fields
    queries_l2: list[str]
    search_results: list[dict]
    summary: str
    needs_next_level: bool

    # L2 reflexive loop fields
    all_search_results: list[dict]   # Brave results, cumulative across iterations
    selected_sources: list[dict]     # Top sources after ranking (current iteration)
    extracted_passages: list[dict]   # Extracted passages, cumulative across iterations
    failed_urls: list[str]           # URLs that returned 403/error, excluded from future ranking
    loop_count: int                  # Reflection loop counter, init 0
    max_loops: int                   # Max reflection loops: 1 (eco) or 2 (perf)
    sufficient: bool                 # Reflection output

    # L3 loop fields
    queries_l3: list[str]
    all_search_results_l3: list[dict]
    selected_sources_l3: list[dict]
    extracted_passages_l3: list[dict]
    failed_urls_l3: list[str]
    l3_loop_count: int
    l3_max_loops: int
    l3_sufficient: bool
    analysis: str

    # Final output
    analyzed: bool
    sources: list[dict]

    # Metrics (accumulated across nodes)
    passes: list[dict]


# =================== L2 Nodes ================================================

async def generate_queries_node(state: AnalysisState) -> dict:
    """Generates 1-3 search queries to verify the claim."""
    queries, metrics = await generate_queries(
        claim_id=state["claim_id"],
        idea=state["idea"],
        claim_type=state.get("type", ""),
        child_results=state.get("child_results", []),
        country=state.get("country", "INT"),
        analysis_level="l2",
    )
    return {"queries_l2": queries, "passes": state.get("passes", []) + metrics.get("passes", [])}


async def brave_search_node(state: AnalysisState) -> dict:
    """Executes Brave search for current queries, cumulates results."""
    queries = state.get("queries_l2", [])
    country = state.get("country", "INT")

    results, metrics = await brave_search(queries, country)

    # Cumulate with previous iterations
    prev_results = state.get("all_search_results", [])
    # Dedup by URL across iterations
    seen_urls = {r["url"] for r in prev_results}
    new_results = [r for r in results if r["url"] not in seen_urls]

    return {
        "all_search_results": prev_results + new_results,
        "passes": state.get("passes", []) + metrics.get("passes", []),
    }


async def rank_select_node(state: AnalysisState) -> dict:
    """Ranks and selects top sources from current search results."""
    results = state.get("all_search_results", [])
    idea = state.get("idea", "")
    queries = state.get("queries_l2", [])
    excluded = set(state.get("failed_urls", []))

    selected = rank_and_select(results, idea, queries, excluded_urls=excluded)
    return {"selected_sources": selected}


async def fetch_extract_node(state: AnalysisState) -> dict:
    """Fetches pages and extracts relevant passages, cumulates."""
    sources = state.get("selected_sources", [])
    idea = state.get("idea", "")
    queries = state.get("queries_l2", [])

    extracted, metrics, new_failed = await fetch_and_extract(sources, idea, queries)

    # Cumulate with previous iterations, dedup by URL
    prev_passages = state.get("extracted_passages", [])
    seen_urls = {p["url"] for p in prev_passages}
    new_passages = [p for p in extracted if p["url"] not in seen_urls and not p.get("fetch_failed")]

    # Accumulate failed URLs
    prev_failed = state.get("failed_urls", [])

    return {
        "extracted_passages": prev_passages + new_passages,
        "failed_urls": prev_failed + new_failed,
    }


async def reflection_node(state: AnalysisState) -> dict:
    """Evaluates if we have enough material, or need another research loop."""
    passages = state.get("extracted_passages", [])
    loop_count = state.get("loop_count", 0)

    result, metrics = await reflect(
        claim_idea=state.get("idea", ""),
        claim_type=state.get("type", ""),
        child_results=state.get("child_results", []),
        passages=passages,
        loop_count=loop_count,
        analysis_level="l2",
    )

    update = {
        "loop_count": loop_count + 1,
        "sufficient": result["sufficient"],
        "passes": state.get("passes", []) + metrics.get("passes", []),
    }

    # If insufficient, update queries for next loop iteration
    if not result["sufficient"] and result.get("follow_up_queries"):
        update["queries_l2"] = result["follow_up_queries"]

    return update


async def synthesizer_node(state: AnalysisState) -> dict:
    """Evaluates the solidity of the author's argument for this claim."""

    # Assign 1-indexed IDs to extracted passages (deduped) before passing to synthesizer
    passages = state.get("extracted_passages", [])
    for i, p in enumerate(passages):
        p["id"] = i + 1

    result, metrics = await synthesize(
        claim_id=state["claim_id"],
        idea=state["idea"],
        claim_type=state.get("type", ""),
        child_results=state.get("child_results", []),
        sources=passages,
        analysis_level="l2",
    )
    return {
        "summary": result["summary"],
        "needs_next_level": result["needs_next_level"],
        "sources": result["sources"],
        "analyzed": True,
        "passes": state.get("passes", []) + metrics.get("passes", []),
    }


# =================== L3 Nodes ================================================

async def generate_queries_l3_node(state: AnalysisState) -> dict:
    """Generates 1-3 search queries for L3 political/opinion analysis."""
    queries, metrics = await generate_queries(
        claim_id=state["claim_id"],
        idea=state["idea"],
        claim_type=state.get("type", ""),
        child_results=state.get("child_results", []),
        country=state.get("country", "INT"),
        l2_summary=state.get("summary", ""),
        analysis_level="l3",
    )
    return {"queries_l3": queries, "passes": state.get("passes", []) + metrics.get("passes", [])}


async def brave_search_l3_node(state: AnalysisState) -> dict:
    """Executes Brave search for L3 queries, cumulates results."""
    queries = state.get("queries_l3", [])
    country = state.get("country", "INT")

    results, metrics = await brave_search(queries, country)

    prev = state.get("all_search_results_l3", [])
    seen = {r["url"] for r in prev}
    new = [r for r in results if r["url"] not in seen]

    return {
        "all_search_results_l3": prev + new,
        "passes": state.get("passes", []) + metrics.get("passes", []),
    }


async def rank_select_l3_node(state: AnalysisState) -> dict:
    """Ranks and selects top sources from L3 search results."""
    results = state.get("all_search_results_l3", [])
    idea = state.get("idea", "")
    queries = state.get("queries_l3", [])
    excluded = set(state.get("failed_urls_l3", []))

    selected = rank_and_select(results, idea, queries, excluded_urls=excluded)
    return {"selected_sources_l3": selected}


async def fetch_extract_l3_node(state: AnalysisState) -> dict:
    """Fetches pages and extracts relevant passages for L3, cumulates."""
    sources = state.get("selected_sources_l3", [])
    idea = state.get("idea", "")
    queries = state.get("queries_l3", [])

    extracted, metrics, new_failed = await fetch_and_extract(sources, idea, queries)

    prev = state.get("extracted_passages_l3", [])
    seen = {p["url"] for p in prev}
    new = [p for p in extracted if p["url"] not in seen and not p.get("fetch_failed")]
    prev_failed = state.get("failed_urls_l3", [])

    return {
        "extracted_passages_l3": prev + new,
        "failed_urls_l3": prev_failed + new_failed,
    }


async def reflection_l3_node(state: AnalysisState) -> dict:
    """Evaluates if L3 passages are sufficient, or need another research loop."""
    passages = state.get("extracted_passages_l3", [])
    loop_count = state.get("l3_loop_count", 0)

    result, metrics = await reflect(
        claim_idea=state.get("idea", ""),
        claim_type=state.get("type", ""),
        child_results=state.get("child_results", []),
        passages=passages,
        loop_count=loop_count,
        analysis_level="l3",
    )

    update = {
        "l3_loop_count": loop_count + 1,
        "l3_sufficient": result["sufficient"],
        "passes": state.get("passes", []) + metrics.get("passes", []),
    }

    if not result["sufficient"] and result.get("follow_up_queries"):
        update["queries_l3"] = result["follow_up_queries"]

    return update


async def synthesizer_l3_node(state: AnalysisState) -> dict:
    """Produces L3 political/opinion analysis based on sources."""

    passages = state.get("extracted_passages_l3", [])
    for i, p in enumerate(passages):
        p["id"] = i + 1

    result, metrics = await synthesize(
        claim_id=state["claim_id"],
        idea=state["idea"],
        claim_type=state.get("type", ""),
        child_results=state.get("child_results", []),
        sources=passages,
        l2_summary=state.get("summary", ""),
        analysis_level="l3",
    )

    # Merge L2 and L3 cited sources
    l2_sources = state.get("sources", [])
    l3_sources = result["sources"]

    return {
        "analysis": result["summary"],
        "needs_next_level": result["needs_next_level"],
        "sources": l2_sources + l3_sources,
        "analyzed": True,
        "passes": state.get("passes", []) + metrics.get("passes", []),
    }


# =================== L4 Placeholder ==========================================

def level4_placeholder(state: AnalysisState) -> dict:
    """Placeholder for Level 4 interpretive analysis (not yet implemented)."""
    print(f"    [L4] Claim #{state['claim_id']} routed to Level 4 (not yet implemented)")
    return {}


# =================== Conditional edges ========================================

def route_by_verifiability(state: AnalysisState) -> str:
    """Entry routing: dispatches to the right branch based on verifiability."""
    v = state.get("verifiability", "")
    if v in ("B", "C"):
        return "generate_queries"
    elif v == "D":
        t = state.get("type", "")
        if t == "opinion":
            return "generate_queries_l3"
        else:
            return "level4_placeholder"
    else:
        print(f"    [ROUTER] WARNING: unexpected verifiability '{v}' for claim #{state.get('claim_id')}, skipping")
        return "level4_placeholder"


def route_after_ranking(state: AnalysisState) -> str:
    """After ranking: skip to synthesizer if no new URLs to fetch."""
    selected_urls = {s["url"] for s in state.get("selected_sources", [])}
    already_extracted = {p["url"] for p in state.get("extracted_passages", [])}
    failed = set(state.get("failed_urls", []))
    new_urls = selected_urls - already_extracted - failed
    if len(new_urls) == 0:
        print(f"    [ROUTER] No new URLs to fetch — skipping to synthesizer")
        return "synthesizer"
    return "fetch_extract"


def route_after_fetch(state: AnalysisState) -> str:
    """After fetch: skip reflection on last allowed loop to save tokens."""
    loop_count = state.get("loop_count", 0)
    max_loops = state.get("max_loops", 1)
    if loop_count >= max_loops:
        print(f"    \033[2m[ROUTER] loop {loop_count} >= max_loops {max_loops} — skipping reflection\033[0m")
        return "synthesizer"
    return "reflection"


def route_after_reflection(state: AnalysisState) -> str:
    """After reflection: route to synthesizer if sufficient or max loops, else loop back."""
    max_loops = state.get("max_loops", 1)
    if state.get("sufficient") or state.get("loop_count", 0) > max_loops:
        return "synthesizer"
    return "brave_search"


def route_after_synthesizer(state: AnalysisState) -> str:
    """After L2 synthesis: route to L3 if needs_next_level and verifiability C, else END.
    B + needs_next_level is an error — go to END with warning."""
    if state.get("needs_next_level"):
        if state.get("verifiability") == "B":
            print(f"    \033[33m[ROUTER] WARNING: needs_next_level=true for B claim #{state.get('claim_id')} — skipping L3\033[0m")
            return END
        return "generate_queries_l3"
    return END


def route_after_ranking_l3(state: AnalysisState) -> str:
    """After L3 ranking: skip to L3 synthesizer if no new URLs to fetch."""
    selected = {s["url"] for s in state.get("selected_sources_l3", [])}
    extracted = {p["url"] for p in state.get("extracted_passages_l3", [])}
    failed = set(state.get("failed_urls_l3", []))
    new = selected - extracted - failed
    if len(new) == 0:
        print(f"    [ROUTER] No new L3 URLs to fetch — skipping to synthesizer L3")
        return "synthesizer_l3"
    return "fetch_extract_l3"


def route_after_fetch_l3(state: AnalysisState) -> str:
    """After L3 fetch: skip reflection on last allowed loop."""
    if state.get("l3_loop_count", 0) >= state.get("l3_max_loops", 0):
        print(f"    \033[2m[ROUTER] L3 loop {state.get('l3_loop_count', 0)} >= max {state.get('l3_max_loops', 0)} — skipping reflection L3\033[0m")
        return "synthesizer_l3"
    return "reflection_l3"


def route_after_reflection_l3(state: AnalysisState) -> str:
    """After L3 reflection: loop or proceed to synthesis."""
    if state.get("l3_sufficient") or state.get("l3_loop_count", 0) > state.get("l3_max_loops", 0):
        return "synthesizer_l3"
    return "brave_search_l3"


# =================== Graph construction =======================================

def _build_graph() -> StateGraph:
    graph = StateGraph(AnalysisState)

    # L2 nodes
    graph.add_node("generate_queries", generate_queries_node)
    graph.add_node("brave_search", brave_search_node)
    graph.add_node("rank_and_select", rank_select_node)
    graph.add_node("fetch_extract", fetch_extract_node)
    graph.add_node("reflection", reflection_node)
    graph.add_node("synthesizer", synthesizer_node)

    # L3 nodes
    graph.add_node("generate_queries_l3", generate_queries_l3_node)
    graph.add_node("brave_search_l3", brave_search_l3_node)
    graph.add_node("rank_select_l3", rank_select_l3_node)
    graph.add_node("fetch_extract_l3", fetch_extract_l3_node)
    graph.add_node("reflection_l3", reflection_l3_node)
    graph.add_node("synthesizer_l3", synthesizer_l3_node)

    # L4 placeholder
    graph.add_node("level4_placeholder", level4_placeholder)

    # Entry: conditional edge from START
    graph.add_conditional_edges(START, route_by_verifiability)

    # L2 fact-checking loop
    graph.add_edge("generate_queries", "brave_search")
    graph.add_edge("brave_search", "rank_and_select")
    graph.add_conditional_edges("rank_and_select", route_after_ranking)
    graph.add_conditional_edges("fetch_extract", route_after_fetch)
    graph.add_conditional_edges("reflection", route_after_reflection)

    # L2 → L3 or END
    graph.add_conditional_edges("synthesizer", route_after_synthesizer)

    # L3 political analysis loop
    graph.add_edge("generate_queries_l3", "brave_search_l3")
    graph.add_edge("brave_search_l3", "rank_select_l3")
    graph.add_conditional_edges("rank_select_l3", route_after_ranking_l3)
    graph.add_conditional_edges("fetch_extract_l3", route_after_fetch_l3)
    graph.add_conditional_edges("reflection_l3", route_after_reflection_l3)
    graph.add_edge("synthesizer_l3", END)

    # L4 placeholder
    graph.add_edge("level4_placeholder", END)

    return graph


# Compile once at module level
workflow = _build_graph().compile()


# =================== Entry point ==============================================

def _l3_max_loops(verifiability: str, mode: str) -> int:
    """Determine L3 max loops based on entry path and mode.
    D/opinion enters L3 directly: full loop budget.
    C enters L3 via needs_next_level: no loop, just initial search pass."""
    if verifiability == "D":
        return 1 if mode == "eco" else 2
    return 0


async def run_analysis(claim: Claim, child_results: list[dict], country: str = "INT", mode: str = "eco") -> tuple[AnalyzedClaim, dict]:
    """Runs the analysis workflow for a single claim.
    Takes a Claim + child_results + country, returns (AnalyzedClaim, metrics)."""

    # Build internal state from the Claim
    state: AnalysisState = {
        "claim_id": claim.id,
        "idea": claim.idea,
        "verifiability": claim.verifiability or "",
        "type": claim.type or "",
        "role": claim.role,
        "supports": claim.supports,
        "child_results": child_results,
        "country": country,
        "passes": [],
        "loop_count": 0,
        "max_loops": 1 if mode == "eco" else 2,
        "l3_loop_count": 0,
        "l3_max_loops": _l3_max_loops(claim.verifiability or "", mode),
    }

    result = await workflow.ainvoke(state)

    analyzed_claim = AnalyzedClaim(
        claim_id=claim.id,
        idea=claim.idea,
        role=claim.role,
        summary=result.get("summary", ""),
        analyzed=result.get("analyzed", False),
        supports=claim.supports,
        sources=[],  # TODO: convert result["sources"] to Source objects
        analysis=result.get("analysis"),
    )

    metrics = {"passes": result.get("passes", [])}
    return analyzed_claim, metrics
