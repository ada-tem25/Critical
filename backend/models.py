"""
Pydantic models shared across the pipeline.
"""
from typing import Optional
from uuid import uuid4
from pydantic import BaseModel, Field


class Rhetoric(BaseModel):
    type: str
    passage: str
    explanation: str


class Source(BaseModel):
    url: str
    title: str
    date: str
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


class ArticleSource(BaseModel):
    id: int
    url: str
    title: str
    date: str
    bias: str

class ArticleQuote(BaseModel):
    text: str
    author: str
    date: str = ""


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
    quote: Optional[ArticleQuote] = None


class PipelineResult(BaseModel):
    id: str = Field(default_factory=lambda: uuid4().hex[:12])
    # Original input
    source_type: str
    source_url: str
    author: str
    date: str

    # Writer output
    title: str
    subtitle: Optional[str] = None
    verdict: str
    summary: str
    article: str
    format: str  # "short" or "long"
    language: str  # target language, e.g. "French" or "English"
    sources: list[ArticleSource]
    quote: Optional[ArticleQuote] = None
