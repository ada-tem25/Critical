"""
Generate Queries agent — produces 1-3 search queries to verify a claim.
"""
import json
import re
import time
from dotenv import load_dotenv
from langchain_anthropic import ChatAnthropic
from langchain_core.messages import SystemMessage, HumanMessage
from prompts.queries import generate_queries_l2_instructions, generate_queries_l3_instructions
from llm_retry import llm_call_with_retry

load_dotenv()

GENERATE_QUERIES_MODEL = "claude-haiku-4-5"

llm = ChatAnthropic(model=GENERATE_QUERIES_MODEL, temperature=0)

_INSTRUCTIONS = {
    "l2": generate_queries_l2_instructions,
    "l3": generate_queries_l3_instructions,
}

def _parse_queries(content: str, fallback_idea: str) -> list[str]: #This functions prevents the use of the with_structured_output tool, gaining 600 tokens per call.
    """Extract a JSON list from LLM output, tolerating markdown fences and preamble."""
    match = re.search(r'\[.*?\]', content, re.DOTALL)
    if match:
        try:
            queries = json.loads(match.group())
            if isinstance(queries, list) and all(isinstance(q, str) for q in queries):
                return queries
        except json.JSONDecodeError:
            pass
    return [fallback_idea]


async def generate_queries(claim_id: int, idea: str, claim_type: str, child_results: list[dict], country: str = "INT", l2_summary: str = "", analysis_level: str = "l2") -> tuple[list[str], dict]:
    """LLM agent. Generates 1-3 search queries for a claim.
    analysis_level: "l2" or "l3" — selects the prompt instructions.
    Returns (queries, metrics)."""

    label = f"GENERATE QUERIES" if analysis_level == "l2" else f"GENERATE QUERIES L3"
    instructions = _INSTRUCTIONS[analysis_level]

    claim_context = {
        "idea": idea,
        "type": claim_type,
        "child_results": child_results,
        "country": country,
    }
    if analysis_level == "l3" and l2_summary:
        claim_context["l2_summary"] = l2_summary

    t0 = time.perf_counter()
    response = await llm_call_with_retry(
        lambda: llm.ainvoke([
            SystemMessage(content=[{"type": "text", "text": instructions}]),
            HumanMessage(content=json.dumps(claim_context, ensure_ascii=False)),
        ]),
        agent_name=label,
    )
    duration = time.perf_counter() - t0

    raw_text = response.content if isinstance(response.content, str) else response.content[0].get("text", "")
    queries = _parse_queries(raw_text, idea)

    if queries == [idea]:
        print(f"    \033[34m[{label}]\033[0m \033[33mParsing failed, using fallback\033[0m")
        print(f"    \033[34m[{label}]\033[0m \033[2mRaw output: {raw_text}\033[0m")
        return [idea], {"duration": duration, "passes": []}

    usage = response.usage_metadata

    print(f"\n{'-'*50}")
    print(f"    \033[34m[{label}]\033[0m #{claim_id} [{claim_type}] → {queries} ({duration:.2f}s)")

    metrics = {
        "duration": duration,
        "passes": [
            {
                "agent": f"generate_queries_{analysis_level}",
                "model": GENERATE_QUERIES_MODEL,
                "input_tokens": usage.get("input_tokens", 0),
                "output_tokens": usage.get("output_tokens", 0),
            },
        ],
    }

    return queries, metrics
