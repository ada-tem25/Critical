"""
Generate Queries agent — produces 1-3 search queries to verify a claim.
"""
import json
import time
from pydantic import BaseModel
from dotenv import load_dotenv
from langchain_anthropic import ChatAnthropic
from langchain_core.messages import SystemMessage, HumanMessage
from prompts.queries import generate_queries_l2_instructions

load_dotenv()

GENERATE_QUERIES_MODEL = "claude-haiku-4-5"

llm = ChatAnthropic(model=GENERATE_QUERIES_MODEL, temperature=0)


class QueryList(BaseModel):
    """Structured output: list of search queries."""
    queries: list[str]


async def generate_queries_l2(claim_id: int, idea: str, claim_type: str, child_results: list[dict]) -> tuple[list[str], dict]:
    """LLM agent. Generates 1-3 search queries for a claim.
    Returns (queries, metrics)."""

    # Build the claim context for the LLM
    claim_context = {
        "idea": idea,
        "type": claim_type,
        "child_results": child_results,
    }

    structured_llm = llm.with_structured_output(QueryList, include_raw=True)

    t0 = time.perf_counter()
    raw_response = await structured_llm.ainvoke([ # LLM Call
        SystemMessage(content=[{"type": "text", "text": generate_queries_l2_instructions, "cache_control": {"type": "ephemeral"}}]),
        HumanMessage(content=json.dumps(claim_context, ensure_ascii=False)),
    ])
    duration = time.perf_counter() - t0

    if raw_response["parsed"] is None: # Error handling
        print(f"    [GENERATE QUERIES] Parsing failed: {raw_response.get('parsing_error')}")
        print(f"    [GENERATE QUERIES] Raw output: {raw_response['raw'].content}")
        return [idea], {"duration": duration, "passes": []}

    queries = raw_response["parsed"].queries
    usage = raw_response["raw"].usage_metadata
    details = usage.get("input_token_details", {})

    print(f"    [GENERATE QUERIES] #{claim_id} [{claim_type}] → {queries} ({duration:.2f}s)")

    metrics = {
        "duration": duration,
        "passes": [
            {
                "model": GENERATE_QUERIES_MODEL,
                "input_tokens": usage.get("input_tokens", 0),
                "output_tokens": usage.get("output_tokens", 0),
                "cache_creation_input_tokens": details.get("ephemeral_5m_input_tokens", 0),
                "cache_read_input_tokens": details.get("cache_read", 0),
            },
        ],
    }

    return queries, metrics
