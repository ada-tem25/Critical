"""
Writer agent — produces the final journalistic fact-check article.
"""
from normalizer import NormalizedInput
from models import AnalyzedClaim, Rhetoric


async def write_article(normalized: NormalizedInput, analyzed_claims: list[AnalyzedClaim], rhetorics: list[Rhetoric]) -> str:
    """LLM agent. Produces the final journalistic fact-check article."""
    # TODO: implement
    return "[Article placeholder]"
