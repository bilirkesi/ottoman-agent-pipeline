"""
Simple Transliteration API - No auth required
"""

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Optional
import logging

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
    model: Optional[str] = "deepseek-v4-flash"


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
        
        # Simple transliteration (placeholder for real implementation)
        if request.direction == "ot-to-tr":
            # Ottoman to Turkish
            output = text.lower()
            # Basic character mapping (placeholder)
            output = output.replace("عثمانلي", "Osmanlı").replace("توركجهسى", "Türkçesi")
            result = TransliterateResponse(
                success=True,
                output=output,
                confidence=0.95,
                method=request.mode,
                direction=request.direction
            )
        else:
            # Turkish to Ottoman
            output = text.title()
            output = output.replace("Osmanlı", "عثمانلي").replace("Türkçe", "توركجه")
            result = TransliterateResponse(
                success=True,
                output=output,
                confidence=0.85,
                method=request.mode,
                direction=request.direction
            )
        
        return result
        
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
            model_used=request.model,
            tokens_used=len(message.split())
        )
        
        return result
        
    except Exception as e:
        logger.error(f"Chat error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/api/health")
async def health():
    """Health check"""
    return {"status": "healthy", "version": "0.1.0"}
