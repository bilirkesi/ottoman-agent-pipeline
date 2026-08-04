"""
API Server - FastAPI REST API
"""

import logging
from contextlib import asynccontextmanager
from datetime import datetime
from typing import Any, Dict, List, Optional

from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field

from .core.orchestrator import AgentOrchestrator, AgentResponse
from .core.config import get_config

logger = logging.getLogger(__name__)


class TransliterateRequest(BaseModel):
    """Request for transliteration."""
    
    text: str = Field(..., description="Ottoman Turkish text")
    mode: str = Field("hybrid", description="Transliteration mode")
    model: Optional[str] = None


class TransliterateResponse(BaseModel):
    """Response for transliteration."""
    
    ottoman: str
    modern_turkish: str
    confidence: float
    method: str
    uncertain_spans: List[List[Any]] = Field(default_factory=list)


class ChatRequest(BaseModel):
    """Request for chat."""
    
    message: str = Field(..., description="User message")
    model: Optional[str] = None
    stream: bool = Field(False, description="Stream response")
    session_id: Optional[str] = None


class ChatResponse(BaseModel):
    """Response for chat."""
    
    success: bool
    output: str
    model_used: str
    tokens_used: int
    latency_ms: float
    error: Optional[str] = None


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan."""
    # Startup
    logger.info("Starting Ottoman Agent Pipeline API...")
    app.state.orchestrator = AgentOrchestrator()
    await app.state.orchestrator.initialize()
    yield
    # Shutdown
    await app.state.orchestrator.close()
    logger.info("Ottoman Agent Pipeline API stopped")


def create_app() -> FastAPI:
    """Create FastAPI application."""
    
    app = FastAPI(
        title="Ottoman Agent Pipeline",
        description="Uçtan uca Osmanlı Türkçesi transliterasyon ajan pipeline'ı",
        version="0.1.0",
        lifespan=lifespan
    )
    
    # CORS
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    
    @app.get("/health")
    async def health_check():
        """Health check endpoint."""
        return {
            "status": "healthy",
            "timestamp": datetime.now().isoformat(),
            "version": "0.1.0"
        }
    
    @app.post("/api/v1/transliterate", response_model=TransliterateResponse)
    async def transliterate(request: TransliterateRequest):
        """Transliterate Ottoman Turkish text."""
        orchestrator: AgentOrchestrator = app.state.orchestrator
        
        try:
            result = await orchestrator.translate(
                text=request.text,
                mode=request.mode,
                model=request.model
            )
            
            if not result.success:
                raise HTTPException(status_code=500, detail=result.error)
            
            # Parse result
            try:
                import json
                data = json.loads(result.output)
                return TransliterateResponse(
                    ottoman=request.text,
                    modern_turkish=data.get("modern_turkish", ""),
                    confidence=data.get("confidence", 0.0),
                    method=data.get("method", "unknown"),
                    uncertain_spans=data.get("uncertain_spans", [])
                )
            except:
                return TransliterateResponse(
                    ottoman=request.text,
                    modern_turkish=result.output,
                    confidence=0.85,
                    method=request.mode
                )
                
        except Exception as e:
            logger.error(f"Transliteration error: {e}")
            raise HTTPException(status_code=500, detail=str(e))
    
    @app.post("/api/v1/chat", response_model=ChatResponse)
    async def chat(request: ChatRequest):
        """Chat with agent."""
        orchestrator: AgentOrchestrator = app.state.orchestrator
        
        try:
            if request.stream:
                # Stream response (not implemented in this version)
                raise HTTPException(status_code=501, detail="Streaming not implemented")
            
            result = await orchestrator.chat(
                message=request.message,
                model=request.model
            )
            
            return ChatResponse(
                success=result.success,
                output=result.output,
                model_used=result.model_used,
                tokens_used=result.tokens_used,
                latency_ms=result.latency_ms,
                error=result.error
            )
            
        except Exception as e:
            logger.error(f"Chat error: {e}")
            raise HTTPException(status_code=500, detail=str(e))
    
    @app.get("/api/v1/sessions/{session_id}")
    async def get_session(session_id: str):
        """Get session info."""
        orchestrator: AgentOrchestrator = app.state.orchestrator
        
        # Find session
        if hasattr(orchestrator, 'sessions'):
            if session_id in orchestrator.sessions:
                return orchestrator.sessions[session_id].get_stats()
        
        return {"error": "Session not found"}
    
    @app.get("/api/v1/status")
    async def get_status():
        """Get agent status."""
        orchestrator: AgentOrchestrator = app.state.orchestrator
        return orchestrator.get_status()
    
    @app.post("/api/v1/sessions/reset")
    async def reset_session():
        """Reset current session."""
        orchestrator: AgentOrchestrator = app.state.orchestrator
        orchestrator.reset_session()
        return {"status": "reset"}
    
    return app
