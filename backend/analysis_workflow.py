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
from agents.generate_queries import generate_queries_l2


# =================== Internal State ===========================================

class AnalysisState(TypedDict, total=False):
    # Copied from the input Claim at invocation
    claim_id: int
    idea: str
    verifiability: str          # "A", "B", "C", "D"
    type: str                   # "factual", "statistical", "quote", "event", "causal", "comparative", "predictive", "opinion"
    role: str                   # "thesis", "supporting", "counterargument"
    supports: list[int]
    child_results: list[dict]

    # L2 intermediate fields
    queries_l2: list[str]
    search_results_unbiased: list[dict]
    sources_sufficient: bool
    search_results_biased: list[dict]
    summary: str
    needs_level3: bool

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

def common_knowledge_teacher(state: AnalysisState) -> dict:
    """Responds directly to verifiability-A claims without web search."""
    print(f"    [CK TEACHER] Answering common knowledge claim #{state['claim_id']}")
    return {"summary": "[placeholder — common knowledge teacher not yet implemented]", "analyzed": True, "sources": []}


async def generate_queries(state: AnalysisState) -> dict:
    """Generates 1-3 search queries to verify the claim."""
    queries, metrics = await generate_queries_l2(
        claim_id=state["claim_id"],
        idea=state["idea"],
        claim_type=state.get("type", ""),
        child_results=state.get("child_results", []),
    )
    return {"queries_l2": queries, "passes": state.get("passes", []) + metrics.get("passes", [])}


def web_research_unbiased(state: AnalysisState) -> dict:
    """Executes queries, retains only high-reliability sources."""
    print(f"    [WEB RESEARCH] Searching unbiased sources for claim #{state['claim_id']} ({len(state.get('queries_l2', []))} queries)")
    return {"search_results_unbiased": [], "sources": []}


def sources_evaluator(state: AnalysisState) -> dict:
    """Evaluates if sources are sufficient (quantity, convergence, circularity)."""
    print(f"    [SOURCES EVAL] Evaluating sources for claim #{state['claim_id']}")
    return {"sources_sufficient": True}


def web_research_biased(state: AnalysisState) -> dict:
    """Widens search to lower-reliability or biased sources."""
    print(f"    [WEB RESEARCH BIASED] Widening search for claim #{state['claim_id']}")
    return {"search_results_biased": [], "sources": state.get("sources", [])}


def synthesizer(state: AnalysisState) -> dict:
    """Evaluates the solidity of the author's argument for this claim."""
    print(f"    [SYNTHESIZER] Synthesizing analysis for claim #{state['claim_id']}")
    return {"summary": "[placeholder — synthesizer not yet implemented]", "analyzed": True, "needs_level3": False}


def level3_placeholder(state: AnalysisState) -> dict:
    """Placeholder for Level 3 analysis (not yet implemented)."""
    print(f"    [L3] Claim #{state['claim_id']} routed to Level 3 (not yet implemented)")
    return {}


# =================== Conditional edges ========================================

def route_by_verifiability(state: AnalysisState) -> str:
    """Entry routing: dispatches to the right branch based on verifiability."""
    v = state.get("verifiability", "")
    if v == "A":
        return "common_knowledge_teacher"
    elif v in ("B", "C"):
        return "generate_queries"
    elif v == "D":
        return "level3_placeholder"
    else:
        print(f"    [ROUTER] WARNING: unexpected verifiability '{v}' for claim #{state.get('claim_id')}, skipping")
        return "level3_placeholder"


def route_after_eval(state: AnalysisState) -> str:
    """After sources evaluation: sufficient → synthesizer, insufficient → biased search."""
    if state.get("sources_sufficient", False):
        return "synthesizer"
    return "web_research_biased"


# =================== Graph construction =======================================

def _build_graph() -> StateGraph:
    graph = StateGraph(AnalysisState)

    # Add nodes
    graph.add_node("common_knowledge_teacher", common_knowledge_teacher)
    graph.add_node("generate_queries", generate_queries)
    graph.add_node("web_research_unbiased", web_research_unbiased)
    graph.add_node("sources_evaluator", sources_evaluator)
    graph.add_node("web_research_biased", web_research_biased)
    graph.add_node("synthesizer", synthesizer)
    graph.add_node("level3_placeholder", level3_placeholder)

    # Entry: conditional edge from START
    graph.add_conditional_edges(START, route_by_verifiability)

    # A branch
    graph.add_edge("common_knowledge_teacher", END)

    # B/C branch: generate → research → evaluate → conditional
    graph.add_edge("generate_queries", "web_research_unbiased")
    graph.add_edge("web_research_unbiased", "sources_evaluator")
    graph.add_conditional_edges("sources_evaluator", route_after_eval)
    graph.add_edge("web_research_biased", "synthesizer")
    graph.add_edge("synthesizer", END)

    # D branch
    graph.add_edge("level3_placeholder", END)

    return graph


# Compile once at module level
workflow = _build_graph().compile()


# =================== Entry point ==============================================

async def run_analysis(claim: Claim, child_results: list[dict]) -> tuple[AnalyzedClaim, dict]:
    """Runs the analysis workflow for a single claim.
    Takes a Claim + child_results, returns (AnalyzedClaim, metrics)."""

    # Build internal state from the Claim
    state: AnalysisState = {
        "claim_id": claim.id,
        "idea": claim.idea,
        "verifiability": claim.verifiability or "",
        "type": claim.type or "",
        "role": claim.role,
        "supports": claim.supports,
        "child_results": child_results,
        "passes": [],
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
