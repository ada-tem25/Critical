"""
Dev endpoint to inject claims directly, bypassing the Decomposer and Rhetoric Detector.
Runs the full pipeline (Orchestrator → Writer → metrics → cost) with pre-made claims.
"""
from fastapi import APIRouter
from pydantic import BaseModel
from normalizer import NormalizedInput
from models import Claim
from main_pipeline import run_pipeline

router = APIRouter()


class InjectClaimsRequest(BaseModel):
    text: str
    claims: list[Claim]
    mode: str = "eco"


@router.post("/api/inject-claims")
async def inject_claims(request: InjectClaimsRequest):
    if not request.claims:
        return {"status": "error", "message": "La liste de claims est vide."}

    normalized = NormalizedInput(
        text=request.text,
        source_type="injected",
        source_url="",
        author="",
        date="",
    )

    print(f"\n[INJECT] {len(request.claims)} claims injectés:")
    for c in request.claims:
        print(f"  #{c.id} [{c.verifiability}/{c.type}] ({c.role}) {c.idea}")

    result = await run_pipeline(normalized, mode=request.mode, injected_claims=request.claims)

    return {
        "status": "ok",
        "message": f"{len(result.analyzed_claims)} claims analysés",
        "result": result.model_dump(),
    }
