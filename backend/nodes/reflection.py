"""
Reflection agent — evaluates whether extracted passages provide enough material
to verify a claim. If not, produces refined follow-up queries.
LLM agent (Haiku 4.5).
"""
import json
import time
from typing import Optional
from dotenv import load_dotenv
from langchain_anthropic import ChatAnthropic
from langchain_core.messages import SystemMessage, HumanMessage
from pydantic import BaseModel, Field

load_dotenv()

REFLECTION_MODEL = "claude-haiku-4-5"

llm = ChatAnthropic(model=REFLECTION_MODEL, temperature=0)


class ReflectionOutput(BaseModel):
    sufficient: bool = Field(description="Whether there is enough factual material to produce a solid synthesis.")
    gap: Optional[str] = Field(default=None, description="What specific information is missing (only if sufficient=false).")
    follow_up_queries: list[str] = Field(default_factory=list, description="1-2 refined search queries to fill the gap (only if sufficient=false).")


REFLECTION_PROMPT = """You evaluate whether web research results contain enough factual material to verify a claim.

## Input

You receive:
- `idea`: the claim to verify.
- `type`: the claim type (factual, statistical, quote, event, causal, comparative, predictive).
- `child_results`: analyses of sub-claims supporting this one (may be empty).
- `passages`: extracted web passages with source metadata (reliability, category, bias).
- `loop_count`: how many research iterations have already been done.

## Instructions

1. **Assess coverage.** Do the passages contain enough factual information to evaluate whether the author's claim holds up? Look for:
   - Direct evidence confirming or refuting the claim
   - Relevant data, quotes, or facts from reliable sources
   - At least 1-2 substantive passages (not just tangentially related content)

2. **Be pragmatic.** You don't need perfect coverage. If there's enough to write a meaningful 1-2 sentence synthesis, mark as sufficient.

3. **If loop_count >= 1, be more lenient.** We've already tried refined queries. If there's any relevant material at all, mark as sufficient — the synthesizer can work with partial evidence.

4. **If insufficient**, explain concisely what's missing and produce 1-2 targeted follow-up queries (3-8 words each, named entities preferred).

## Output

Return a JSON object with:
- `sufficient`: boolean — is there enough material for synthesis?
- `gap`: string (only if insufficient) — what specific information is missing.
- `follow_up_queries`: list of 1-2 query strings (only if insufficient).
"""


async def reflect(claim_idea: str, claim_type: str, child_results: list[dict], passages: list[dict], loop_count: int) -> tuple[dict, dict]:
    """Evaluates if passages are sufficient for synthesis.
    Returns (reflection_result, metrics)."""

    context = {
        "idea": claim_idea,
        "type": claim_type,
        "child_results": child_results,
        "passages": [
            {
                "url": p.get("url", ""),
                "title": p.get("title", ""),
                "reliability": p.get("reliability", "unknown"),
                "content": p.get("content", "")[:2500],  # Cap per passage for token budget
            }
            for p in passages if p.get("content")
        ],
        "loop_count": loop_count,
    }

    context_json = json.dumps(context, ensure_ascii=False)
    print(f"    \033[34m[REFLECTION]\033[0m loop={loop_count}, {len(passages)} passages, {len(context_json)} chars")

    structured_llm = llm.with_structured_output(ReflectionOutput, include_raw=True)

    t0 = time.perf_counter()
    raw_response = await structured_llm.ainvoke([
        SystemMessage(content=REFLECTION_PROMPT),
        HumanMessage(content=context_json),
    ])
    duration = time.perf_counter() - t0

    usage = raw_response["raw"].usage_metadata

    if raw_response["parsed"] is None:
        print(f"    \033[34m[REFLECTION]\033[0m \033[31mParsing failed — defaulting to sufficient=True\033[0m")
        result = {"sufficient": True, "gap": None, "follow_up_queries": []}
    else:
        parsed = raw_response["parsed"]
        result = {
            "sufficient": parsed.sufficient,
            "gap": parsed.gap,
            "follow_up_queries": parsed.follow_up_queries[:2],  # Cap at 2
        }
        if parsed.sufficient:
            print(f"    \033[34m[REFLECTION]\033[0m \033[32mSufficient — proceeding to synthesizer\033[0m")
        else:
            print(f"    \033[34m[REFLECTION]\033[0m \033[33mInsufficient — gap: {parsed.gap}\033[0m")
            print(f"    \033[34m[REFLECTION]\033[0m Follow-up queries: {parsed.follow_up_queries}")

    metrics = {
        "duration": duration,
        "passes": [
            {
                "agent": "reflection",
                "model": REFLECTION_MODEL,
                "input_tokens": usage.get("input_tokens", 0),
                "output_tokens": usage.get("output_tokens", 0),
            },
        ],
    }

    return result, metrics
