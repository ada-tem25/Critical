"""
Main Pipeline — Layer 1.
Orchestrates: Normalizer → (Rhetoric Detector || Decomposer → Orchestrator) → Writer.
"""
import asyncio
import time
from typing import Optional
from dotenv import load_dotenv
from pydantic import BaseModel
from langchain_anthropic import ChatAnthropic
from langchain_core.messages import SystemMessage, HumanMessage
from normalizer import NormalizedInput
from prompts import decomposer_instructions, decomposer_corrector_instructions

load_dotenv()

llm = ChatAnthropic(model="claude-sonnet-4-20250514")
llm_haiku = ChatAnthropic(model="claude-haiku-4-5-20251001")


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
    verifiability: Optional[str] = None  # A | B | C | D | E
    type: Optional[str] = None
    role: str           # thesis | supporting | counterargument
    supports: list[int]


class RecommendedReading(BaseModel):
    title: str
    author: str
    year: int


class AnalyzedClaim(BaseModel):
    claim_id: int
    idea: str
    role: str
    summary: str
    analyzed: bool = False
    supports: list[int]
    sources: list[Source]
    analysis: Optional[str] = None
    recommended_reading: list[RecommendedReading] = []


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


class ClaimList(BaseModel):
    """Wrapper for structured output (list of Claim)."""
    claims: list[Claim]


async def decompose(normalized: NormalizedInput, correct: bool = False) -> tuple[list[Claim], dict]:
    """LLM agent. Decomposes text into claims (Sonnet), optionally corrects (Haiku).
    Returns (claims, metrics) where metrics contains timing and token usage."""

    import json

    # ── Pass 1: Decomposer (Sonnet) ──
    structured_sonnet = llm.with_structured_output(ClaimList, include_raw=True)

    t0 = time.perf_counter()
    raw_response = await structured_sonnet.ainvoke([
        SystemMessage(content=decomposer_instructions),
        HumanMessage(content=normalized.text),
    ])
    decomposer_duration = time.perf_counter() - t0

    if raw_response["parsed"] is None:
        print(f"[DECOMPOSER] Parsing failed: {raw_response.get('parsing_error')}")
        print(f"[DECOMPOSER] Raw output: {raw_response['raw'].content}")
        raise ValueError(f"Decomposer failed to produce valid output: {raw_response.get('parsing_error')}")

    initial_claims = raw_response["parsed"].claims
    usage_1 = raw_response["raw"].usage_metadata

    print(f"\n{'='*50}")
    print(f"[DECOMPOSER] {len(initial_claims)} claims extracted in {decomposer_duration:.2f}s")
    print(f"[DECOMPOSER] Tokens: {usage_1.get('input_tokens', 0)} in / {usage_1.get('output_tokens', 0)} out")
    for c in initial_claims:
        print(f"  #{c.id} [{c.verifiability}] ({c.type}/{c.role}) {c.idea}")
        if c.supports:
            print(f"       supports: {c.supports}")
    print(f"{'='*50}\n")

    # ── Pass 2: Corrector (Haiku) — optional ──
    if correct:
        claims_json = json.dumps([c.model_dump() for c in initial_claims], ensure_ascii=False, indent=2)
        corrector_input = f"ORIGINAL TEXT:\n{normalized.text}\n\nCLAIMS:\n{claims_json}"

        structured_haiku = llm_haiku.with_structured_output(ClaimList, include_raw=True)

        t1 = time.perf_counter()
        corrector_response = await structured_haiku.ainvoke([
            SystemMessage(content=decomposer_corrector_instructions),
            HumanMessage(content=corrector_input),
        ])
        corrector_duration = time.perf_counter() - t1

        if corrector_response["parsed"] is None:
            print(f"[CORRECTOR] Parsing failed: {corrector_response.get('parsing_error')}")
            print(f"[CORRECTOR] Raw output: {corrector_response['raw'].content}")
            print(f"[CORRECTOR] Falling back to uncorrected claims")
            final_claims = initial_claims
            usage_2 = corrector_response["raw"].usage_metadata
        else:
            final_claims = corrector_response["parsed"].claims
            usage_2 = corrector_response["raw"].usage_metadata

            removed = len(initial_claims) - len(final_claims)
            print(f"{'='*50}")
            print(f"[CORRECTOR] {len(final_claims)} claims after correction in {corrector_duration:.2f}s ({removed:+d} claims)")
            print(f"[CORRECTOR] Tokens: {usage_2.get('input_tokens', 0)} in / {usage_2.get('output_tokens', 0)} out")
            for c in final_claims:
                print(f"  #{c.id} [{c.verifiability}] ({c.type}/{c.role}) {c.idea}")
                if c.supports:
                    print(f"       supports: {c.supports}")
            print(f"{'='*50}\n")
    else:
        final_claims = initial_claims
        corrector_duration = 0.0
        usage_2 = {"input_tokens": 0, "output_tokens": 0, "total_tokens": 0}

    # ── Combine metrics ──
    metrics = {
        "duration": decomposer_duration + corrector_duration,
        "input_tokens": usage_1.get("input_tokens", 0) + usage_2.get("input_tokens", 0),
        "output_tokens": usage_1.get("output_tokens", 0) + usage_2.get("output_tokens", 0),
        "total_tokens": usage_1.get("total_tokens", 0) + usage_2.get("total_tokens", 0),
    }

    return final_claims, metrics


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

