"""
Simple API Server - User-friendly endpoints
"""

import logging
from datetime import datetime

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

# Import simple routes
from .simple_routes import router as simple_router

logger = logging.getLogger(__name__)


def create_simple_app() -> FastAPI:
    """Create simple FastAPI application for end users"""

    app = FastAPI(
        title="Ottoman Agent - Simple API",
        description="End-user friendly API for Ottoman Turkish transliteration",
        version="0.1.0",
    )

    # CORS
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # Include simple routes
    app.include_router(simple_router)

    # Root endpoint
    @app.get("/")
    async def root():
        return {
            "service": "Ottoman Agent",
            "version": "0.1.0",
            "endpoints": {
                "transliterate": "/api/transliterate",
                "chat": "/api/chat",
                "health": "/api/health",
            },
        }

    # Health endpoint
    @app.get("/health")
    async def health_check():
        return {
            "status": "healthy",
            "timestamp": datetime.now().isoformat(),
            "version": "0.1.0",
        }

    return app
