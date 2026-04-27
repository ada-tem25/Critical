"""
Writer agent — produces the final journalistic fact-check article.
"""
import json
import re
import time
from typing import Optional
from dotenv import load_dotenv
from langchain_anthropic import ChatAnthropic
from langchain_core.messages import SystemMessage, HumanMessage
from pydantic import BaseModel, Field
from normalizer import NormalizedInput
from models import AnalyzedClaim, Rhetoric
from prompts.writer import writer_instructions
from llm_retry import llm_call_with_retry

load_dotenv()

WRITER_MODEL = "claude-sonnet-4-6"

llm = ChatAnthropic(model=WRITER_MODEL, temperature=0)


class WriterOutput(BaseModel):
    title: str = Field(description="Article title.")
    subtitle: Optional[str] = Field(default=None, description="Optional subtitle.")
    verdict: str = Field(description="Displayed verdict: VRAI, FAUX, INCERTAIN, TROMPEUR, etc.")
    summary: str = Field(description="Short summary of the article (2-3 sentences).")
    article: str = Field(description="Full journalistic fact-check article with *N source citations and optional ~N quote marker.")
    rationale: str = Field(default="", description="Concrete problems encountered in the inputs during writing.")


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
        for s in uncited:
            print(f"    \033[2m[*{s['id']}] {s['title']} — {s['url']}\033[0m")

    return cited, updated_article


def _extract_quote(article: str, analyzed_claims: list[AnalyzedClaim]) -> Optional[dict]:
    """Scans article for a ~N marker and resolves it to the quote from the referenced claim."""
    matches = re.findall(r'~(\d+)', article)
    if not matches:
        return None

    claim_id = int(matches[0])
    if len(matches) > 1:
        print(f"\033[35m[WRITER]\033[0m \033[33mWarning: multiple ~N markers found, using first (~{claim_id})\033[0m")

    claims_by_id = {c.claim_id: c for c in analyzed_claims}
    claim = claims_by_id.get(claim_id)

    if not claim:
        print(f"\033[35m[WRITER]\033[0m \033[33mWarning: ~{claim_id} references non-existent claim\033[0m")
        return None
    if not claim.quote:
        print(f"\033[35m[WRITER]\033[0m \033[33mWarning: ~{claim_id} references claim with no quote\033[0m")
        return None

    print(f"\033[35m[WRITER]\033[0m Quote (~{claim_id}): \033[3m\"{claim.quote.text}\"\033[0m — {claim.quote.author}")
    return {"text": claim.quote.text, "author": claim.quote.author, "date": claim.quote.date}


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
                "summary": c.summary,
                "analyzed": c.analyzed,
                "supports": c.supports,
                "source_ids": [url_to_id[s.url] for s in c.sources if s.url in url_to_id],
                "analysis": c.analysis,
                "perspective": c.perspective,
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
    return json.dumps(context, ensure_ascii=False)


async def write_article(normalized: NormalizedInput, analyzed_claims: list[AnalyzedClaim], rhetorics: list[Rhetoric], target_language: str = "English") -> tuple[dict, dict]:
    """LLM agent. Produces the final journalistic fact-check article.
    Returns (result_dict, metrics_dict)."""

    registry, url_to_id = _build_source_registry(analyzed_claims)
    context_json = _build_context(normalized, analyzed_claims, rhetorics, registry, url_to_id)
    print(f"\033[35m[WRITER]\033[0m Context: {len(context_json)} chars, {len(analyzed_claims)} claims, {len(rhetorics)} rhetorics, {len(registry)} sources in registry")

    structured_llm = llm.with_structured_output(WriterOutput, include_raw=True)

    formatted_instructions = writer_instructions.format(
        target_language=target_language
    )

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

    if raw_response["parsed"] is None:
        print(f"\033[35m[WRITER]\033[0m \033[31mParsing failed: {raw_response.get('parsing_error')}\033[0m")
    else:
        parsed = raw_response["parsed"]
        article_text = parsed.article

        # Post-processing: build sources list from registry based on *N citations
        cited_sources, article_text = _extract_cited_sources(article_text, registry)

        # Post-processing: resolve ~N quote marker
        quote = _extract_quote(article_text, analyzed_claims)

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
        "duration": duration,
        "passes": [
            {
                "agent": "writer",
                "model": WRITER_MODEL,
                "input_tokens": usage.get("input_tokens", 0),
                "output_tokens": usage.get("output_tokens", 0),
                "cache_creation_input_tokens": usage.get("cache_creation_input_tokens", 0),
                "cache_read_input_tokens": usage.get("cache_read_input_tokens", 0),
            },
        ],
    }

    return result, metrics
