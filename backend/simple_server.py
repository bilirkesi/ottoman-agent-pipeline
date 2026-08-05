"""
Simple Backend Server - For end users
"""

import os
import sys

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))

import uvicorn

from ottoman_agent_pipeline.api.simple_server import create_simple_app

if __name__ == "__main__":
    app = create_simple_app()
    uvicorn.run(app, host="0.0.0.0", port=8001)
