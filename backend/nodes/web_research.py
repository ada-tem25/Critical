"""
Web Research — utility functions for domain tagging and result filtering.
(Tavily search removed — Brave Search is now used instead.)
"""
from urllib.parse import urlparse
from domain_registry import DOMAIN_REGISTRY


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
