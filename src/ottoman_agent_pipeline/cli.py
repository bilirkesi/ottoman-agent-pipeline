"""
CLI Interface
"""

from __future__ import annotations

import asyncio
import json
from pathlib import Path

import typer
from loguru import logger

from .core.config import get_config
from .core.orchestrator import AgentOrchestrator

app = typer.Typer(help="Ottoman Agent Pipeline CLI")
orchestrator: AgentOrchestrator | None = None


def get_orchestrator() -> AgentOrchestrator:
    """Get or create orchestrator instance."""
    global orchestrator
    if orchestrator is None:
        orchestrator = AgentOrchestrator()
        asyncio.run(orchestrator.initialize())
    return orchestrator


@app.command()
def chat(
    message: str = typer.Argument(..., help="Message to send"),
    model: str = typer.Option("deepseek-v4-flash", help="Model to use"),
    session: str | None = typer.Option(None, help="Session ID"),
    stream: bool = typer.Option(False, help="Stream response"),
    json_output: bool = typer.Option(False, help="Output as JSON"),
):
    """Chat with Ottoman Agent."""
    orch = get_orchestrator()

    if session:
        # Load existing session
        pass

    result = asyncio.run(orch.chat(message, model=model, stream=stream))

    if json_output:
        print(result.to_json())
    else:
        print(f"\n{result.output}")
        print(f"\nModel: {result.model_used}")
        print(f"Tokens: {result.tokens_used}")
        print(f"Latency: {result.latency_ms:.1f}ms")


@app.command()
def translate(
    text: str = typer.Argument(..., help="Ottoman Turkish text"),
    mode: str = typer.Option("hybrid", help="Transliteration mode"),
    model: str = typer.Option("deepseek-v4-flash", help="Model to use"),
    json_output: bool = typer.Option(False, help="Output as JSON"),
):
    """Transliterate Ottoman Turkish text."""
    orch = get_orchestrator()

    result = asyncio.run(orch.translate(text, mode=mode, model=model))

    if json_output:
        print(result.to_json())
    else:
        print(f"\n{result.output}")


@app.command()
def analyze(
    text: str = typer.Argument(..., help="Text to analyze"),
    entities: bool = typer.Option(True, help="Extract entities"),
    pos: bool = typer.Option(False, help="POS tagging"),
    json_output: bool = typer.Option(False, help="Output as JSON"),
):
    """Analyze Ottoman Turkish text."""
    orch = get_orchestrator()

    result = asyncio.run(orch.analyze(text, entities=entities, pos=pos))

    if json_output:
        print(result.to_json())
    else:
        print(f"\n{result.output}")


@app.command()
def serve(
    host: str = typer.Option("0.0.0.0", help="Host to bind"),
    port: int = typer.Option(8000, help="Port to bind"),
    reload: bool = typer.Option(False, help="Enable reload"),
):
    """Start API server."""
    import uvicorn

    logger.info(f"Starting server at {host}:{port}")

    uvicorn.run(
        "ottoman_agent_pipeline.api.server:create_app",
        host=host,
        port=port,
        reload=reload,
        factory=True,
    )


@app.command()
def info():
    """Show agent information."""
    orch = get_orchestrator()
    status = orch.get_status()

    print("\n=== Ottoman Agent Pipeline ===")
    print(f"Version: {status['config'].get('agent', {}).get('version', '0.1.0')}")
    print(f"Session: {status['session_id']}")
    print(f"Tools: {', '.join(status['tools'])}")
    print(f"Models: {', '.join(status['models'])}")
    print(f"Messages: {status['session_messages']}")
    print()


@app.command()
def init():
    """Initialize agent configuration."""
    from .core.config import ConfigManager

    config_path = ConfigManager.DEFAULT_CONFIG_PATH
    config_path.parent.mkdir(parents=True, exist_ok=True)

    if config_path.exists():
        logger.info(f"Config already exists: {config_path}")
    else:
        manager = ConfigManager(config_path)
        manager.save(get_config())
        logger.info(f"Config created: {config_path}")

    logger.info("Run 'ottoman-agent info' to see configuration")


@app.callback()
def main(
    verbose: bool = typer.Option(
        False, "--verbose", "-v", help="Enable verbose logging"
    ),
    config: Path | None = typer.Option(None, "--config", "-c", help="Config file path"),
):
    """Ottoman Agent Pipeline - Uçtan uca Osmanlı Türkçesi transliterasyon sistemi."""
    if verbose:
        logger.enable("ottoman_agent_pipeline")

    if config:
        from .core.config import _config_manager

        _config_manager.config_path = config


@app.command()
def agents():
    """Agent takımı durumu"""
    from .agents import get_agent_team

    team = get_agent_team()
    status = team.get_status()

    print("\n=== Agent Takımı Durumu ===")
    for name in status["agents"]:
        print(f"  {name}: ready")
    print(f"\nCompleted: {status['tasks_completed']}")
    print(f"Failed: {status['tasks_failed']}")


@app.command()
def pipeline(type: str = typer.Option("default", "--type", "-t", help="Pipeline tipi")):
    """Tam pipeline çalıştır"""
    from .agents import run_full_pipeline

    logger.info(f"Running pipeline: {type}")
    result = asyncio.run(run_full_pipeline())

    print(json.dumps(result, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    app()
