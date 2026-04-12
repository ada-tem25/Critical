"""
Brave Search — calls Brave Web Search API, deduplicates results by URL.
No LLM. Pure HTTP calls with rate limiting.
"""
import os
import asyncio
import time
from urllib.parse import urlparse
from dotenv import load_dotenv
import httpx

load_dotenv()

BRAVE_API_KEY = os.getenv("BRAVE_API_KEY", "")
BRAVE_ENDPOINT = "https://api.search.brave.com/res/v1/web/search"

# Rate limiter: Brave free tier = 1 req/s
_rate_semaphore = asyncio.Semaphore(1)

# Country → search language mapping
_COUNTRY_TO_LANG = {
    "FR": "fr", "BE": "fr", "CH": "fr", "LU": "fr",
    "DE": "de", "AT": "de",
    "ES": "es",
    "IT": "it",
    "PT": "pt",
    "NL": "nl",
    "US": "en", "UK": "en", "IE": "en", "CA": "en", "AU": "en",
}


def _normalize_url(url: str) -> str:
    """Normalize URL for dedup: strip scheme, trailing slash, www."""
    parsed = urlparse(url)
    host = (parsed.hostname or "").replace("www.", "")
    path = parsed.path.rstrip("/")
    return f"{host}{path}"


async def _search_single(client: httpx.AsyncClient, query: str, country: str) -> list[dict]:
    """Execute a single Brave search query with rate limiting."""
    async with _rate_semaphore:
        params = {
            "q": query,
            "count": 10,
        }
        lang = _COUNTRY_TO_LANG.get(country)
        if lang:
            params["search_lang"] = lang
        if country and country != "INT":
            params["country"] = country

        headers = {
            "Accept": "application/json",
            "Accept-Encoding": "gzip",
            "X-Subscription-Token": BRAVE_API_KEY,
        }

        try:
            response = await client.get(BRAVE_ENDPOINT, params=params, headers=headers, timeout=10.0)
            response.raise_for_status()
            data = response.json()
        except Exception as e:
            print(f"    \033[36m[BRAVE]\033[0m \033[31mQuery '{query}' failed: {e}\033[0m")
            return []

        results = []
        for item in data.get("web", {}).get("results", []):
            results.append({
                "url": item.get("url", ""),
                "title": item.get("title", ""),
                "snippet": item.get("description", ""),
                "age": item.get("age", ""),
            })

        # 1s delay between requests for rate limiting
        await asyncio.sleep(1.0)
        return results


async def brave_search(queries: list[str], country: str = "INT") -> tuple[list[dict], dict]:
    """Execute multiple Brave searches, deduplicate results by URL.
    Returns (results, metrics)."""

    t0 = time.perf_counter()

    async with httpx.AsyncClient() as client:
        tasks = [_search_single(client, q, country) for q in queries]
        all_results = await asyncio.gather(*tasks)

    # Flatten and deduplicate by normalized URL
    seen_urls = set()
    deduped = []
    for batch in all_results:
        for r in batch:
            norm = _normalize_url(r["url"])
            if norm not in seen_urls:
                seen_urls.add(norm)
                deduped.append(r)

    duration = time.perf_counter() - t0
    query_count = len(queries)
    print(f"    \033[36m[BRAVE]\033[0m {query_count} queries → {sum(len(b) for b in all_results)} raw results → {len(deduped)} after dedup ({duration:.2f}s)")

    metrics = {
        "duration": duration,
        "passes": [
            {
                "agent": "brave_search",
                "type": "api",
                "query_count": query_count,
                "cost": query_count * 0.005,
            },
        ],
    }
    return deduped, metrics
