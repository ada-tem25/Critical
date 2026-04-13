"""
Analysis Workflow — Layer 2 (LangGraph).
Called once per claim by the Orchestrator.
Routes by verifiability, then executes the appropriate analysis branch.

Input:  Claim + child_results
Output: AnalyzedClaim
"""
from typing_extensions import TypedDict
from langgraph.graph import StateGraph, START, END
from models import Claim, AnalyzedClaim
from nodes.generate_queries import generate_queries_l2
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
    needs_level3: bool

    # L2 reflexive loop fields (NOUVEAU)
    all_search_results: list[dict]   # Brave results, cumulative across iterations
    selected_sources: list[dict]     # Top sources after ranking (current iteration)
    extracted_passages: list[dict]   # Extracted passages, cumulative across iterations
    failed_urls: list[str]           # URLs that returned 403/error, excluded from future ranking
    loop_count: int                  # Reflection loop counter, init 0, max 2
    sufficient: bool                 # Reflection output

    # L3 intermediate fields
    queries_l3: list[str]
    search_results_l3: list[dict]
    analysis: str

    # Final output
    analyzed: bool
    sources: list[dict]

    # Metrics (accumulated across nodes)
    passes: list[dict]


# =================== Nodes ========================================

async def generate_queries(state: AnalysisState) -> dict:
    """Generates 1-3 search queries to verify the claim."""
    queries, metrics = await generate_queries_l2(
        claim_id=state["claim_id"],
        idea=state["idea"],
        claim_type=state.get("type", ""),
        child_results=state.get("child_results", []),
        country=state.get("country", "INT"),
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
    new_passages = [p for p in extracted if p["url"] not in seen_urls]

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
    )
    return {
        "summary": result["summary"],
        "needs_level3": result["needs_level3"],
        "sources": result["sources"],
        "analyzed": True,
        "passes": state.get("passes", []) + metrics.get("passes", []),
    }


def level3_placeholder(state: AnalysisState) -> dict:
    """Placeholder for Level 3 analysis (not yet implemented)."""
    print(f"    [L3] Claim #{state['claim_id']} routed to Level 3 (not yet implemented)")
    return {}


# =================== Conditional edges ========================================

def route_by_verifiability(state: AnalysisState) -> str:
    """Entry routing: dispatches to the right branch based on verifiability."""
    v = state.get("verifiability", "")
    if v in ("B", "C"):
        return "generate_queries"
    elif v == "D":
        return "level3_placeholder"
    else:
        print(f"    [ROUTER] WARNING: unexpected verifiability '{v}' for claim #{state.get('claim_id')}, skipping")
        return "level3_placeholder"


MAX_RESEARCH_LOOPS = 1  # Max reflection loop iterations (increase later if needed)


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


def route_after_reflection(state: AnalysisState) -> str:
    """After reflection: route to synthesizer if sufficient or max loops, else loop back."""
    if state.get("sufficient") or state.get("loop_count", 0) > MAX_RESEARCH_LOOPS:
        return "synthesizer"
    return "brave_search"


# =================== Graph construction =======================================

def _build_graph() -> StateGraph:
    graph = StateGraph(AnalysisState)

    # All nodes
    graph.add_node("generate_queries", generate_queries)
    graph.add_node("brave_search", brave_search_node)
    graph.add_node("rank_and_select", rank_select_node)
    graph.add_node("fetch_extract", fetch_extract_node)
    graph.add_node("reflection", reflection_node)
    graph.add_node("synthesizer", synthesizer_node)
    graph.add_node("level3_placeholder", level3_placeholder)

    # Entry: conditional edge from START
    graph.add_conditional_edges(START, route_by_verifiability)

    # L2 fact-checking loop (NOUVEAU — Brave + fetch + reflection loop)
    graph.add_edge("generate_queries", "brave_search")
    graph.add_edge("brave_search", "rank_and_select")
    graph.add_conditional_edges("rank_and_select", route_after_ranking)
    graph.add_edge("fetch_extract", "reflection")
    graph.add_conditional_edges("reflection", route_after_reflection)
    graph.add_edge("synthesizer", END)

    # D branch #TODO
    graph.add_edge("level3_placeholder", END)

    return graph


# Compile once at module level
workflow = _build_graph().compile()


# =================== Entry point ==============================================

async def run_analysis(claim: Claim, child_results: list[dict], country: str = "INT") -> tuple[AnalyzedClaim, dict]:
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
