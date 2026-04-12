"""
Rhetoric detector agent — detects manipulative rhetorical devices.
Two-pass architecture: Sonnet detects, optional Haiku review.
"""
import json
import time
from pydantic import BaseModel
from dotenv import load_dotenv
from langchain_anthropic import ChatAnthropic
from langchain_core.messages import SystemMessage, HumanMessage
from normalizer import NormalizedInput
from models import Rhetoric
from prompts.rhetoric import rhetoric_detector_instructions, rhetoric_reviewer_instructions
from rhetoric_catalog import VALID_RHETORIC_NAMES

load_dotenv()

DETECTOR_MODEL = "claude-sonnet-4-6"
REVIEWER_MODEL = "claude-sonnet-4-6"

llm = ChatAnthropic(model=DETECTOR_MODEL, temperature=0)
llm_2 = ChatAnthropic(model=REVIEWER_MODEL, temperature=0)


class RhetoricList(BaseModel):
    """Wrapper for structured output (list of Rhetoric)."""
    rhetorics: list[Rhetoric]


async def detect_rhetorics(normalized: NormalizedInput, correct: bool = False) -> tuple[list[Rhetoric], dict]:
    """LLM agent. Detects manipulative rhetorical devices (Sonnet), optionally reviews (Haiku).
    Returns (rhetorics, metrics) where metrics contains timing and token usage."""

    # ── Pass 1: Detector (Sonnet) ──
    structured_llm = llm.with_structured_output(RhetoricList, include_raw=True)

    t0 = time.perf_counter()
    raw_response = await structured_llm.ainvoke([
        SystemMessage(content=[{"type": "text", "text": rhetoric_detector_instructions, "cache_control": {"type": "ephemeral"}}]),
        HumanMessage(content=normalized.text),
    ])
    detector_duration = time.perf_counter() - t0

    if raw_response["parsed"] is None:
        print(f"[RHETORIC] Parsing failed: {raw_response.get('parsing_error')}")
        print(f"[RHETORIC] Raw output: {raw_response['raw'].content}")
        raise ValueError(f"Rhetoric detector failed to produce valid output: {raw_response.get('parsing_error')}")

    initial_rhetorics = raw_response["parsed"].rhetorics
    usage_1 = raw_response["raw"].usage_metadata

    print(f"\n{'='*50}")
    print(f"[RHETORIC] {len(initial_rhetorics)} rhetorical devices detected in {detector_duration:.2f}s")
    print(f"[RHETORIC] Tokens: {usage_1.get('input_tokens', 0)} in / {usage_1.get('output_tokens', 0)} out")
    for r in initial_rhetorics:
        print(f"  [{r.type}] \"{r.passage[:80]}{'...' if len(r.passage) > 80 else ''}\"")
        print(f"    → {r.explanation}")
    print(f"{'='*50}\n")

    # ── Pass 2: Reviewer (Haiku) — optional ──
    if correct:
        rhetorics_json = json.dumps([r.model_dump() for r in initial_rhetorics], ensure_ascii=False, indent=2)
        reviewer_input = f"ORIGINAL TEXT:\n{normalized.text}\n\nDETECTED RHETORICS:\n{rhetorics_json}"

        structured_llm_2 = llm_2.with_structured_output(RhetoricList, include_raw=True)

        t1 = time.perf_counter()
        reviewer_response = await structured_llm_2.ainvoke([
            SystemMessage(content=[{"type": "text", "text": rhetoric_reviewer_instructions, "cache_control": {"type": "ephemeral"}}]),
            HumanMessage(content=reviewer_input),
        ])
        reviewer_duration = time.perf_counter() - t1

        if reviewer_response["parsed"] is None:
            print(f"[RHETORIC REVIEWER] Parsing failed: {reviewer_response.get('parsing_error')}")
            print(f"[RHETORIC REVIEWER] Raw output: {reviewer_response['raw'].content}")
            print(f"[RHETORIC REVIEWER] Falling back to unreviewed rhetorics")
            final_rhetorics = initial_rhetorics
            usage_2 = reviewer_response["raw"].usage_metadata
        else:
            final_rhetorics = reviewer_response["parsed"].rhetorics
            usage_2 = reviewer_response["raw"].usage_metadata

            removed = len(initial_rhetorics) - len(final_rhetorics)
            print(f"{'='*50}")
            print(f"[RHETORIC REVIEWER] {len(final_rhetorics)} rhetorics after review in {reviewer_duration:.2f}s (removed {removed})")
            print(f"[RHETORIC REVIEWER] Tokens: {usage_2.get('input_tokens', 0)} in / {usage_2.get('output_tokens', 0)} out")
            for r in final_rhetorics:
                print(f"  [{r.type}] \"{r.passage[:80]}{'...' if len(r.passage) > 80 else ''}\"")
                print(f"    → {r.explanation}")
            print(f"{'='*50}\n")
    else:
        final_rhetorics = initial_rhetorics
        reviewer_duration = 0.0

    # Validate rhetoric names against catalog
    for r in final_rhetorics:
        if r.type not in VALID_RHETORIC_NAMES:
            print(f"[RHETORIC] WARNING: '{r.type}' is not in the rhetoric catalog")

    # ── Combine metrics ──
    details_1 = usage_1.get("input_token_details", {})
    passes = [
        {
            "model": DETECTOR_MODEL,
            "input_tokens": usage_1.get("input_tokens", 0),
            "output_tokens": usage_1.get("output_tokens", 0),
            "cache_creation_input_tokens": details_1.get("ephemeral_5m_input_tokens", 0),
            "cache_read_input_tokens": details_1.get("cache_read", 0),
        },
    ]
    if correct:
        details_2 = usage_2.get("input_token_details", {})
        passes.append({
            "model": REVIEWER_MODEL,
            "input_tokens": usage_2.get("input_tokens", 0),
            "output_tokens": usage_2.get("output_tokens", 0),
            "cache_creation_input_tokens": details_2.get("ephemeral_5m_input_tokens", 0),
            "cache_read_input_tokens": details_2.get("cache_read", 0),
        })

    metrics = {
        "duration": detector_duration + reviewer_duration,
        "passes": passes,
    }

    return final_rhetorics, metrics
