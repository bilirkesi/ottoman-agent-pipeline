"""
Agent Chat API Routes
"""

from fastapi import APIRouter, HTTPException, Body
from pydantic import BaseModel
from typing import Dict, Any, Optional
import logging

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/v1", tags=["Agent"])


class ChatRequest(BaseModel):
    message: str
    model: Optional[str] = "deepseek-v4-flash"
    stream: Optional[bool] = False


class ChatResponse(BaseModel):
    success: bool
    output: Optional[str] = None
    model_used: Optional[str] = None
    tokens_used: Optional[int] = None
    latency_ms: Optional[float] = None
    error: Optional[str] = None


@router.post("/chat", response_model=ChatResponse)
async def chat(request: dict = Body(...)):
    """
    Agent chat endpoint
    
    - **message**: Kullanıcı mesajı
    - **model**: Model seçimi (default: deepseek-v4-flash)
    - **stream**: Stream modu (default: False)
    """
    try:
        message = request.get("message", "")
        model = request.get("model", "deepseek-v4-flash")
        
        if not message:
            raise HTTPException(status_code=400, detail="Message is required")
        
        # Simulated response (actual implementation needs API keys)
        response_text = f"Osmanlica Agent response to: {message}"
        
        return ChatResponse(
            success=True,
            output=response_text,
            model_used=model,
            tokens_used=len(message.split()),
            latency_ms=150.0
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Chat error: {e}")
        raise HTTPException(status_code=500, detail=str(e))
