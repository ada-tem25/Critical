"""
Dev endpoint to inject claims directly into the Orchestrator, bypassing the Decomposer.
Saves LLM credits when testing the downstream pipeline.
"""
import time
from typing import Any
from fastapi import APIRouter
from pydantic import BaseModel
from models import Claim
from orchestrator import orchestrate

router = APIRouter()


class InjectClaimsRequest(BaseModel):
    claims: list[Claim]
    mode: str = "eco"


class InjectClaimsResponse(BaseModel):
    status: str
    message: str
    analyzed_claims: list[dict[str, Any]]


@router.post("/api/inject-claims", response_model=InjectClaimsResponse)
async def inject_claims(request: InjectClaimsRequest):
    if not request.claims:
        return InjectClaimsResponse(
            status="error",
            message="La liste de claims est vide.",
            analyzed_claims=[],
        )

    print(f"\n[INJECT] {len(request.claims)} claims reçus:")
    for c in request.claims:
        print(f"  #{c.id} [{c.verifiability}/{c.type}] ({c.role}) {c.idea}")
        if c.supports:
            print(f"       supports: {c.supports}")

    t0 = time.perf_counter()
    analyzed = await orchestrate(request.claims)
    duration = time.perf_counter() - t0

    return InjectClaimsResponse(
        status="ok",
        message=f"{len(analyzed)} claims analysés en {duration:.2f}s",
        analyzed_claims=[ac.model_dump() for ac in analyzed],
    )
