"""
Orchestrator — deterministic topological sort and claim analysis dispatch.
"""
from models import Claim, AnalyzedClaim


async def orchestrate(claims: list[Claim]) -> list[AnalyzedClaim]:
    """Deterministic. Topological sort → batch A claims → launch analysis workflow per claim → collect results."""
    # TODO: implement (filter out verifiability E claims, call analysis_workflow.analyze_claim per claim)
    return [
        AnalyzedClaim(claim_id=c.id, idea=c.idea, role=c.role, summary="", supports=c.supports, sources=[])
        for c in claims
    ]
