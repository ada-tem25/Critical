"""
Rhetoric detector agent — detects manipulative rhetorical devices.
"""
import time
from pydantic import BaseModel
from dotenv import load_dotenv
from langchain_anthropic import ChatAnthropic
from langchain_core.messages import SystemMessage, HumanMessage
from normalizer import NormalizedInput
from models import Rhetoric
from prompts.rhetoric import rhetoric_detector_instructions
from rhetoric_catalog import VALID_RHETORIC_NAMES

load_dotenv()

llm = ChatAnthropic(model="claude-sonnet-4-20250514") # claude-haiku-4-5-20251001 / claude-sonnet-4-20250514


class RhetoricList(BaseModel):
    """Wrapper for structured output (list of Rhetoric)."""
    rhetorics: list[Rhetoric]


async def detect_rhetorics(normalized: NormalizedInput) -> tuple[list[Rhetoric], dict]:
    """LLM agent. Detects manipulative rhetorical devices from a bank of known biases.
    Returns (rhetorics, metrics) where metrics contains timing and token usage."""

    structured_llm = llm.with_structured_output(RhetoricList, include_raw=True)

    t0 = time.perf_counter()
    raw_response = await structured_llm.ainvoke([
        SystemMessage(content=rhetoric_detector_instructions),
        HumanMessage(content=normalized.text),
    ])
    duration = time.perf_counter() - t0

    if raw_response["parsed"] is None:
        print(f"[RHETORIC] Parsing failed: {raw_response.get('parsing_error')}")
        print(f"[RHETORIC] Raw output: {raw_response['raw'].content}")
        raise ValueError(f"Rhetoric detector failed to produce valid output: {raw_response.get('parsing_error')}")

    rhetorics = raw_response["parsed"].rhetorics
    usage = raw_response["raw"].usage_metadata

    # Validate rhetoric names against catalog
    for r in rhetorics:
        if r.type not in VALID_RHETORIC_NAMES:
            print(f"[RHETORIC] WARNING: '{r.type}' is not in the rhetoric catalog")

    print(f"\n{'='*50}")
    print(f"[RHETORIC] {len(rhetorics)} rhetorical devices detected in {duration:.2f}s")
    print(f"[RHETORIC] Tokens: {usage.get('input_tokens', 0)} in / {usage.get('output_tokens', 0)} out")
    for r in rhetorics:
        print(f"  [{r.type}] \"{r.passage[:80]}{'...' if len(r.passage) > 80 else ''}\"")
        print(f"    → {r.explanation}")
    print(f"{'='*50}\n")

    metrics = {
        "duration": duration,
        "input_tokens": usage.get("input_tokens", 0),
        "output_tokens": usage.get("output_tokens", 0),
        "total_tokens": usage.get("total_tokens", 0),
    }

    return rhetorics, metrics
