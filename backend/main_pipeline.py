"""
Main Pipeline — Layer 1.
Orchestrates: Normalizer → (Rhetoric Detector || Decomposer → Orchestrator) → Writer.
"""
import asyncio
import time
from normalizer import NormalizedInput
from models import Claim, PipelineResult
from agents.decomposer import decompose
from agents.rhetoric_detector import detect_rhetorics
from orchestrator import orchestrate
from agents.writer import write_article
from cost import compute_cost


# =================== Main entry point ========================================

async def run_pipeline(normalized: NormalizedInput, preprocessing_duration: float = 0.0, mode: str = "eco", injected_claims: list[Claim] | None = None) -> PipelineResult:
    """Runs the full main pipeline from a NormalizedInput to final article.
    preprocessing_duration: time spent before the pipeline (scraping, transcription, etc.)
    mode: 'eco' (default) or 'performance' (enables the decomposition correction for now).
    injected_claims: if provided, skips Decomposer and Rhetoric Detector."""

    pipeline_t0 = time.perf_counter()
    all_metrics = {}
    if preprocessing_duration > 0:
        all_metrics["preprocessing"] = {"duration": preprocessing_duration}

    # 1. Parallel: rhetoric detection || (decompose → orchestrate)
    async def _decompose_and_analyze():
        if injected_claims is not None:
            claims = injected_claims
            country = "INT"
        else:
            claims, country, decomposer_metrics = await decompose(normalized, correct=(mode == "performance"))
            all_metrics["decomposer"] = decomposer_metrics

        t0 = time.perf_counter()
        analyzed, orchestrator_metrics = await orchestrate(claims, country)
        all_metrics["orchestrator"] = {"duration": time.perf_counter() - t0, "passes": orchestrator_metrics.get("passes", [])}
        return analyzed

    async def _detect_rhetorics():
        if injected_claims is not None:
            return []
        result, rhetoric_metrics = await detect_rhetorics(normalized, correct=(mode == "performance"))
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
    total_input = 0
    total_output = 0
    total_cache_write = 0
    total_cache_read = 0
    for m in all_metrics.values():
        for p in m.get("passes", []):
            total_input += p.get("input_tokens", 0)
            total_output += p.get("output_tokens", 0)
            total_cache_write += p.get("cache_creation_input_tokens", 0)
            total_cache_read += p.get("cache_read_input_tokens", 0)

    print(f"\n{'='*50}")
    print(f"[PIPELINE] '{mode}' mode analysis ended.")
    print(f"[PIPELINE] Total: {total_duration:.2f}s (preprocessing: {preprocessing_duration:.2f}s + pipeline: {pipeline_duration:.2f}s)")
    print(f"[PIPELINE] Timing breakdown:")
    for name, m in all_metrics.items():
        passes = m.get("passes", [])
        if passes:
            p_input = sum(p.get("input_tokens", 0) for p in passes)
            p_output = sum(p.get("output_tokens", 0) for p in passes)
            p_cache_r = sum(p.get("cache_read_input_tokens", 0) for p in passes)
            cache_str = f" | cache read: {p_cache_r}" if p_cache_r else ""
            print(f"  {name}: {m['duration']:.2f}s | {p_input} in + {p_output} out{cache_str}")
        else:
            print(f"  {name}: {m['duration']:.2f}s")
    print(f"[PIPELINE] Total tokens: {total_input} in + {total_output} out")
    if total_cache_read:
        print(f"[PIPELINE] Cache: {total_cache_write} write + {total_cache_read} read")

    # 3b. Cost breakdown
    compute_cost(all_metrics)
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
