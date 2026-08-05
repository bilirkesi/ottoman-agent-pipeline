"""
Transliteration API Routes

Real transliteration via TranslationTool (ottoman-transliterator engine
with rule-based fallback when no API key is configured).
"""

from __future__ import annotations

import logging
import time

from fastapi import APIRouter, Body, HTTPException
from pydantic import BaseModel

from ..tools.translation import get_translation_tool

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/v1", tags=["Transliteration"])


class TransliterateRequest(BaseModel):
    text: str
    mode: str = "hybrid"  # hybrid, neural, nlp
    direction: str = "ot-to-tr"  # ot-to-tr, tr-to-ot


class TransliterateResponse(BaseModel):
    success: bool
    output: str | None = None
    modern_turkish: str | None = None
    osmanlica: str | None = None
    confidence: float | None = None
    method: str | None = None
    chunks: int | None = None
    latency_ms: float | None = None
    error: str | None = None


@router.post("/transliterate", response_model=TransliterateResponse)
async def transliterate(request: dict = Body(...)):
    """
    Transliterate Ottoman Turkish text

    - **text**: Input text
    - **mode**: Transliteration mode (hybrid/neural/nlp)
    - **direction**: Translation direction (ot-to-tr/tr-to-ot)
    """
    start = time.perf_counter()
    try:
        text = (request.get("text") or "").strip()
        mode = request.get("mode", "hybrid")
        direction = request.get("direction", "ot-to-tr")

        if not text:
            raise HTTPException(status_code=400, detail="Text is required")

        tool = get_translation_tool()
        if tool._transliterator is None:
            await tool.initialize()

        if direction == "tr-to-ot":
            result = await tool.execute(action="reverse", text=text)
            latency_ms = round((time.perf_counter() - start) * 1000, 1)
            return TransliterateResponse(
                success=True,
                output=result.get("ottoman"),
                osmanlica=result.get("ottoman"),
                confidence=result.get("confidence"),
                method=result.get("method"),
                chunks=1,
                latency_ms=latency_ms,
            )

        result = await tool.execute(action="transliterate", text=text, mode=mode)
        latency_ms = round((time.perf_counter() - start) * 1000, 1)

        if "error" in result and result.get("modern_turkish") is None:
            return TransliterateResponse(
                success=False,
                error=str(result.get("error")),
                latency_ms=latency_ms,
            )

        return TransliterateResponse(
            success=True,
            output=result.get("modern_turkish"),
            modern_turkish=result.get("modern_turkish"),
            confidence=result.get("confidence"),
            method=result.get("method"),
            chunks=len(str(result.get("ottoman", "")).split("\n")),
            latency_ms=latency_ms,
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Transliteration error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/transliterate/direction")
async def detect_direction(text: str):
    """
    Detect translation direction based on text
    """
    has_arabic = any("\u0600" <= c <= "\u06ff" for c in text)
    return {
        "direction": "ot-to-tr" if has_arabic else "tr-to-ot",
        "has_arabic_script": has_arabic,
    }
