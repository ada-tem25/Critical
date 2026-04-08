"""
Synthesizer agent — evaluates the solidity of the author's argument for a claim.
Receives tagged sources from web research + child_results.
"""
import json
import time
from dotenv import load_dotenv
from langchain_anthropic import ChatAnthropic
from langchain_core.messages import SystemMessage, HumanMessage
from prompts.synthesizing import synthesizer_l2_instructions

load_dotenv()

SYNTHESIZER_MODEL = "claude-sonnet-4-6"

llm = ChatAnthropic(model=SYNTHESIZER_MODEL, temperature=0)


async def synthesize(claim_id: int, idea: str, claim_type: str, child_results: list[dict], sources: list[dict]) -> tuple[dict, dict]:
    """LLM agent. Analyzes the solidity of the author's argument based on sources.
    Returns ({summary, needs_level3, sources}, metrics)."""

    claim_context = {
        "idea": idea,
        "type": claim_type,
        "child_results": child_results,
        "sources": sources,
    }

    t0 = time.perf_counter()
    response = await llm.ainvoke([
        SystemMessage(content=[{"type": "text", "text": synthesizer_l2_instructions, "cache_control": {"type": "ephemeral"}}]),
        HumanMessage(content=json.dumps(claim_context, ensure_ascii=False)),
    ])
    duration = time.perf_counter() - t0

    usage = response.usage_metadata
    details = usage.get("input_token_details", {})

    raw_text = response.content if isinstance(response.content, str) else response.content[0].get("text", "")

    print(f"\n{'-'*50}")
    print(f"    [SYNTHESIZER] #{claim_id} [{claim_type}] ({duration:.2f}s)")
    print(f"    [SYNTHESIZER] Result:\n{raw_text[:500]}{'...' if len(raw_text) > 500 else ''}")
    print(f"    [SYNTHESIZER] Tokens: {usage}")

    # TODO: parse response.content into structured output (summary, needs_level3, sources)
    # For now, return placeholder structure
    result = {
        "summary": raw_text,
        "needs_level3": False,
        "sources": sources,
    }

    metrics = {
        "duration": duration,
        "passes": [
            {
                "agent": "synthesizer",
                "model": SYNTHESIZER_MODEL,
                "input_tokens": usage.get("input_tokens", 0),
                "output_tokens": usage.get("output_tokens", 0),
                "cache_creation_input_tokens": details.get("ephemeral_5m_input_tokens", 0),
                "cache_read_input_tokens": details.get("cache_read", 0),
            },
        ],
    }

    return result, metrics
