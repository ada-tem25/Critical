"""
Normalizer module.
Transforms all text inputs (recording, instagram, raw text) into a unified format.
"""
from datetime import date
from typing import Optional
from pydantic import BaseModel


class NormalizedInput(BaseModel):
    text: str
    source_type: str  # "recording", "instagram", "text"
    source_url: str
    author: str
    date: str  # YYYY-MM-DD


def normalize(
    text: str,
    source_type: str,
    source_url: str = "",
    author: str = "",
    date_str: str = "",
) -> NormalizedInput:
    """
    Builds a NormalizedInput from any source.

    For instagram, date_str is expected in YYYYMMDD format (from yt-dlp).
    For recording and text, date defaults to today.
    """
    # Format the date
    if date_str:
        # Convert YYYYMMDD -> YYYY-MM-DD
        if len(date_str) == 8 and date_str.isdigit():
            formatted_date = f"{date_str[:4]}-{date_str[4:6]}-{date_str[6:8]}"
        else:
            formatted_date = date_str
    else:
        formatted_date = date.today().isoformat()

    result = NormalizedInput(
        text=text.strip(),
        source_type=source_type,
        source_url=source_url,
        author=author,
        date=formatted_date,
    )

    print(f"\n{'='*50}")
    print(f"[NORMALIZER] Source: {result.source_type}")
    print(f"[NORMALIZER] Author: {result.author or '(none)'}")
    print(f"[NORMALIZER] Date: {result.date}")
    print(f"[NORMALIZER] URL: {result.source_url or '(none)'}")
    print(f"[NORMALIZER] Text: {result.text}")
    print(f"{'='*50}\n")

    return result
