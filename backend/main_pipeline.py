"""
Main Pipeline — Layer 1.
Orchestrates: Normalizer → (Rhetoric Detector || Decomposer → Orchestrator) → Writer.
"""
import asyncio
import json
import time
from pathlib import Path
from normalizer import NormalizedInput
from models import Claim, PipelineResult
from nodes.decomposer import decompose
from nodes.rhetoric_detector import detect_rhetorics
from orchestrator import orchestrate
from nodes.writer import write_article
from cost import compute_cost
from utils import format_duration


# =================== Main entry point ========================================

async def run_pipeline(normalized: NormalizedInput, preprocessing_duration: float = 0.0, mode: str = "eco", target_language: str = "French", injected_claims: list[Claim] | None = None) -> PipelineResult:
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
            country = "FR"
        else:
            claims, country, decomposer_metrics = await decompose(normalized, correct=True)
            all_metrics["decomposer"] = decomposer_metrics

        t0 = time.perf_counter()
        analyzed, orchestrator_metrics = await orchestrate(claims, country, mode=mode, target_language=target_language)
        all_metrics["orchestrator"] = {"duration": time.perf_counter() - t0, "passes": orchestrator_metrics.get("passes", [])}
        return analyzed

    async def _detect_rhetorics():
        if injected_claims is not None:
            return []
        result, rhetoric_metrics = await detect_rhetorics(normalized, correct=True)
        all_metrics["rhetoric_detector"] = rhetoric_metrics
        return result

    rhetorics, analyzed_claims = await asyncio.gather(
        _detect_rhetorics(),
        _decompose_and_analyze(),
    )

    # 2. Write final article
    t0 = time.perf_counter()
    writer_result, writer_metrics = await write_article(normalized, analyzed_claims, rhetorics, target_language=target_language)
    all_metrics["writer"] = {"duration": time.perf_counter() - t0, "passes": writer_metrics.get("passes", [])}

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

    print(f"\n\033[1m{'='*50}\033[0m")
    print(f"\033[1m[PIPELINE]\033[0m '{mode}' mode analysis ended.")
    print(f"\033[1m[PIPELINE]\033[0m Total: \033[1m{format_duration(total_duration)}\033[0m (preprocessing: {format_duration(preprocessing_duration)} + pipeline: {format_duration(pipeline_duration)})")
    print(f"\033[1m[PIPELINE]\033[0m Timing breakdown:")
    for name, m in all_metrics.items():
        passes = m.get("passes", [])
        if passes:
            p_input = sum(p.get("input_tokens", 0) for p in passes)
            p_output = sum(p.get("output_tokens", 0) for p in passes)
            p_cache_r = sum(p.get("cache_read_input_tokens", 0) for p in passes)
            cache_str = f" \033[2m| cache read: {p_cache_r}\033[0m" if p_cache_r else ""
            print(f"  {name}: {format_duration(m['duration'])} | {p_input} in + {p_output} out{cache_str}")
        else:
            print(f"  \033[2m{name}: {format_duration(m['duration'])}\033[0m")
    print(f"\033[1m[PIPELINE]\033[0m Total tokens: {total_input} in + {total_output} out")
    if total_cache_read:
        print(f"\033[1m[PIPELINE]\033[0m \033[2mCache: {total_cache_write} write + {total_cache_read} read\033[0m")

    # 3b. Cost breakdown
    compute_cost(all_metrics)
    print(f"\033[1m{'='*50}\033[0m\n")

    # 3c. Print Writer output for evaluation
    print(f"\033[1;36m{'─'*50}\033[0m")
    print(f"\033[1;36m  ARTICLE OUTPUT\033[0m")
    print(f"\033[1;36m{'─'*50}\033[0m")
    print(f"\033[1m  Title:\033[0m    {writer_result['title']}")
    if writer_result.get("subtitle"):
        print(f"\033[1m  Subtitle:\033[0m {writer_result['subtitle']}")
    print(f"\033[1m  Verdict:\033[0m  \033[1;33m{writer_result['verdict']}\033[0m")
    print(f"\033[1m  Format:\033[0m   {writer_result['format']} ({len(writer_result['article'])} chars)")
    print(f"\033[1m  Summary:\033[0m  {writer_result['summary']}")
    if writer_result.get("quote"):
        q = writer_result["quote"]
        print(f'\033[1m  Quote:\033[0m    \033[3m"{q["text"]}"\033[0m — {q["author"]}, {q["date"]}')
    print(f"\033[1;36m{'─'*50}\033[0m")
    print(f"\033[1m  Sources ({len(writer_result['sources'])}):\033[0m")
    for s in writer_result["sources"]:
        print(f"    [{s['id']}] {s['title']}")
        print(f"        \033[2m{s['url']}\033[0m")
    print(f"\033[1;36m{'─'*50}\033[0m")
    print(f"\033[1m  Article:\033[0m")
    print()
    print(writer_result["article"])
    print()
    print(f"\033[1;36m{'─'*50}\033[0m\n")

    # 4. Build result & auto-save to outputs/
    result = PipelineResult(
        source_type=normalized.source_type,
        source_url=normalized.source_url,
        author=normalized.author,
        date=normalized.date,
        title=writer_result["title"],
        subtitle=writer_result.get("subtitle"),
        verdict=writer_result["verdict"],
        summary=writer_result["summary"],
        article=writer_result["article"],
        format=writer_result["format"],
        language=target_language,
        sources=writer_result["sources"],
        quote=writer_result.get("quote"),
    )

    # [DEMO ONLY] Copy result to the frontend's analyzed/ directory so it appears on the demo page.
    # In the real app, results will be served via the API — this won't be needed.
    frontend_analyzed_dir = Path(__file__).parent.parent / "frontend_critical_lovable" / "src" / "data" / "analyzed"
    if frontend_analyzed_dir.exists():
        demo_path = frontend_analyzed_dir / f"{result.id}.json"
        demo_path.write_text(json.dumps(result.model_dump(), ensure_ascii=False, indent=2), encoding="utf-8")
        print(f"\033[1m[PIPELINE]\033[0m \033[2m[DEMO] Output saved to the demo frontend: \033[4m{demo_path}\033[0m")

    return result
