"""
Writer agent — produces the final journalistic fact-check article.
"""
import json
import os
import re
import time
from typing import Optional
from dotenv import load_dotenv
from langchain_anthropic import ChatAnthropic
from langchain_core.messages import SystemMessage, HumanMessage
from pydantic import BaseModel, Field
from normalizer import NormalizedInput
from models import AnalyzedClaim, Rhetoric
from prompts.writer import writer_instructions, editor_instructions
from llm_retry import llm_call_with_retry

load_dotenv()

WRITER_MODEL = "claude-sonnet-4-6"
EDITOR_MODEL = "claude-haiku-4-5"

llm = ChatAnthropic(model=WRITER_MODEL, temperature=0)
llm_editor = ChatAnthropic(model=EDITOR_MODEL, temperature=0)


class WriterOutput(BaseModel):
    title: str = Field(description="Article title.")
    subtitle: Optional[str] = Field(default=None, description="Optional subtitle.")
    verdict: str = Field(description="Displayed verdict: Vrai, Faux, Incertain, Trompeur, etc.")
    summary: str = Field(description="Short summary of the article (2-3 sentences).")
    article: str = Field(description="Full journalistic fact-check article with *N source citations and optional ~N quote marker.")
    rationale: str = Field(default="", description="Concrete problems encountered in the inputs during writing.")


# ============================ Post-processing - Sources remapping ===============================

def _build_source_registry(analyzed_claims: list[AnalyzedClaim]) -> tuple[list[dict], dict]:
    """Deduplicates sources across all claims and assigns global sequential IDs.
    Returns (registry_list, url_to_id_map)."""
    url_to_id = {}
    registry = []
    for claim in analyzed_claims:
        for s in claim.sources:
            if s.url not in url_to_id:
                sid = len(registry) + 1
                url_to_id[s.url] = sid
                registry.append({
                    "id": sid,
                    "url": s.url,
                    "title": s.title,
                    "date": s.date,
                    "bias": s.bias,
                })
    return registry, url_to_id


def _extract_cited_sources(article: str, registry: list[dict]) -> tuple[list[dict], str]:
    """Scans article for *N markers, renumbers them sequentially from 1, and returns (cited_sources, updated_article)."""
    cited_ids = {int(m) for m in re.findall(r'\*(\d+)', article)}
    registry_by_id = {s["id"]: s for s in registry}

    invalid = cited_ids - set(registry_by_id.keys())
    if invalid:
        print(f"\033[35m[WRITER]\033[0m \033[33mWarning: invalid source ids in article: {invalid}\033[0m")

    old_to_new = {old_id: new_id for new_id, old_id in enumerate(sorted(cited_ids & set(registry_by_id.keys())), 1)}

    cited = []
    for old_id, new_id in sorted(old_to_new.items(), key=lambda x: x[1]):
        s = {**registry_by_id[old_id], "id": new_id}
        cited.append(s)

    updated_article = re.sub(r'\*(\d+)', lambda m: f"*{old_to_new[int(m.group(1))]}" if int(m.group(1)) in old_to_new else m.group(0), article)

    print(f"\033[35m[WRITER]\033[0m Sources cited in article ({len(cited)}/{len(registry)}):")
    for s in cited:
        print(f"    \033[35m[*{s['id']}]\033[0m {s['title']}")
        print(f"        \033[2m{s['url']}\033[0m")

    uncited = [s for s in registry if s["id"] not in cited_ids]
    if uncited:
        print(f"\033[35m[WRITER]\033[0m \033[2mUncited sources ({len(uncited)}):\033[0m")
        for s in uncited: print(f"    \033[2m[*{s['id']}] {s['title']} — {s['url']}\033[0m")

    return cited, updated_article

def _remap_inline_citations(text: str, claim_sources: list, url_to_id: dict) -> str:
    """Rewrites [N] markers — where N is a 1-based index into claim_sources —
    into [G] where G is the global registry id. Orphan markers are stripped."""
    if not text:
        return text
    def repl(m):
        local = int(m.group(1))
        if 1 <= local <= len(claim_sources):
            gid = url_to_id.get(claim_sources[local - 1].url)
            if gid is not None:
                return f"[{gid}]"
        return ""
    return re.sub(r'\[(\d+)\]', repl, text)


# ============================ Post-processing - Strip stray headers ===============================

