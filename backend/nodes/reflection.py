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
from llm_retry import llm_call_with_retry
from prompts.reflection import reflection_agent_instructions

load_dotenv()

REFLECTION_MODEL = "claude-haiku-4-5"

llm = ChatAnthropic(model=REFLECTION_MODEL, temperature=0)


class ReflectionOutput(BaseModel):
    sufficient: bool = Field(description="Whether there is enough factual material to produce a solid synthesis.")
    follow_up_queries: list[str] = Field(default_factory=list, description="1-2 refined search queries to fill the gap (only if sufficient=false).")


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
                "content": p.get("content", "")[:4000],  # Cap per passage for token budget
            }
            for p in passages if p.get("content")
        ],
        "loop_count": loop_count,
    }

    context_json = json.dumps(context, ensure_ascii=False)
    print(f"    \033[34m[REFLECTION]\033[0m loop={loop_count}, {len(passages)} passages, {len(context_json)} chars")

    structured_llm = llm.with_structured_output(ReflectionOutput, include_raw=True)

    t0 = time.perf_counter()
    raw_response = await llm_call_with_retry(
        lambda: structured_llm.ainvoke([
            SystemMessage(content=reflection_agent_instructions),
            HumanMessage(content=context_json),
        ]),
        agent_name="REFLECTION",
    )
    duration = time.perf_counter() - t0

    usage = raw_response["raw"].usage_metadata

    if raw_response["parsed"] is None:
        print(f"    \033[34m[REFLECTION]\033[0m \033[31mParsing failed — defaulting to sufficient=True\033[0m")
        result = {"sufficient": True, "gap": None, "follow_up_queries": []}
    else:
        parsed = raw_response["parsed"]
        result = {
            "sufficient": parsed.sufficient,
            "follow_up_queries": parsed.follow_up_queries[:2],  # Cap at 2
        }
        if parsed.sufficient:
            print(f"    \033[34m[REFLECTION]\033[0m \033[32mSufficient — proceeding to synthesizer\033[0m")
        else:
            print(f"    \033[34m[REFLECTION]\033[0m \033[33mInsufficient\033[0m")
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
