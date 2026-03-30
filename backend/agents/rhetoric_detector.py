"""
Rhetoric detector agent — detects manipulative rhetorical devices.
"""
from normalizer import NormalizedInput
from models import Rhetoric


async def detect_rhetorics(normalized: NormalizedInput) -> list[Rhetoric]:
    """LLM agent. Detects manipulative rhetorical devices from a bank of ~20 known biases."""
    # TODO: implement
    return []