def _strip_headers(article: str) -> str:
    """Removes markdown headers (## ...) and standalone bold-only lines (**Title**)
    that the Writer sometimes inserts despite the prompt instructions.
    Inline **...** (used for rhetoric names) is preserved."""
    if not article:
        return article

    removed = 0
    lines = article.splitlines()
    cleaned = []
    md_header = re.compile(r'^\s*#{1,6}\s+\S')
    bold_only = re.compile(r'^\s*\*\*[^*\n]+\*\*\s*:?\s*$')

    for line in lines:
        if md_header.match(line) or bold_only.match(line):
            removed += 1
            continue
        cleaned.append(line)

    out = "\n".join(cleaned)
    out = re.sub(r'\n{3,}', '\n\n', out).strip()

    if removed:
        print(f"\033[35m[WRITER]\033[0m Stripped {removed} stray header line(s)")
    return out


# ============================ Post-processing - Quote extraction ===============================

def _extract_quote(article: str, analyzed_claims: list[AnalyzedClaim]) -> tuple[Optional[dict], str]:
    """Scans article for a ~N marker and resolves it to the quote from the referenced claim.
    Returns (quote_dict_or_None, updated_article). Orphan markers are stripped."""
    matches = re.findall(r'~(\d+)', article)
    if not matches:
        return None, article

    claim_id = int(matches[0])
    if len(matches) > 1:
        print(f"\033[35m[WRITER]\033[0m \033[33mWarning: multiple ~N markers found, using first (~{claim_id})\033[0m")

    claims_by_id = {c.claim_id: c for c in analyzed_claims}
    claim = claims_by_id.get(claim_id)

    if not claim:
        print(f"\033[35m[WRITER]\033[0m \033[33mWarning: ~{claim_id} references non-existent claim — marker stripped\033[0m")
        return None, re.sub(r'\s*~\d+\b', '', article)
    if not claim.quote:
        print(f"\033[35m[WRITER]\033[0m \033[33mWarning: ~{claim_id} references claim with no quote — marker stripped\033[0m")
        return None, re.sub(r'\s*~\d+\b', '', article)

    print(f"\033[35m[WRITER]\033[0m Quote (~{claim_id}): \033[3m\"{claim.quote.text}\"\033[0m — {claim.quote.author}")
    return {"text": claim.quote.text, "author": claim.quote.author, "date": claim.quote.date}, article


# ============================ Context building ===============================

def _build_context(normalized: NormalizedInput, analyzed_claims: list[AnalyzedClaim], rhetorics: list[Rhetoric], registry: list[dict], url_to_id: dict) -> str:
    """Builds the JSON context string sent to the Writer LLM."""
    context = {
        "origin_content": {
            "text": normalized.text,
            "type": normalized.source_type,
            "url": normalized.source_url,
            "author": normalized.author,
            "date": normalized.date,
        },
        "source_registry": registry,
        "analyzed_claims": [
            {
                "id": c.claim_id,
                "idea": c.idea,
                "role": c.role,
                "summary": _remap_inline_citations(c.summary, c.sources, url_to_id),
                "analyzed": c.analyzed,
                "supports": c.supports,
                "source_ids": [url_to_id[s.url] for s in c.sources if s.url in url_to_id],
                "analysis": _remap_inline_citations(c.analysis, c.sources, url_to_id),
                "perspective": _remap_inline_citations(c.perspective, c.sources, url_to_id),
                "recommended_reading": [r.model_dump() for r in c.recommended_reading],
                "quote": {"text": c.quote.text, "author": c.quote.author} if c.quote else None,
            }
            for c in analyzed_claims
        ],
        "rhetorics": [
            {"type": r.type, "passage": r.passage, "explanation": r.explanation}
            for r in rhetorics
        ],
    }
    context_json = json.dumps(context, ensure_ascii=False)

    try:
        os.makedirs("debug", exist_ok=True)
        debug_path = f"debug/writer_context_{time.strftime('%Y%m%d_%H%M%S')}.json"
        with open(debug_path, "w", encoding="utf-8") as f:
            f.write(context_json)
        print(f"\033[35m[WRITER]\033[0m \033[2mContext dumped to {debug_path}\033[0m")
    except Exception as e:
        print(f"\033[35m[WRITER]\033[0m \033[33mFailed to dump debug context: {e}\033[0m")

    return context_json



# ============================ Main Function ===============================

