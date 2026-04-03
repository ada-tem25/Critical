"""
Decomposer agent — extracts a DAG of claims from normalized text.
Two-pass architecture: Sonnet extracts, optional Haiku correction.
"""
import json
import time
from pydantic import BaseModel
from dotenv import load_dotenv
from langchain_anthropic import ChatAnthropic
from langchain_core.messages import SystemMessage, HumanMessage
from normalizer import NormalizedInput
from models import Claim
from prompts.decomposer import decomposer_instructions, decomposer_corrector_instructions

load_dotenv()

DECOMPOSER_MODEL = "claude-sonnet-4-6"
CORRECTOR_MODEL = "claude-haiku-4-5-20251001"

llm = ChatAnthropic(model=DECOMPOSER_MODEL, temperature=0)
llm_haiku = ChatAnthropic(model=CORRECTOR_MODEL, temperature=0)


class ClaimList(BaseModel):
    """Wrapper for structured output (list of Claim)."""
    claims: list[Claim]


async def decompose(normalized: NormalizedInput, correct: bool = False) -> tuple[list[Claim], dict]:
    """LLM agent. Decomposes text into claims (Sonnet), optionally corrects (Haiku).
    Returns (claims, metrics) where metrics contains timing and token usage."""

    # ── Pass 1: Decomposer (Sonnet) ──
    structured_sonnet = llm.with_structured_output(ClaimList, include_raw=True)

    t0 = time.perf_counter()
    raw_response = await structured_sonnet.ainvoke([
        SystemMessage(content=[
            {
                "type": "text",
                "text": decomposer_instructions,
                "cache_control": {"type": "ephemeral"}
            }
        ]),
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
    print(f"[DECOMPOSER] Raw usage_metadata: {dict(usage_1)}")
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
            SystemMessage(content=[{"type": "text", "text": decomposer_corrector_instructions, "cache_control": {"type": "ephemeral"}}]),
            HumanMessage(content=corrector_input),
        ])
        corrector_duration = time.perf_counter() - t1

        if corrector_response["parsed"] is None:
            print(f"[CORRECTOR] Parsing failed: {corrector_response.get('parsing_error')}")
            print(f"[CORRECTOR] Falling back to uncorrected claims")
            final_claims = initial_claims
            usage_2 = corrector_response["raw"].usage_metadata
        else:
            final_claims = corrector_response["parsed"].claims
            usage_2 = corrector_response["raw"].usage_metadata

            print(f"{'='*50}")
            print(f"[CORRECTOR] {len(final_claims)} claims after correction in {corrector_duration:.2f}s")
            print(f"[CORRECTOR] Tokens: {usage_2.get('input_tokens', 0)} in / {usage_2.get('output_tokens', 0)} out")
            for c in final_claims:
                print(f"  #{c.id} [{c.verifiability}] ({c.type}/{c.role}) {c.idea}")
                if c.supports:
                    print(f"       supports: {c.supports}")
            print(f"{'='*50}\n")
    else:
        final_claims = initial_claims
        corrector_duration = 0.0

    # ── Combine metrics ──
    details_1 = usage_1.get("input_token_details", {})
    passes = [
        {
            "model": DECOMPOSER_MODEL,
            "input_tokens": usage_1.get("input_tokens", 0),
            "output_tokens": usage_1.get("output_tokens", 0),
            "cache_creation_input_tokens": details_1.get("ephemeral_5m_input_tokens", 0),
            "cache_read_input_tokens": details_1.get("cache_read", 0),
        },
    ]
    if correct:
        details_2 = usage_2.get("input_token_details", {})
        passes.append({
            "model": CORRECTOR_MODEL,
            "input_tokens": usage_2.get("input_tokens", 0),
            "output_tokens": usage_2.get("output_tokens", 0),
            "cache_creation_input_tokens": details_2.get("ephemeral_5m_input_tokens", 0),
            "cache_read_input_tokens": details_2.get("cache_read", 0),
        })

    metrics = {
        "duration": decomposer_duration + corrector_duration,
        "passes": passes,
    }

    return final_claims, metrics
