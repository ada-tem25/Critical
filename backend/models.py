"""
Pydantic models shared across the pipeline.
"""
from typing import Optional
from pydantic import BaseModel


class Rhetoric(BaseModel):
    type: str
    passage: str
    explanation: str


class Source(BaseModel):
    url: str
    title: str
    date: str
    anchor: str
    bias: str


class Claim(BaseModel):
    id: int
    idea: str
    verifiability: Optional[str] = None  # A | B | C | D | E
    type: Optional[str] = None
    role: str           # thesis | supporting | counterargument
    supports: list[int]


class RecommendedReading(BaseModel):
    id: int
    url: str = ""
    title: str
    author: str
    year: int


class AnalyzedClaim(BaseModel):
    claim_id: int
    idea: str
    role: str
    summary: str
    analyzed: bool = False
    supports: list[int]
    sources: list[Source]
    analysis: Optional[str] = None
    perspective: str = ""
    recommended_reading: list[RecommendedReading] = []


class ArticleSource(BaseModel):
    id: int
    url: str
    title: str
    date: str
    bias: str

class ArticleQuote(BaseModel):
    text: str
    author: str
    date: str


class PipelineResult(BaseModel):
    # Original input
    text: str
    source_type: str
    source_url: str
    date: str
    rhetorics: list[Rhetoric]
    analyzed_claims: list[AnalyzedClaim]

    # Writer output
    title: str
    subtitle: Optional[str] = None
    verdict: str
    summary: str
    article: str
    format: str  # "short" or "long"
    sources: list[ArticleSource]
    quote: Optional[ArticleQuote] = None
