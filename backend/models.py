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
    recommended_reading: list[RecommendedReading] = []


class PipelineResult(BaseModel):
    text: str
    source_type: str
    source_url: str
    author: str
    date: str
    rhetorics: list[Rhetoric]
    analyzed_claims: list[AnalyzedClaim]
    article: str