async def write_article(normalized: NormalizedInput, analyzed_claims: list[AnalyzedClaim], rhetorics: list[Rhetoric], target_language: str = "English") -> tuple[dict, dict]:
    """LLM agent. Produces the final journalistic fact-check article.
    Returns (result_dict, metrics_dict)."""

    # 1. Pre-processing
    registry, url_to_id = _build_source_registry(analyzed_claims)
    context_json = _build_context(normalized, analyzed_claims, rhetorics, registry, url_to_id)
    print(f"\033[35m[WRITER]\033[0m Context: {len(context_json)} chars, {len(analyzed_claims)} claims, {len(rhetorics)} rhetorics, {len(registry)} sources in registry")

    # 2. LLM Inference
    structured_llm = llm.with_structured_output(WriterOutput, include_raw=True)

    formatted_instructions = writer_instructions.format(target_language=target_language)

    t0 = time.perf_counter()
    raw_response = await llm_call_with_retry(
        lambda: structured_llm.ainvoke([
            SystemMessage(content=[{
                "type": "text",
                "text": formatted_instructions,
                "cache_control": {"type": "ephemeral"},
            }]),
            HumanMessage(content=context_json),
        ]),
        agent_name="WRITER",
    )
    duration = time.perf_counter() - t0

    usage = raw_response["raw"].usage_metadata

    editor_duration = 0.0
    editor_usage = {}

    if raw_response["parsed"] is None:
        print(f"\033[35m[WRITER]\033[0m \033[31mParsing failed: {raw_response.get('parsing_error')}\033[0m")
    else:
        parsed = raw_response["parsed"]
        article_text = parsed.article

        # 3. Post-processing
        article_text = _strip_headers(article_text) #remove stray markdown headers / bold-only title lines

        # 4. Editor pass (Haiku) — refines prose; markers *N / ~N must be preserved per its instructions
        t1 = time.perf_counter()
        try:
            editor_response = await llm_call_with_retry(
                lambda: llm_editor.ainvoke([
                    SystemMessage(content=[{
                        "type": "text",
                        "text": editor_instructions,
                        "cache_control": {"type": "ephemeral"},
                    }]),
                    HumanMessage(content=article_text),
                ]),
                agent_name="EDITOR",
            )
            editor_duration = time.perf_counter() - t1
            edited = editor_response.content
            if edited and edited.strip():
                article_text = edited
            else:
                print(f"\033[35m[EDITOR]\033[0m \033[33mEmpty output — keeping original article\033[0m")
            editor_usage = editor_response.usage_metadata or {}
            print(f"\033[35m[EDITOR]\033[0m \033[2mTokens: {editor_usage.get('input_tokens', 0)} in / {editor_usage.get('output_tokens', 0)} out | {editor_duration:.1f}s\033[0m")
        except Exception as e:
            editor_duration = time.perf_counter() - t1
            print(f"\033[35m[EDITOR]\033[0m \033[31mFailed: {e} — keeping original article\033[0m")

        # 5. Marker extraction (after Editor so it sees citations in context)
        cited_sources, article_text = _extract_cited_sources(article_text, registry) #build sources list from registry based on *N citations

        quote, article_text = _extract_quote(article_text, analyzed_claims) #resolve ~N quote marker

        result = {
            "title": parsed.title,
            "subtitle": parsed.subtitle,
            "verdict": parsed.verdict,
            "summary": parsed.summary,
            "article": article_text,
            "format": "long" if len(article_text) >= 2000 else "short",
            "sources": cited_sources,
            "quote": quote,
        }
        print(f"\033[35m[WRITER]\033[0m Verdict: {parsed.verdict} | Format: {result['format']} | {len(article_text)} chars")
        if parsed.rationale:
            print(f"\033[35m[WRITER]\033[0m \033[33mRationale:\033[0m\n{parsed.rationale}")

    print(f"\033[35m[WRITER]\033[0m \033[2mTokens: {usage.get('input_tokens', 0)} in / {usage.get('output_tokens', 0)} out | {duration:.1f}s\033[0m")

    metrics = {
        "duration": duration + editor_duration,
        "passes": [
            {
                "agent": "writer",
                "model": WRITER_MODEL,
                "input_tokens": usage.get("input_tokens", 0),
                "output_tokens": usage.get("output_tokens", 0),
                "cache_creation_input_tokens": usage.get("cache_creation_input_tokens", 0),
                "cache_read_input_tokens": usage.get("cache_read_input_tokens", 0),
            },
            {
                "agent": "editor",
                "model": EDITOR_MODEL,
                "input_tokens": editor_usage.get("input_tokens", 0),
                "output_tokens": editor_usage.get("output_tokens", 0),
                "cache_creation_input_tokens": editor_usage.get("cache_creation_input_tokens", 0),
                "cache_read_input_tokens": editor_usage.get("cache_read_input_tokens", 0),
            },
        ],
    }

    return result, metrics
