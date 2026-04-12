"""
Web Research — Tavily search + deterministic domain tagger.
No LLM call. Executes queries, deduplicates results, tags each source by domain tier.
"""
import os
import time
from urllib.parse import urlparse
from dotenv import load_dotenv
from tavily import AsyncTavilyClient
from domain_registry import DOMAIN_REGISTRY, get_domains
from utils import get_tavily_country

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
    """Tags a URL with its reliability, category, and bias from the domain registry."""
    domain = _extract_domain(url)
    entry = DOMAIN_REGISTRY.get(domain)
    if entry is None:
        return {"reliability": "unknown", "category": "unknown", "bias": "unknown"}
    return {
        "reliability": entry.get("reliability", "unknown"),
        "category": entry.get("category", "unknown"),
        "bias": entry.get("bias", "neutral"),
    }


def _filter_results(results: list[dict]) -> tuple[list[dict], list[dict]]:
    """Filter out junk results (sitemaps, XML, too short/long). Returns (kept, discarded)."""
    kept, discarded = [], []
    for r in results:
        url = r.get("url", "")
        content = r.get("content", "")
        if any(kw in url.lower() for kw in ["sitemap", ".xml", "/feed", "/rss"]):
            discarded.append(r)
        elif len(content) < 100 or len(content) > 3000:
            discarded.append(r)
        else:
            kept.append(r)
    return kept, discarded


async def search_and_tag(claim_id: int, reliabilities: list[str], categories: list[str], regions: list[str], queries: list[str], country: str = "INT") -> tuple[list[dict], dict]:
    """Executes Tavily searches for all queries, deduplicates, tags by domain.
    Returns (tagged_sources, metrics)."""

    t0 = time.perf_counter()
    tagged_sources: list[dict] = []

    domains = get_domains(reliability=reliabilities, category=categories, region=regions)
    print(f"    [WEB RESEARCH] #{claim_id} Searching... ({len(domains)} domains allowed)")

    for query in queries:
        tavily_kwargs = {
            "query": query,
            "include_domains": domains,
            "max_results": 6,
        }
        tavily_country = get_tavily_country(country)
        if tavily_country:
            tavily_kwargs["country"] = tavily_country
        response = await tavily.search(**tavily_kwargs)
        for result in response.get("results", []):
            url = result.get("url", "")

            tag = _tag_domain(url)
            tagged_sources.append({
                "url": url,
                "title": result.get("title", ""),
                "content": result.get("content", ""),
                "reliability": tag["reliability"],
                "category": tag["category"],
                "bias": tag["bias"],
            })

    # Filter junk results that may come out of the Tavily API call
    kept, discarded = _filter_results(tagged_sources)
    duration = time.perf_counter() - t0

    # Number kept sources (1-indexed) so downstream agents can reference them as [1], [2], etc.
    for i, s in enumerate(kept):
        s["id"] = i + 1

    print(f"    [WEB RESEARCH] #{claim_id} — {len(tagged_sources)} sources, {len(kept)} kept, {len(discarded)} filtered ({duration:.2f}s)")

    metrics = {
        "duration": duration
    }

    return kept, metrics
