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
from prompts.synthesizing import synthesizer_l2_instructions, synthesizer_l3_instructions, synthesizer_l4_instructions
from llm_retry import llm_call_with_retry

load_dotenv()

SYNTHESIZER_MODEL = "claude-haiku-4-5"

llm = ChatAnthropic(model=SYNTHESIZER_MODEL, temperature=0)

_INSTRUCTIONS = {
    "l2": synthesizer_l2_instructions,
    "l3": synthesizer_l3_instructions,
    "l4": synthesizer_l4_instructions,
}


class SynthesizerOutput(BaseModel):
    summary: str = Field(description="Analysis of the claim.")
    needs_next_level: bool = Field(description="Whether this claim requires deeper analysis at the next level.")
    idea: Optional[str] = Field(default=None, description="The claim idea — only included when needs_next_level is true.")
    claim_type: Optional[str] = Field(default=None, description="The claim type — only included when needs_next_level is true.")
    child_results: Optional[list[dict]] = Field(default=None, description="Child results — only included when needs_next_level is true.")
    recommended_reading: Optional[list[dict]] = Field(default=None, description="Academic/intellectual references — only for L4.")
    quote: Optional[dict] = Field(default=None, description="A striking quote found in sources — only for L3. Keys: text, author, source_id.")


async def synthesize(claim_id: int, idea: str, claim_type: str, child_results: list[dict], sources: list[dict], previous_summary: str = "", analysis_level: str = "l2", target_language: str = "French") -> tuple[dict, dict]:
    """LLM agent. Analyzes the solidity of the author's argument based on sources.
    analysis_level: "l2", "l3", or "l4" — selects the prompt instructions.
    Returns ({summary, needs_next_level, sources, recommended_reading?, ...}, metrics)."""

    label = "SYNTHESIZER" if analysis_level == "l2" else f"SYNTHESIZER {analysis_level.upper()}"
    raw_instructions = _INSTRUCTIONS[analysis_level]
    instructions = raw_instructions.format(target_language=target_language) if analysis_level != "l2" else raw_instructions

    claim_context = {
        "idea": idea,
        "type": claim_type,
        "child_results": child_results,
        "sources": sources,
    }
    if analysis_level != "l2" and previous_summary:
        claim_context["previous_summary"] = previous_summary

    context_json = json.dumps(claim_context, ensure_ascii=False)
    print(f"    \033[34m[{label}]\033[0m #{claim_id} — {len(sources)} sources, {len(context_json)} chars total")

    structured_llm = llm.with_structured_output(SynthesizerOutput, include_raw=True)

    t0 = time.perf_counter()
    raw_response = await llm_call_with_retry(
        lambda: structured_llm.ainvoke([
            SystemMessage(content=instructions),
            HumanMessage(content=context_json),
        ]),
        agent_name=label,
    )
    duration = time.perf_counter() - t0

    usage = raw_response["raw"].usage_metadata

    if raw_response["parsed"] is None:
        print(f"    \033[34m[{label}]\033[0m \033[31m#{claim_id} Parsing failed: {raw_response.get('parsing_error')}\033[0m")
        raw_text = raw_response["raw"].content if isinstance(raw_response["raw"].content, str) else raw_response["raw"].content[0].get("text", "")
        result = {"summary": raw_text, "needs_next_level": False, "sources": sources}
    else:
        parsed = raw_response["parsed"]
        if parsed.needs_next_level: print(f"    \033[34m[{label}]\033[0m \033[33mneeds_next_level={parsed.needs_next_level}!\033[0m")
        print(f"    \033[34m[{label}]\033[0m #{claim_id} Summary:\n{parsed.summary}")

        cited_ids = {int(m) for m in re.findall(r'\[(\d+)\]', parsed.summary)}
        cited_sources = [s for s in sources if s.get("id") in cited_ids]

        # Renumber inline [N] citations from pool-local ids to 1-based positions in cited_sources, so downstream consumers can map [N] → cited_sources[N-1].
        id_to_pos = {s["id"]: i + 1 for i, s in enumerate(cited_sources)}
        remapped_summary = re.sub(
            r'\[(\d+)\]',
            lambda m: f"[{id_to_pos[int(m.group(1))]}]" if int(m.group(1)) in id_to_pos else "",
            parsed.summary,
        )

        result = {
            "summary": remapped_summary, #mettre parsed.summary pour revenir à avant le fix
            "needs_next_level": parsed.needs_next_level,
            "sources": cited_sources,
        }
        if parsed.needs_next_level:
            result["idea"] = idea
            result["claim_type"] = claim_type
            result["child_results"] = child_results
        if parsed.recommended_reading:
            result["recommended_reading"] = [
                {**r, "id": i + 1} for i, r in enumerate(parsed.recommended_reading)
            ]
        if parsed.quote:
            result["quote"] = parsed.quote
            print(f"    \033[34m[{label}]\033[0m \033[36mQuote: \033[3m\"{parsed.quote.get('text', '')}\"\033[0m\033[36m — {parsed.quote.get('author', '?')}\033[0m")

    print(f"    \033[34m[{label}]\033[0m \033[2mTokens: {usage.get('input_tokens', 0)} in / {usage.get('output_tokens', 0)} out\033[0m")

    metrics = {
        "duration": duration,
        "passes": [
            {
                "agent": f"synthesizer_{analysis_level}",
                "model": SYNTHESIZER_MODEL,
                "input_tokens": usage.get("input_tokens", 0),
                "output_tokens": usage.get("output_tokens", 0),
            },
        ],
    }

    return result, metrics
