"""
Rank & Select — deterministic scorer for search results.
No LLM. Uses domain registry for reliability + keyword TF for relevance.
"""
import re
from domain_registry import get_domain_meta


# Reliability tier → weight
_RELIABILITY_WEIGHTS = {
    "reference": 3.0,
    "established": 2.0,
    "oriented": 1.0,
    "unknown": 0.5,
}


def _extract_keywords(text: str, min_length: int = 3) -> set[str]:
    """Extract lowercase keywords from text, filtering short words."""
    words = re.findall(r'\b\w+\b', text.lower())
    return {w for w in words if len(w) >= min_length}


def _snippet_relevance(snippet: str, keywords: set[str]) -> float:
    """Compute keyword overlap ratio between snippet and claim keywords."""
    if not keywords:
        return 0.0
    snippet_words = _extract_keywords(snippet)
    if not snippet_words:
        return 0.0
    overlap = keywords & snippet_words
    return len(overlap) / len(keywords)


def rank_and_select(results: list[dict], idea: str, queries: list[str], min_sources: int = 5, max_sources: int = 10, excluded_urls: set[str] | None = None) -> list[dict]:
    """Score and rank search results. Returns top sources with metadata.

    Scoring: reliability_weight * 0.6 + snippet_relevance * 0.4
    If <min_sources tiered sources, fills with best unknown sources.
    """
    if excluded_urls:
        results = [r for r in results if r["url"] not in excluded_urls]

    # Build keyword set from claim idea + all queries
    keywords = _extract_keywords(idea)
    for q in queries:
        keywords |= _extract_keywords(q)

    scored = []
    for r in results:
        meta = get_domain_meta(r["url"])
        if meta:
            reliability = meta.get("reliability", "unknown")
            category = meta.get("category", "unknown")
            bias = meta.get("bias", "neutral")
        else:
            reliability = "unknown"
            category = "unknown"
            bias = "unknown"

        rel_weight = _RELIABILITY_WEIGHTS.get(reliability, 0.5)
        snippet_score = _snippet_relevance(r.get("snippet", ""), keywords)
        score = rel_weight * 0.6 + snippet_score * 0.4

        scored.append({
            "url": r["url"],
            "title": r["title"],
            "snippet": r.get("snippet", ""),
            "reliability": reliability,
            "category": category,
            "bias": bias,
            "score": round(score, 3),
        })

    # Sort by score descending
    scored.sort(key=lambda x: x["score"], reverse=True)

    # Select: prioritize tiered sources, fill with unknown if needed
    tiered = [s for s in scored if s["reliability"] != "unknown"]
    unknown = [s for s in scored if s["reliability"] == "unknown"]

    if len(tiered) >= min_sources:
        selected = tiered[:max_sources]
    else:
        # Not enough tiered — fill with best unknown
        needed = min_sources - len(tiered)
        selected = tiered + unknown[:needed]
        # Cap at max
        selected = selected[:max_sources]

    print(f"    \033[35m[RANK]\033[0m {len(results)} results → {len(selected)} selected (tiered: {len(tiered)}, unknown: {len(unknown)})")
    for s in selected:
        print(f"      \033[2m[{s['reliability']}/{s['category']}] score={s['score']} — {s['url']}\033[0m")

    return selected
