"""
Generate Queries agent — produces 1-3 search queries to verify a claim.
"""
import asyncio
import json
import re
import time
from dotenv import load_dotenv
from langchain_anthropic import ChatAnthropic
from langchain_core.messages import SystemMessage, HumanMessage
from prompts.queries import generate_queries_l2_instructions

load_dotenv()

GENERATE_QUERIES_MODEL = "claude-haiku-4-5"

llm = ChatAnthropic(model=GENERATE_QUERIES_MODEL, temperature=0)

_semaphore = None

def _get_semaphore(): #Semaphore n'envoie les requêtes à l'API que 2 à 2 pour ne pas taper le Rate Limiting
    global _semaphore
    if _semaphore is None:
        _semaphore = asyncio.Semaphore(2)
    return _semaphore


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


async def generate_queries_l2(claim_id: int, idea: str, claim_type: str, child_results: list[dict]) -> tuple[list[str], dict]:
    """LLM agent. Generates 1-3 search queries for a claim.
    Returns (queries, metrics)."""

    # Build the claim context for the LLM
    claim_context = {
        "idea": idea,
        "type": claim_type,
        "child_results": child_results,
    }

    async with _get_semaphore():
        t0 = time.perf_counter()
        response = await llm.ainvoke([ # LLM Call
            SystemMessage(content=[{"type": "text", "text": generate_queries_l2_instructions}]),
            HumanMessage(content=json.dumps(claim_context, ensure_ascii=False)),
        ])
        duration = time.perf_counter() - t0

    # Parse JSON list from raw response
    raw_text = response.content if isinstance(response.content, str) else response.content[0].get("text", "")
    queries = _parse_queries(raw_text, idea)

    if queries == [idea]: #Error handling
        print(f"    [GENERATE QUERIES] Parsing failed, using fallback")
        print(f"    [GENERATE QUERIES] Raw output: {raw_text}")
        return [idea], {"duration": duration, "passes": []}

    usage = response.usage_metadata
    details = usage.get("input_token_details", {})

    print(f"\n{'-'*50}")
    print(f"    [GENERATE QUERIES] #{claim_id} [{claim_type}] → {queries} ({duration:.2f}s)")
    print(f"    [GENERATE QUERIES] Tokens: {usage}")

    metrics = {
        "duration": duration,
        "passes": [
            {
                "agent": "generate_queries",
                "model": GENERATE_QUERIES_MODEL,
                "input_tokens": usage.get("input_tokens", 0),
                "output_tokens": usage.get("output_tokens", 0),
                "cache_creation_input_tokens": details.get("ephemeral_5m_input_tokens", 0),
                "cache_read_input_tokens": details.get("cache_read", 0),
            },
        ],
    }

    return queries, metrics
