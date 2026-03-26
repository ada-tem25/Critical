"""
Analysis Workflow — Layer 2 (LangGraph).
Called once per claim by the Orchestrator.
"""
from typing_extensions import TypedDict


class AnalysisState(TypedDict, total=False):
    # Input fields (set at invocation by the Orchestrator)
    claim_id: int
    idea: str
    verifiability: str          # "A", "B", "C", "D"
    claim_type: str             # "factual", "statistical", "quote", "event", "causal", "comparative", "predictive", "opinion"
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
    sources: list[dict]
