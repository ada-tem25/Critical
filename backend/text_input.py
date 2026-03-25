"""
Text input endpoint.
Receives raw text from the frontend for processing.
"""
from fastapi import APIRouter
from pydantic import BaseModel
from normalizer import normalize

router = APIRouter()


class TextInputRequest(BaseModel):
    text: str


class TextInputResponse(BaseModel):
    status: str
    text: str
    message: str


@router.post("/api/text", response_model=TextInputResponse)
async def receive_text(request: TextInputRequest):
    text = request.text.strip()

    if not text:
        return TextInputResponse(
            status="error",
            text="",
            message="Le texte est vide."
        )

    normalize(text=text, source_type="text")

    return TextInputResponse(
        status="ok",
        text=text,
        message=f"Texte recu ({len(text)} caracteres)"
    )
