"""
Web Research — Tavily search + deterministic domain tagger.
No LLM call. Executes queries, deduplicates results, tags each source by domain tier.
"""
import os
import time
from urllib.parse import urlparse
from dotenv import load_dotenv
from tavily import AsyncTavilyClient
from domain_registry import DOMAIN_REGISTRY

load_dotenv()

tavily = AsyncTavilyClient(api_key=os.getenv("TAVILY_KEY"))


def _extract_domain(url: str) -> str:
    """Extracts the root domain from a URL (e.g. 'www.lemonde.fr' → 'lemonde.fr')."""
    hostname = urlparse(url).hostname or ""
    parts = hostname.split(".")
    if len(parts) > 2:
        return ".".join(parts[-2:])
    return hostname


def _tag_domain(url: str) -> dict:
    """Tags a URL with its tier and bias from the domain registry."""
    domain = _extract_domain(url)
    entry = DOMAIN_REGISTRY.get(domain)
    if entry is None:
        return {"tier": "unknown", "bias": "unknown"}
    return {"tier": entry["tier"], "bias": entry.get("bias", "neutral")}


async def search_and_tag(claim_id: int, queries: list[str]) -> tuple[list[dict], dict]:
    """Executes Tavily searches for all queries, deduplicates, tags by domain.
    Returns (tagged_sources, metrics)."""

    t0 = time.perf_counter()
    seen_urls: set[str] = set()
    all_results: list[dict] = []

    for query in queries:
        response = await tavily.search(query=query, max_results=5)
        for result in response.get("results", []):
            url = result.get("url", "")
            if url in seen_urls:
                continue
            seen_urls.add(url)

            tag = _tag_domain(url)
            all_results.append({
                "url": url,
                "title": result.get("title", ""),
                "content": result.get("content", ""),
                "tier": tag["tier"],
                "bias": tag["bias"],
            })

    # Filter out unknown sources
    tagged_sources = [r for r in all_results if r["tier"] != "unknown"]
    unknown_count = len(all_results) - len(tagged_sources)

    duration = time.perf_counter() - t0

    print(f"    [WEB RESEARCH] #{claim_id} — {len(all_results)} results, {len(tagged_sources)} kept, {unknown_count} discarded ({duration:.2f}s)")
    if tagged_sources:
        print(f"    [WEB RESEARCH] Kept:")
        for s in tagged_sources:
            print(f"      [{s['tier']}] {_extract_domain(s['url'])} — {s['title'][:80]}")
    unknown_sources = [r for r in all_results if r["tier"] == "unknown"]
    if unknown_sources:
        print(f"    [WEB RESEARCH] Discarded (unknown):")
        for s in unknown_sources:
            print(f"      {_extract_domain(s['url'])} — {s['title'][:80]}")

    metrics = {
        "duration": duration,
        "total_results": len(all_results),
        "tagged_results": len(tagged_sources),
        "unknown_discarded": unknown_count,
    }

    return tagged_sources, metrics
