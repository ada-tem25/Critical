"""
Main Pipeline — Layer 1.
Orchestrates: Normalizer → (Rhetoric Detector || Decomposer → Orchestrator) → Writer.
"""
import asyncio
from typing import Optional
from pydantic import BaseModel
from normalizer import NormalizedInput


# ── Models ──────────────────────────────────────────────────

class Rhetoric(BaseModel):
    type: str
    passage: str
    explanation: str


class Source(BaseModel):
    url: str
    title: str
    date: str
    anchor: str
    bias: str


class Claim(BaseModel):
    id: int
    idea: str
    verifiability: str  # A | B | C | D | E
    type: str
    role: str           # thesis | supporting | counterargument
    supports: list[int]


class AnalyzedClaim(BaseModel):
    claim_id: int
    idea: str
    role: str
    summary: str
    supports: list[int]
    sources: list[Source]
    analysis: Optional[str] = None


class PipelineResult(BaseModel):
    text: str
    source_type: str
    source_url: str
    author: str
    date: str
    rhetorics: list[Rhetoric]
    analyzed_claims: list[AnalyzedClaim]
    article: str


# ── Component skeletons ─────────────────────────────────────

async def detect_rhetorics(normalized: NormalizedInput) -> list[Rhetoric]:
    """LLM agent. Detects manipulative rhetorical devices from a bank of ~20 known biases."""
    
    # TODO: implement
    return []


async def decompose(normalized: NormalizedInput) -> list[Claim]:
    """LLM agent. Reads the full text and decomposes it into a DAG of claims."""
    
    # TODO: implement
    return [Claim(id=1, idea="[Placeholder claim]", verifiability="B", type="factual", role="thesis", supports=[])]


async def orchestrate(claims: list[Claim]) -> list[AnalyzedClaim]:
    """Deterministic. Topological sort → batch A claims → launch analysis workflow per claim → collect results."""
    # TODO: implement (filter out verifiability E claims, call analysis_workflow.analyze_claim per claim)
    return [
        AnalyzedClaim(claim_id=c.id, idea=c.idea, role=c.role, summary="", supports=c.supports, sources=[])
        for c in claims
    ]


async def write_article(normalized: NormalizedInput, analyzed_claims: list[AnalyzedClaim], rhetorics: list[Rhetoric]) -> str:
    """LLM agent. Produces the final journalistic fact-check article."""
    # TODO: implement
    return "[Article placeholder]"


# =================== Main entry point ========================================

async def run_pipeline(normalized: NormalizedInput) -> PipelineResult:
    """Runs the full main pipeline from a NormalizedInput to final article."""

    # 1. Parallel: rhetoric detection || (decompose → orchestrate)
    async def _decompose_and_analyze():
        claims = await decompose(normalized)
        return await orchestrate(claims)

    rhetorics, analyzed_claims = await asyncio.gather(
        detect_rhetorics(normalized),
        _decompose_and_analyze(),
    )

    # 3. Write final article
    article = await write_article(normalized, analyzed_claims, rhetorics)

    # 4. Return result
    return PipelineResult(
        text=normalized.text,
        source_type=normalized.source_type,
        source_url=normalized.source_url,
        author=normalized.author,
        date=normalized.date,
        rhetorics=rhetorics,
        analyzed_claims=analyzed_claims,
        article=article,
    )