async def run_pipeline(normalized: NormalizedInput, preprocessing_duration: float = 0.0, correct_decomposition: bool = False) -> PipelineResult:
    """Runs the full main pipeline from a NormalizedInput to final article.
    preprocessing_duration: time spent before the pipeline (scraping, transcription, etc.)
    correct_decomposition: if True, runs a second LLM pass to clean up the claim DAG."""

    pipeline_t0 = time.perf_counter()
    all_metrics = {}
    if preprocessing_duration > 0:
        all_metrics["preprocessing"] = {"duration": preprocessing_duration}

    # 1. Parallel: rhetoric detection || (decompose → orchestrate)
    async def _decompose_and_analyze():
        claims, decomposer_metrics = await decompose(normalized, correct=correct_decomposition)
        all_metrics["decomposer"] = decomposer_metrics

        t0 = time.perf_counter()
        analyzed = await orchestrate(claims)
        all_metrics["orchestrator"] = {"duration": time.perf_counter() - t0}
        return analyzed

    async def _detect_rhetorics():
        t0 = time.perf_counter()
        result = await detect_rhetorics(normalized)
        all_metrics["rhetoric_detector"] = {"duration": time.perf_counter() - t0}
        return result

    rhetorics, analyzed_claims = await asyncio.gather(
        _detect_rhetorics(),
        _decompose_and_analyze(),
    )

    # 2. Write final article
    t0 = time.perf_counter()
    article = await write_article(normalized, analyzed_claims, rhetorics)
    all_metrics["writer"] = {"duration": time.perf_counter() - t0}

    pipeline_duration = time.perf_counter() - pipeline_t0
    total_duration = pipeline_duration + preprocessing_duration

    # 3. Print pipeline summary
    total_input = sum(m.get("input_tokens", 0) for m in all_metrics.values())
    total_output = sum(m.get("output_tokens", 0) for m in all_metrics.values())
    total_tokens = sum(m.get("total_tokens", 0) for m in all_metrics.values())

    print(f"\n{'='*50}")
    print(f"[PIPELINE] Total: {total_duration:.2f}s (preprocessing: {preprocessing_duration:.2f}s + pipeline: {pipeline_duration:.2f}s)")
    print(f"[PIPELINE] Timing breakdown:")
    for name, m in all_metrics.items():
        tokens_str = ""
        if m.get("total_tokens"):
            tokens_str = f" | {m['input_tokens']} in + {m['output_tokens']} out = {m['total_tokens']} tokens"
        print(f"  {name}: {m['duration']:.2f}s{tokens_str}")
    print(f"[PIPELINE] Total tokens: {total_input} in + {total_output} out = {total_tokens}")
    print(f"{'='*50}\n")

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
