"""
Generate Queries agent — produces 1-3 search queries to verify a claim.
"""
import json
import re
import time
from dotenv import load_dotenv
from langchain_anthropic import ChatAnthropic
from langchain_core.messages import SystemMessage, HumanMessage
from prompts.queries import generate_queries_l2_instructions
from llm_retry import llm_call_with_retry

load_dotenv()

GENERATE_QUERIES_MODEL = "claude-haiku-4-5"

llm = ChatAnthropic(model=GENERATE_QUERIES_MODEL, temperature=0)

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


async def generate_queries_l2(claim_id: int, idea: str, claim_type: str, child_results: list[dict], country: str = "INT") -> tuple[list[str], dict]:
    """LLM agent. Generates 1-3 search queries for a claim.
    Returns (queries, metrics)."""

    # Build the claim context for the LLM
    claim_context = {
        "idea": idea,
        "type": claim_type,
        "child_results": child_results,
        "country": country,
    }

    t0 = time.perf_counter()
    response = await llm_call_with_retry(
        lambda: llm.ainvoke([
            SystemMessage(content=[{"type": "text", "text": generate_queries_l2_instructions}]),
            HumanMessage(content=json.dumps(claim_context, ensure_ascii=False)),
        ]),
        agent_name="GENERATE QUERIES",
    )
    duration = time.perf_counter() - t0

    # Parse JSON list from raw response
    raw_text = response.content if isinstance(response.content, str) else response.content[0].get("text", "")
    queries = _parse_queries(raw_text, idea)

    if queries == [idea]: #Error handling
        print(f"    \033[34m[GENERATE QUERIES]\033[0m \033[33mParsing failed, using fallback\033[0m")
        print(f"    \033[34m[GENERATE QUERIES]\033[0m \033[2mRaw output: {raw_text}\033[0m")
        return [idea], {"duration": duration, "passes": []}

    usage = response.usage_metadata

    print(f"\n{'-'*50}")
    print(f"    \033[34m[GENERATE QUERIES]\033[0m #{claim_id} [{claim_type}] → {queries} ({duration:.2f}s)")

    metrics = {
        "duration": duration,
        "passes": [
            {
                "agent": "generate_queries",
                "model": GENERATE_QUERIES_MODEL,
                "input_tokens": usage.get("input_tokens", 0),
                "output_tokens": usage.get("output_tokens", 0),
            },
        ],
    }

    return queries, metrics
