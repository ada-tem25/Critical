"""
Fetch & Extract — fetches web pages and extracts relevant passages.
No LLM. Uses Trafilatura for content extraction + keyword paragraph selection.
"""
import asyncio
import re
import time
from urllib.parse import urlparse
import httpx
import trafilatura
from trafilatura.settings import use_config


# Max characters per source (~800 tokens ≈ 3200 chars)
MAX_CHARS_PER_SOURCE = 3500

# Browser User-Agent to avoid basic 403 bot-blocking
_USER_AGENT = "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36"

_TRAF_CONFIG = use_config()
_TRAF_CONFIG.set("DEFAULT", "USER_AGENTS", _USER_AGENT)


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
    """Fetch a single URL and extract relevant passages.
    Cascade: httpx+Trafilatura → Jina Reader → Brave snippet."""
    url = source["url"]
    extracted = None

    # --- Tentative 1: httpx + Trafilatura ---
    try:
        response = await client.get(url, timeout=8.0, follow_redirects=True, headers={"User-Agent": _USER_AGENT})
        response.raise_for_status()
        html = response.text
        try:
            extracted = await asyncio.to_thread(
                trafilatura.extract, html,
                include_comments=False,
                include_tables=True,
                config=_TRAF_CONFIG,
            )
        except Exception as e:
            print(f"    \033[35m[FETCH]\033[0m \033[31mTrafilatura failed {url[:60]}: {e}\033[0m")
    except Exception as e:
        print(f"    \033[35m[FETCH]\033[0m \033[31mFailed {url[:60]}: {e}\033[0m")

    if extracted:
        content = _select_passages(extracted, keywords)
        return {**source, "content": content, "fetch_failed": False, "fetch_method": "direct"}

    # --- Tentative 2: Jina Reader ---
    try:
        jina_resp = await client.get(
            f"https://r.jina.ai/{url}",
            timeout=10.0,
            headers={"Accept": "text/plain", "User-Agent": _USER_AGENT},
        )
        if jina_resp.status_code == 200 and len(jina_resp.text) > 100:
            content = _select_passages(jina_resp.text[:2500], keywords)
            return {**source, "content": content, "fetch_failed": False, "fetch_method": "jina"}
    except Exception:
        pass

    # --- Tentative 3: snippet Brave (dernier recours) ---
    return {**source, "content": source.get("snippet", ""), "fetch_failed": True, "fetch_method": "snippet"}


async def fetch_and_extract(sources: list[dict], idea: str, queries: list[str]) -> tuple[list[dict], dict]:
    """Fetch pages and extract relevant passages for all sources.
    Returns (enriched_sources, metrics, failed_urls)."""

    t0 = time.perf_counter()

    # Build keyword set from claim + queries
    keywords = _extract_keywords(idea)
    for q in queries:
        keywords |= _extract_keywords(q)

    async with httpx.AsyncClient() as client:
        tasks = [_fetch_single(client, s, keywords) for s in sources]
        results = await asyncio.gather(*tasks)

    duration = time.perf_counter() - t0
    n_direct = sum(1 for r in results if r.get("fetch_method") == "direct")
    n_jina = sum(1 for r in results if r.get("fetch_method") == "jina")
    n_failed = sum(1 for r in results if r.get("fetch_failed"))
    print(f"    \033[35m[FETCH]\033[0m {len(sources)} URLs → {n_direct} direct, {n_jina} via Jina, {n_failed} failed ({duration:.2f}s)")
    for r in results:
        parsed = urlparse(r["url"])
        short_url = parsed.hostname.replace("www.", "") + parsed.path[:40]
        print(f"      \033[2m{len(r.get('content', '')):>5}c — {short_url}\033[0m")

    failed_urls = [r["url"] for r in results if r.get("fetch_failed")]
    metrics = {"duration": duration}
    return results, metrics, failed_urls
