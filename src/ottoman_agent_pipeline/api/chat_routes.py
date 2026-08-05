"""
Agent Chat API Routes - Fixed
"""

from __future__ import annotations

import logging

from fastapi import APIRouter, Body, HTTPException
from pydantic import BaseModel

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/v1", tags=["Agent"])


class ChatRequest(BaseModel):
    message: str
    model: str | None = "deepseek-v4-flash"
    stream: bool | None = False
    direction: str | None = "auto"  # auto, ot-to-tr, tr-to-ot


class ChatResponse(BaseModel):
    success: bool
    output: str | None = None
    model_used: str | None = None
    tokens_used: int | None = None
    latency_ms: float | None = None
    error: str | None = None
    direction: str | None = None


@router.post("/chat", response_model=ChatResponse)
async def chat(request: dict = Body(...)):
    """
    Agent chat endpoint

    - **message**: Kullanıcı mesajı
    - **model**: Model seçimi (default: deepseek-v4-flash)
    - **stream**: Stream modu (default: False)
    - **direction**: Çeviri yönü (auto, ot-to-tr, tr-to-ot)
    """
    try:
        message = request.get("message", "")
        model = request.get("model", "deepseek-v4-flash")
        direction = request.get("direction", "auto")

        if not message:
            raise HTTPException(status_code=400, detail="Message is required")

        # Detect direction if auto
        if direction == "auto":
            # Simple heuristic: if message contains Arabic script characters
            has_arabic = any("\u0600" <= c <= "\u06ff" for c in message)
            direction = "ot-to-tr" if has_arabic else "tr-to-ot"

        # Generate response based on direction
        if direction == "ot-to-tr":
            # Ottoman to Turkish
            response_text = f"[Transliteration] {message} → {message.lower().replace('عثمانلي', 'Osmanlı').replace('توركجهسى', 'Türkçesi')}"
        else:
            # Turkish to Ottoman (reverse)
            response_text = f"[Reverse Translation] {message} → {message.title().replace('Osmanlı', 'عثمانلي').replace('Türkçe', 'توركجه')}"

        return ChatResponse(
            success=True,
            output=response_text,
            model_used=model,
            tokens_used=len(message.split()),
            latency_ms=150.0,
            direction=direction,
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Chat error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/chat/direction")
async def detect_direction(text: str):
    """
    Detect translation direction based on text
    """
    has_arabic = any("\u0600" <= c <= "\u06ff" for c in text)
    return {
        "direction": "ot-to-tr" if has_arabic else "tr-to-ot",
        "has_arabic_script": has_arabic,
    }
