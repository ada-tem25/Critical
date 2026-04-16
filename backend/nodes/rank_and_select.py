"""
Rank & Select — deterministic scorer for search results.
No LLM. Uses domain registry for reliability + keyword TF for relevance.
"""
import re
from domain_registry import get_domain_meta
from utils import get_categories_for_type


# Reliability tier → weight
_RELIABILITY_WEIGHTS = {
    "reference": 2.0,
    "established": 1.5,
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


def rank_and_select(results: list[dict], idea: str, queries: list[str], claim_type: str = "", min_sources: int = 4, max_sources: int = 6, excluded_urls: set[str] | None = None) -> list[dict]:
    """Score and rank search results. Returns top sources with metadata.

    Scoring: reliability_weight * 0.5 + snippet_relevance * 0.3 + category_boost * 0.2
    Category boost: sources whose category matches the preferred categories for the claim type.
    If <min_sources tiered sources, fills with best unknown sources.
    """
    if excluded_urls:
        results = [r for r in results if r["url"] not in excluded_urls]

    # Build keyword set from claim idea + all queries
    keywords = _extract_keywords(idea)
    for q in queries:
        keywords |= _extract_keywords(q)

    preferred_categories = set(get_categories_for_type(claim_type))

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
        category_boost = 0.2 if category in preferred_categories else 0.0
        score = rel_weight * 0.5 + snippet_score * 0.3 + category_boost

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

    print(f"    \033[35m[RANK]\033[0m {len(results)} results → {len(selected)} selected ({len(tiered)} tiered, {len(unknown)} unknown)")

    return selected
