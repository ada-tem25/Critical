"""
LLM retry helper — retries LLM calls on rate limit errors using retry-after header.
"""
import asyncio
from anthropic import RateLimitError


async def llm_call_with_retry(coro_factory, agent_name: str, max_retries: int = 5):
    """Retry an LLM call on rate limit, sleeping for retry-after seconds.

    coro_factory: a callable that returns a new coroutine each time (e.g. lambda: llm.ainvoke(...))
    agent_name: display name for log messages (e.g. "REFLECTION")
    """
    for attempt in range(max_retries + 1):
        try:
            return await coro_factory()
        except RateLimitError as e:
            if attempt == max_retries:
                raise
            retry_after = int(e.response.headers.get("retry-after", 30))
            print(f"    \033[31m[{agent_name}] Rate limit — retry in {retry_after}s (attempt {attempt + 1}/{max_retries})\033[0m")
            await asyncio.sleep(retry_after)
