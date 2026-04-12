"""
Fetch & Extract — fetches web pages and extracts relevant passages.
No LLM. Uses Trafilatura for content extraction + keyword paragraph selection.
"""
import asyncio
import re
import time
import httpx
import trafilatura


# Max characters per source (~800 tokens ≈ 3200 chars)
MAX_CHARS_PER_SOURCE = 3200


def _extract_keywords(text: str, min_length: int = 3) -> set[str]:
    """Extract lowercase keywords from text."""
    words = re.findall(r'\b\w+\b', text.lower())
    return {w for w in words if len(w) >= min_length}


def _score_paragraph(paragraph: str, keywords: set[str]) -> float:
    """Score a paragraph by keyword overlap."""
    if not keywords or not paragraph.strip():
        return 0.0
    para_words = _extract_keywords(paragraph)
    if not para_words:
        return 0.0
    return len(keywords & para_words) / len(keywords)


def _select_passages(text: str, keywords: set[str], max_chars: int = MAX_CHARS_PER_SOURCE) -> str:
    """Split text into paragraphs, score by keyword relevance, keep top ones."""
    paragraphs = [p.strip() for p in text.split("\n\n") if p.strip()]

    if not paragraphs:
        return text[:max_chars]

    # If total text is short enough, keep it all
    if len(text) <= max_chars:
        return text

    # Score and sort paragraphs
    scored = [(p, _score_paragraph(p, keywords)) for p in paragraphs]
    scored.sort(key=lambda x: x[1], reverse=True)

    # Greedily take top paragraphs until budget exhausted
    selected = []
    total_chars = 0
    for para, score in scored:
        if total_chars + len(para) > max_chars:
            # If we have nothing yet, take a truncated first paragraph
            if not selected:
                selected.append(para[:max_chars])
            break
        selected.append(para)
        total_chars += len(para)

    # Re-order by original position for coherence
    original_order = {p: i for i, p in enumerate(paragraphs)}
    selected.sort(key=lambda p: original_order.get(p, 0))

    return "\n\n".join(selected)


async def _fetch_single(client: httpx.AsyncClient, source: dict, keywords: set[str]) -> dict:
    """Fetch a single URL and extract relevant passages."""
    url = source["url"]

    try:
        response = await client.get(url, timeout=8.0, follow_redirects=True)
        response.raise_for_status()
        html = response.text
    except Exception as e:
        print(f"    \033[35m[FETCH]\033[0m \033[31mFailed {url[:60]}: {e}\033[0m")
        # Fallback: keep the Brave snippet as content
        return {
            **source,
            "content": source.get("snippet", ""),
            "fetch_failed": True,
        }

    # Extract text with Trafilatura (sync, run in thread)
    try:
        extracted = await asyncio.to_thread(
            trafilatura.extract, html,
            include_comments=False,
            include_tables=True,
        )
    except Exception as e:
        print(f"    \033[35m[FETCH]\033[0m \033[31mTrafilatura failed {url[:60]}: {e}\033[0m")
        return {
            **source,
            "content": source.get("snippet", ""),
            "fetch_failed": True,
        }

    if not extracted:
        return {
            **source,
            "content": source.get("snippet", ""),
            "fetch_failed": True,
        }

    # Select relevant passages
    content = _select_passages(extracted, keywords)

    return {
        **source,
        "content": content,
        "fetch_failed": False,
    }


async def fetch_and_extract(sources: list[dict], idea: str, queries: list[str]) -> tuple[list[dict], dict]:
    """Fetch pages and extract relevant passages for all sources.
    Returns (enriched_sources, metrics)."""

    t0 = time.perf_counter()

    # Build keyword set from claim + queries
    keywords = _extract_keywords(idea)
    for q in queries:
        keywords |= _extract_keywords(q)

    async with httpx.AsyncClient() as client:
        tasks = [_fetch_single(client, s, keywords) for s in sources]
        results = await asyncio.gather(*tasks)

    duration = time.perf_counter() - t0
    fetched_ok = sum(1 for r in results if not r.get("fetch_failed"))
    print(f"    \033[35m[FETCH]\033[0m {len(sources)} URLs → {fetched_ok} fetched OK, {len(sources) - fetched_ok} failed ({duration:.2f}s)")
    for r in results:
        if r.get("fetch_failed"):
            print(f"      \033[2m[FALLBACK] {len(r.get('content', ''))} chars — {r['url']}\033[0m")
        else:
            print(f"      \033[32m[OK]\033[0m {len(r.get('content', ''))} chars — {r['url']}")

    metrics = {"duration": duration}
    return results, metrics
