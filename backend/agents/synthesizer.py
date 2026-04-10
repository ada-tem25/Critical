"""
Synthesizer agent — evaluates the solidity of the author's argument for a claim.
Receives tagged sources from web research + child_results.
"""
import json
import re
import time
from typing import Optional
from dotenv import load_dotenv
from langchain_anthropic import ChatAnthropic
from langchain_core.messages import SystemMessage, HumanMessage
from pydantic import BaseModel, Field
from prompts.synthesizing import synthesizer_l2_instructions

load_dotenv()

SYNTHESIZER_MODEL = "claude-haiku-4-5"

llm = ChatAnthropic(model=SYNTHESIZER_MODEL, temperature=0)


class SynthesizerOutput(BaseModel):
    summary: str = Field(description="Analysis of the solidity of the author's argument for this claim.")
    needs_level3: bool = Field(description="Whether this claim requires deeper critical analysis (level 3).")
    idea: Optional[str] = Field(default=None, description="The claim idea — only included when needs_level3 is true.")
    claim_type: Optional[str] = Field(default=None, description="The claim type — only included when needs_level3 is true.")
    child_results: Optional[list[dict]] = Field(default=None, description="Child results — only included when needs_level3 is true.")


async def synthesize(claim_id: int, idea: str, claim_type: str, child_results: list[dict], sources: list[dict]) -> tuple[dict, dict]:
    """LLM agent. Analyzes the solidity of the author's argument based on sources.
    Returns ({summary, needs_level3, sources, idea?, claim_type?, child_results?}, metrics)."""

    claim_context = {
        "idea": idea,
        "type": claim_type,
        "child_results": child_results,
        "sources": sources,
    }

    # Debug: inspect source sizes
    context_json = json.dumps(claim_context, ensure_ascii=False)
    print(f"    [SYNTHESIZER] #{claim_id} — Sources: {len(sources)} items, total length = {sum(len(s.get('content', '')) for s in sources)} chars (+ claim & child results --> {len(context_json)} chars)")
    for i, s in enumerate(sources):
        print(f"      source[{i}]: {len(s.get('content', ''))} chars — {s.get('content', '')[:200]}")

    structured_llm = llm.with_structured_output(SynthesizerOutput, include_raw=True)

    t0 = time.perf_counter()
    raw_response = await structured_llm.ainvoke([
        SystemMessage(content=synthesizer_l2_instructions),
        HumanMessage(content=context_json),
    ])
    duration = time.perf_counter() - t0

    usage = raw_response["raw"].usage_metadata

    if raw_response["parsed"] is None:
        print(f"    [SYNTHESIZER] #{claim_id} Parsing failed: {raw_response.get('parsing_error')}")
        raw_text = raw_response["raw"].content if isinstance(raw_response["raw"].content, str) else raw_response["raw"].content[0].get("text", "")
        result = {"summary": raw_text, "needs_level3": False, "sources": sources}
    else:
        parsed = raw_response["parsed"]
        print(f"    [SYNTHESIZER] #{claim_id} [{claim_type}] ({duration:.2f}s)")
        print(f"    [SYNTHESIZER] Result: needs_level3={parsed.needs_level3}")
        print(f"    [SYNTHESIZER] Summary:\n{parsed.summary}")

        # Keep only sources actually cited in the summary ([1], [3], etc.)
        cited_ids = {int(m) for m in re.findall(r'\[(\d+)\]', parsed.summary)}
        cited_sources = [s for s in sources if s.get("id") in cited_ids]

        result = {
            "summary": parsed.summary,
            "needs_level3": parsed.needs_level3,
            "sources": cited_sources,
        }
        if parsed.needs_level3:
            result["idea"] = idea
            result["claim_type"] = claim_type
            result["child_results"] = child_results

    print(f"    [SYNTHESIZER] Tokens: {usage.get('input_tokens', 0)} in / {usage.get('output_tokens', 0)} out")

    metrics = {
        "duration": duration,
        "passes": [
            {
                "agent": "synthesizer",
                "model": SYNTHESIZER_MODEL,
                "input_tokens": usage.get("input_tokens", 0),
                "output_tokens": usage.get("output_tokens", 0),
            },
        ],
    }

    return result, metrics
