"""
Writer agent — produces the final journalistic fact-check article.
"""
import json
import time
from typing import Optional
from dotenv import load_dotenv
from langchain_anthropic import ChatAnthropic
from langchain_core.messages import SystemMessage, HumanMessage
from pydantic import BaseModel, Field
from normalizer import NormalizedInput
from models import AnalyzedClaim, Rhetoric, ArticleSource, ArticleQuote
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
    article: str = Field(description="Full journalistic fact-check article.")
    sources: list[ArticleSource] = Field(description="Numbered sources cited in the article.")
    quote: Optional[ArticleQuote] = Field(default=None, description="Optional key quote from the source.")


def _build_context(normalized: NormalizedInput, analyzed_claims: list[AnalyzedClaim], rhetorics: list[Rhetoric]) -> str:
    """Builds the JSON context string sent to the Writer LLM."""
    context = {
        "source": {
            "text": normalized.text,
            "type": normalized.source_type,
            "url": normalized.source_url,
            "author": normalized.author,
            "date": normalized.date,
        },
        "analyzed_claims": [
            {
                "id": c.claim_id,
                "idea": c.idea,
                "role": c.role,
                "summary": c.summary,
                "analyzed": c.analyzed,
                "supports": c.supports,
                "sources": [s.model_dump() for s in c.sources],
                "analysis": c.analysis,
                "perspective": c.perspective,
                "recommended_reading": [r.model_dump() for r in c.recommended_reading],
            }
            for c in analyzed_claims
        ],
        "rhetorics": [
            {"type": r.type, "passage": r.passage, "explanation": r.explanation}
            for r in rhetorics
        ],
    }
    return json.dumps(context, ensure_ascii=False)


async def write_article(normalized: NormalizedInput, analyzed_claims: list[AnalyzedClaim], rhetorics: list[Rhetoric]) -> tuple[dict, dict]:
    """LLM agent. Produces the final journalistic fact-check article.
    Returns (result_dict, metrics_dict)."""

    context_json = _build_context(normalized, analyzed_claims, rhetorics)
    print(f"\033[35m[WRITER]\033[0m Context: {len(context_json)} chars, {len(analyzed_claims)} claims, {len(rhetorics)} rhetorics")

    structured_llm = llm.with_structured_output(WriterOutput, include_raw=True)

    t0 = time.perf_counter()
    raw_response = await llm_call_with_retry(
        lambda: structured_llm.ainvoke([
            SystemMessage(content=[{
                "type": "text",
                "text": writer_instructions,
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
        raw_text = raw_response["raw"].content if isinstance(raw_response["raw"].content, str) else raw_response["raw"].content[0].get("text", "")
        result = {
            "title": "",
            "subtitle": None,
            "verdict": "",
            "summary": "",
            "article": raw_text,
            "format": "long" if len(raw_text) >= 2000 else "short",
            "sources": [],
            "quote": None,
            "source_url": normalized.source_url,
            "date": normalized.date,
        }
    else:
        parsed = raw_response["parsed"]
        article_text = parsed.article
        result = {
            "title": parsed.title,
            "subtitle": parsed.subtitle,
            "verdict": parsed.verdict,
            "summary": parsed.summary,
            "article": article_text,
            "format": "long" if len(article_text) >= 2000 else "short",
            "sources": [s.model_dump() for s in parsed.sources],
            "quote": parsed.quote.model_dump() if parsed.quote else None,
            "source_url": normalized.source_url,
            "date": normalized.date,
        }
        print(f"\033[35m[WRITER]\033[0m Verdict: {parsed.verdict} | Format: {result['format']} | {len(article_text)} chars")

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
