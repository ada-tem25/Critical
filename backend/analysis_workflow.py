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
from agents.web_research import search_and_tag
from agents.synthesizer import synthesize
from utils import get_categories_for_type


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

    # L2 intermediate fields
    queries_l2: list[str]
    search_results: list[dict]  # Tagged sources from Tavily + domain tagger
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

async def generate_queries(state: AnalysisState) -> dict:
    """Generates 1-3 search queries to verify the claim."""
    queries, metrics = await generate_queries_l2(
        claim_id=state["claim_id"],
        idea=state["idea"],
        claim_type=state.get("type", ""),
        child_results=state.get("child_results", []),
    )
    return {"queries_l2": queries, "passes": state.get("passes", []) + metrics.get("passes", [])}


async def web_research(state: AnalysisState) -> dict:
    """Executes Tavily search and tags results by domain tier."""
    
    filtered_categories = get_categories_for_type(state.get("type", ""))
    
    
    tagged_sources, metrics = await search_and_tag(
        claim_id=state["claim_id"],
        reliabilities=["reference", "established"], #TODO --> Faire une seconde passe avec oriented en mode performance? Voir en fonction de la qualité des résultats
        categories=filtered_categories,
        regions=["FR", "INT"], #TODO --> Faire que ça dépend de l'utilisateur + du claim ? 
        queries=state.get("queries_l2", []),
    )
    return {"search_results": tagged_sources}


async def synthesizer_node(state: AnalysisState) -> dict:
    """Evaluates the solidity of the author's argument for this claim."""
    result, metrics = await synthesize(
        claim_id=state["claim_id"],
        idea=state["idea"],
        claim_type=state.get("type", ""),
        child_results=state.get("child_results", []),
        sources=state.get("search_results", []),
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


# =================== Graph construction =======================================

def _build_graph() -> StateGraph:
    graph = StateGraph(AnalysisState)

    # All nodes
    graph.add_node("generate_queries", generate_queries)
    graph.add_node("web_research", web_research)
    graph.add_node("synthesizer", synthesizer_node)
    graph.add_node("level3_placeholder", level3_placeholder)


    # Entry: conditional edge from START
    graph.add_conditional_edges(START, route_by_verifiability)

    # Fact-checking Loop: generate queries → web_search → synthesize
    graph.add_edge("generate_queries", "web_research")
    graph.add_edge("web_research", "synthesizer")
    graph.add_edge("synthesizer", END)

    # D branch #TODO
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
