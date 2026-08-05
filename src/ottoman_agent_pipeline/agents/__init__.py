"""
Agent Takımı - Osmanlica Projesi için otomatik agent koordinasyonu
"""

from __future__ import annotations

import asyncio
import json
import logging
from dataclasses import dataclass
from datetime import datetime
from typing import Any

from .team import AgentBus, AgentMessage

logger = logging.getLogger(__name__)


@dataclass
class AgentTask:
    """Agent görev tanımı"""

    name: str
    agent: str  # code_agent, test_agent, deploy_agent, etc.
    payload: dict[str, Any]
    status: str = "pending"
    result: dict | None = None
    error: str | None = None
    started_at: str | None = None
    completed_at: str | None = None


class AgentTeam:
    """
    Agent takımı - Proje koordinasyonu

    Agent'lar:
    - CodeAgent: Kod yazma ve refactoring
    - TestAgent: Test yazma ve çalıştırma
    - DeployAgent: CI/CD ve deployment
    - ResearchAgent: Araştırma ve benchmark
    - DocsAgent: Dokümantasyon
    """

    def __init__(self):
        self.agents: dict[str, Any] = {}
        self.tasks: list[AgentTask] = []
        self.results: dict[str, Any] = {}
        self._initialize_agents()

    def _initialize_agents(self):
        """Agent'ları başlat"""
        # Import agents
        from .team import (
            CodeAgent,
            DeployAgent,
            DocsAgent,
            ResearchAgent,
            TestAgent,
        )

        # Create agents (shared bus wiring)
        self.bus = AgentBus()
        self.agents = {
            "code_agent": CodeAgent(self.bus),
            "test_agent": TestAgent(self.bus),
            "deploy_agent": DeployAgent(self.bus),
            "research_agent": ResearchAgent(self.bus),
            "docs_agent": DocsAgent(self.bus),
        }

        logger.info(f"Initialized {len(self.agents)} agents")

    async def run_task(self, task: AgentTask) -> AgentTask:
        """Tek görev çalıştır"""
        task.status = "running"
        task.started_at = datetime.now().isoformat()

        logger.info(f"Running task: {task.name} on {task.agent}")

        try:
            agent = self.agents.get(task.agent)
            if not agent:
                raise ValueError(f"Agent not found: {task.agent}")

            # Execute agent method
            method_name = f"handle_{task.payload.get('action', 'default')}"
            if hasattr(agent, method_name):
                result = await getattr(agent, method_name)(task.payload)
            else:
                result = await agent.handle(
                    AgentMessage(
                        sender="team",
                        receiver=task.agent,
                        msg_type="request",
                        payload=task.payload,
                    )
                )

            task.result = result
            task.status = "completed"
            task.completed_at = datetime.now().isoformat()

            logger.info(f"Task completed: {task.name}")

        except Exception as e:
            task.status = "failed"
            task.error = str(e)
            task.completed_at = datetime.now().isoformat()
            logger.error(f"Task failed: {task.name} - {e}")

        return task

    async def run_pipeline(self, tasks: list[dict[str, Any]]) -> dict[str, Any]:
        """Pipeline çalıştır"""
        logger.info(f"Running pipeline with {len(tasks)} tasks")

        results = []
        for task_config in tasks:
            task = AgentTask(
                name=task_config.get("name", "unnamed"),
                agent=task_config.get("agent", "code_agent"),
                payload=task_config.get("payload", {}),
            )

            result = await self.run_task(task)
            results.append(result)

            # Stop on failure
            if result.status == "failed":
                logger.error(f"Pipeline stopped at task: {task.name}")
                break

        return {
            "status": (
                "success" if all(r.status == "completed" for r in results) else "failed"
            ),
            "total_tasks": len(results),
            "completed_tasks": sum(1 for r in results if r.status == "completed"),
            "failed_tasks": sum(1 for r in results if r.status == "failed"),
            "results": [
                {
                    "name": r.name,
                    "status": r.status,
                    "result": r.result,
                    "error": r.error,
                    "started_at": r.started_at,
                    "completed_at": r.completed_at,
                }
                for r in results
            ],
        }

    def get_status(self) -> dict[str, Any]:
        """Agent durumu"""
        return {
            "agents": {
                name: {"status": "ready" if hasattr(agent, "status") else "unknown"}
                for name, agent in self.agents.items()
            },
            "tasks_completed": len([t for t in self.tasks if t.status == "completed"]),
            "tasks_failed": len([t for t in self.tasks if t.status == "failed"]),
        }

    async def implement(
        self, name: str, path: str, template: str = "default"
    ) -> AgentTask:
        """Kod implement et"""
        task = AgentTask(
            name=f"Implement {name}",
            agent="code_agent",
            payload={
                "action": "implement",
                "name": name,
                "path": path,
                "template": template,
            },
        )
        return await self.run_task(task)

    async def test(self, path: str, test_path: str) -> AgentTask:
        """Test çalıştır"""
        task = AgentTask(
            name="Run tests",
            agent="test_agent",
            payload={"action": "test", "path": path, "test_path": test_path},
        )
        return await self.run_task(task)

    async def deploy(self, version: str) -> AgentTask:
        """Deploy et"""
        task = AgentTask(
            name="Deploy",
            agent="deploy_agent",
            payload={"action": "deploy", "version": version},
        )
        return await self.run_task(task)

    async def research(self, topic: str) -> AgentTask:
        """Araştırma yap"""
        task = AgentTask(
            name=f"Research: {topic}",
            agent="research_agent",
            payload={"action": "research", "topic": topic},
        )
        return await self.run_task(task)

    async def document(self, project: str) -> AgentTask:
        """Dokümantasyon oluştur"""
        task = AgentTask(
            name=f"Document: {project}",
            agent="docs_agent",
            payload={"action": "document", "project": project},
        )
        return await self.run_task(task)


# Singleton
_team = None


def get_agent_team() -> AgentTeam:
    """Global agent takımı instance'ı"""
    global _team
    if _team is None:
        _team = AgentTeam()
    return _team


async def run_full_pipeline():
    """Tam pipeline çalıştır"""
    team = get_agent_team()

    pipeline = [
        {
            "name": "Implement Transliterator",
            "agent": "code_agent",
            "payload": {
                "action": "implement",
                "name": "ottoman_transliterator",
                "path": "src/ottoman_transliterator/pipeline.py",
                "template": "default",
            },
        },
        {
            "name": "Run Tests",
            "agent": "test_agent",
            "payload": {
                "action": "test",
                "path": "tests/",
                "test_path": "tests/test_pipeline.py",
            },
        },
        {
            "name": "Document Project",
            "agent": "docs_agent",
            "payload": {"action": "document", "project": "ottoman-agent-pipeline"},
        },
        {
            "name": "Deploy",
            "agent": "deploy_agent",
            "payload": {"action": "deploy", "version": "0.1.0"},
        },
    ]

    result = await team.run_pipeline(pipeline)
    return result


if __name__ == "__main__":
    result = asyncio.run(run_full_pipeline())
    print(json.dumps(result, indent=2, ensure_ascii=False))
