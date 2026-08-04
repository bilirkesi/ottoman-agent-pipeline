"""
API Server - FastAPI REST API with BYOK, MCP, and Workflow support
"""

import logging
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from datetime import datetime

# Import routers
from .byok_routes import router as byok_router
from .mcp_routes import router as mcp_router
from .workflow_routes import router as workflow_router
from .chat_routes import router as chat_router
from .transliterate_routes import router as transliterate_router

logger = logging.getLogger(__name__)


def create_app() -> FastAPI:
    """Create FastAPI application"""
    
    app = FastAPI(
        title="Ottoman Agent Pipeline",
        description="Uçtan uca Osmanlı Türkçesi transliterasyon ajan pipeline'ı",
        version="0.1.0",
        docs_url="/docs",
        redoc_url="/redoc"
    )
    
    # CORS
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    
    # Include routers
    app.include_router(byok_router)
    app.include_router(mcp_router)
    app.include_router(workflow_router)
    app.include_router(chat_router)
    app.include_router(transliterate_router)
    
    # Root endpoint
    @app.get("/")
    async def root():
        return {
            "service": "Ottoman Agent Pipeline",
            "version": "0.1.0",
            "description": "Uçtan uca Osmanlı Türkçesi transliterasyon ajan pipeline'ı",
            "docs": "/docs",
            "health": "/health"
        }
    
    # Health endpoint
    @app.get("/health")
    async def health_check():
        return {
            "status": "healthy",
            "timestamp": datetime.now().isoformat(),
            "version": "0.1.0"
        }
    
    return app
