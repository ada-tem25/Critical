"""
Writer agent — produces the final journalistic fact-check article.
"""
from normalizer import NormalizedInput
from models import AnalyzedClaim, Rhetoric

WRITER_MODEL = "claude-sonnet-4-6-20250514"


async def write_article(normalized: NormalizedInput, analyzed_claims: list[AnalyzedClaim], rhetorics: list[Rhetoric]) -> str:
    """LLM agent. Produces the final journalistic fact-check article."""
    # TODO: implement
    return "[Article placeholder]"
