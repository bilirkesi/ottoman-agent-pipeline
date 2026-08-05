"""
Simple Transliteration API - No auth required

End-user friendly endpoints backed by the real TranslationTool
(ottoman-transliterator engine with rule-based fallback).
"""

from __future__ import annotations

import logging

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from ..tools.translation import get_translation_tool

logger = logging.getLogger(__name__)

router = APIRouter()


class TransliterateRequest(BaseModel):
    text: str
    mode: str = "hybrid"
    direction: str = "ot-to-tr"


class TransliterateResponse(BaseModel):
    success: bool
    output: str
    confidence: float
    method: str
    direction: str


class ChatRequest(BaseModel):
    message: str
    model: str | None = "deepseek-v4-flash"


class ChatResponse(BaseModel):
    success: bool
    output: str
    model_used: str
    tokens_used: int


@router.post("/api/transliterate", response_model=TransliterateResponse)
async def transliterate(request: TransliterateRequest):
    """Transliterate Ottoman Turkish text"""
    try:
        text = request.text.strip()
        if not text:
            raise HTTPException(status_code=400, detail="Text is required")

        tool = get_translation_tool()
        if tool._transliterator is None:
            await tool.initialize()

        if request.direction == "tr-to-ot":
            result = await tool.execute(action="reverse", text=text)
            return TransliterateResponse(
                success=True,
                output=result.get("ottoman", text),
                confidence=float(result.get("confidence", 0.5)),
                method=result.get("method", "reverse_mapping"),
                direction=request.direction,
            )

        result = await tool.execute(
            action="transliterate", text=text, mode=request.mode
        )
        return TransliterateResponse(
            success=True,
            output=result.get("modern_turkish", text),
            confidence=float(result.get("confidence", 0.5)),
            method=result.get("method", "fallback"),
            direction=request.direction,
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Transliteration error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/api/chat", response_model=ChatResponse)
async def chat(request: ChatRequest):
    """Chat with agent"""
    try:
        message = request.message.strip()
        if not message:
            raise HTTPException(status_code=400, detail="Message is required")

        # Simple response (placeholder)
        response_text = f"Osmanlica Agent response to: {message}"

        result = ChatResponse(
            success=True,
            output=response_text,
            model_used=request.model or "deepseek-v4-flash",
            tokens_used=len(message.split()),
        )

        return result

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Chat error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/api/health")
async def health():
    """Health check"""
    return {"status": "healthy", "version": "0.1.0"}
