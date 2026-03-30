"""
Main Pipeline — Layer 1.
Orchestrates: Normalizer → (Rhetoric Detector || Decomposer → Orchestrator) → Writer.
"""
import asyncio
import time
from normalizer import NormalizedInput
from models import PipelineResult
from agents.decomposer import decompose
from agents.rhetoric_detector import detect_rhetorics
from agents.orchestrator import orchestrate
from agents.writer import write_article


# =================== Main entry point ========================================

async def run_pipeline(normalized: NormalizedInput, preprocessing_duration: float = 0.0, mode: str = "eco") -> PipelineResult:
    """Runs the full main pipeline from a NormalizedInput to final article.
    preprocessing_duration: time spent before the pipeline (scraping, transcription, etc.)
    mode: 'eco' (default) or 'performance' (enables the decomposition correction for now)."""

    pipeline_t0 = time.perf_counter()
    all_metrics = {}
    if preprocessing_duration > 0:
        all_metrics["preprocessing"] = {"duration": preprocessing_duration}

    # 1. Parallel: rhetoric detection || (decompose → orchestrate)
    async def _decompose_and_analyze():
        return []  # TODO: remove — skipping decomposer while testing rhetoric detector
        claims, decomposer_metrics = await decompose(normalized, correct=(mode == "performance"))
        all_metrics["decomposer"] = decomposer_metrics

        t0 = time.perf_counter()
        analyzed = await orchestrate(claims)
        all_metrics["orchestrator"] = {"duration": time.perf_counter() - t0}
        return analyzed

    async def _detect_rhetorics():
        result, rhetoric_metrics = await detect_rhetorics(normalized)
        all_metrics["rhetoric_detector"] = rhetoric_metrics
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

    # 4. Return result --> To be changed later
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
