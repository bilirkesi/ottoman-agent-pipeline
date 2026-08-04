"""
Agent CLI Commands
"""

import asyncio
import json
import typer
from typing import Optional
from loguru import logger

from .team import (
    ProjectOrchestrator,
    CodeAgent,
    TestAgent,
    DeployAgent,
    ResearchAgent,
    DocsAgent,
    get_orchestrator
)

app = typer.Typer(help="Agent Takımı CLI")


@app.command()
def status():
    """Agent takımı durumunu göster"""
    orch = get_orchestrator()
    status = orch.get_status()
    
    print("\n=== Agent Takımı Durumu ===")
    for name, agent_status in status["agents"].items():
        print(f"  {name}: {agent_status}")
    print(f"\nTamamlanan task'lar: {status['tasks_completed']}")
    print()


@app.command()
def implement(
    name: str = typer.Argument(..., help="Implement edilecek modül adı"),
    path: str = typer.Option("src/", help="Hedef dosya yolu"),
    template: str = typer.Option("default", help="Kod şablonu")
):
    """Kod implement et"""
    orch = get_orchestrator()
    
    task = {
        "name": f"Implement {name}",
        "agent": "code_agent",
        "payload": {
            "action": "implement",
            "name": name,
            "path": path,
            "template": template
        }
    }
    
    logger.info(f"Implementing: {name}")
    result = asyncio.run(orch.run_task(task))
    
    print(json.dumps(result, indent=2, ensure_ascii=False))


@app.command()
def test(
    path: str = typer.Option("tests/", help="Test dizini"),
    test_path: str = typer.Option("tests/test_pipeline.py", help="Test dosyası")
):
    """Test çalıştır"""
    orch = get_orchestrator()
    
    task = {
        "name": "Run tests",
        "agent": "test_agent",
        "payload": {
            "action": "test",
            "path": path,
            "test_path": test_path
        }
    }
    
    logger.info("Running tests")
    result = asyncio.run(orch.run_task(task))
    
    print(json.dumps(result, indent=2, ensure_ascii=False))


@app.command()
def deploy(
    version: str = typer.Option("0.1.0", help="Sürüm numarası")
):
    """Deploy et"""
    orch = get_orchestrator()
    
    task = {
        "name": "Deploy",
        "agent": "deploy_agent",
        "payload": {
            "action": "deploy",
            "version": version
        }
    }
    
    logger.info(f"Deploying version: {version}")
    result = asyncio.run(orch.run_task(task))
    
    print(json.dumps(result, indent=2, ensure_ascii=False))


@app.command()
def research(
    topic: str = typer.Argument(..., help="Araştırma konusu")
):
    """Araştırma yap"""
    orch = get_orchestrator()
    
    task = {
        "name": f"Research: {topic}",
        "agent": "research_agent",
        "payload": {
            "action": "research",
            "topic": topic
        }
    }
    
    logger.info(f"Researching: {topic}")
    result = asyncio.run(orch.run_task(task))
    
    print(json.dumps(result, indent=2, ensure_ascii=False))


@app.command()
def document(
    project: str = typer.Option("ottoman-agent-pipeline", help="Proje adı")
):
    """Dokümantasyon oluştur"""
    orch = get_orchestrator()
    
    task = {
        "name": f"Document: {project}",
        "agent": "docs_agent",
        "payload": {
            "action": "document",
            "project": project
        }
    }
    
    logger.info(f"Documenting: {project}")
    result = asyncio.run(orch.run_task(task))
    
    print(json.dumps(result, indent=2, ensure_ascii=False))


@app.command()
def pipeline(
    tasks: str = typer.Option("default", help="Pipeline tipi (default, full, ci)")
):
    """Pipeline çalıştır"""
    orch = get_orchestrator()
    
    # Default pipeline
    if tasks == "default":
        pipeline = [
            {
                "name": "Implement",
                "agent": "code_agent",
                "payload": {"action": "implement", "name": "example", "path": "src/", "template": "default"}
            },
            {
                "name": "Test",
                "agent": "test_agent",
                "payload": {"action": "test", "path": "tests/", "test_path": "tests/test_pipeline.py"}
            },
            {
                "name": "Deploy",
                "agent": "deploy_agent",
                "payload": {"action": "deploy", "version": "0.1.0"}
            }
        ]
    elif tasks == "full":
        pipeline = [
            {"name": "Research", "agent": "research_agent", "payload": {"action": "research", "topic": "Ottoman NLP"}},
            {"name": "Implement", "agent": "code_agent", "payload": {"action": "implement", "name": "full", "path": "src/", "template": "full"}},
            {"name": "Test", "agent": "test_agent", "payload": {"action": "test", "path": "tests/", "test_path": "tests/test_pipeline.py"}},
            {"name": "Document", "agent": "docs_agent", "payload": {"action": "document", "project": "ottoman-agent-pipeline"}},
            {"name": "Deploy", "agent": "deploy_agent", "payload": {"action": "deploy", "version": "0.1.0"}}
        ]
    else:
        pipeline = []
    
    logger.info(f"Running pipeline: {tasks}")
    result = asyncio.run(orch.run_pipeline(pipeline))
    
    print(json.dumps(result, indent=2, ensure_ascii=False))


@app.command()
def list_agents():
    """Kayıtlı agent'ları listele"""
    orch = get_orchestrator()
    
    print("\n=== Kayıtlı Agent'lar ===")
    for name, agent in orch.agents.items():
        tools = getattr(agent, 'tools', [])
        print(f"\n{name}:")
        print(f"  Status: {agent.status}")
        print(f"  Tools: {', '.join(tools)}")
    print()


if __name__ == "__main__":
    app()
