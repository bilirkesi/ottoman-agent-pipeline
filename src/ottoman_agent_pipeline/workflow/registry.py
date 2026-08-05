"""
Visual Workflow Editor - Ottoman Agent Pipeline için workflow yönetimi
"""

from __future__ import annotations

import json
import logging
import uuid
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
from typing import Any, ClassVar

import networkx as nx

logger = logging.getLogger(__name__)


@dataclass
class WorkflowNode:
    """Workflow düğümü"""

    node_id: str
    type: str
    name: str
    config: dict[str, Any] = field(default_factory=dict)
    position: tuple[int, int] = (0, 0)
    metadata: dict[str, Any] = field(default_factory=dict)
    created_at: datetime = field(default_factory=datetime.now)
    updated_at: datetime = field(default_factory=datetime.now)

    def to_dict(self) -> dict:
        return {
            "node_id": self.node_id,
            "type": self.type,
            "name": self.name,
            "config": self.config,
            "position": list(self.position),
            "metadata": self.metadata,
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat(),
        }

    @classmethod
    def from_dict(cls, data: dict) -> WorkflowNode:
        return cls(
            node_id=data["node_id"],
            type=data["type"],
            name=data["name"],
            config=data.get("config", {}),
            position=tuple(data.get("position", [0, 0])),
            metadata=data.get("metadata", {}),
            created_at=(
                datetime.fromisoformat(data["created_at"])
                if data.get("created_at")
                else datetime.now()
            ),
            updated_at=(
                datetime.fromisoformat(data["updated_at"])
                if data.get("updated_at")
                else datetime.now()
            ),
        )


@dataclass
class WorkflowEdge:
    """Workflow kenarı"""

    edge_id: str
    source_node_id: str
    target_node_id: str
    condition: str | None = None
    metadata: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict:
        return {
            "edge_id": self.edge_id,
            "source_node_id": self.source_node_id,
            "target_node_id": self.target_node_id,
            "condition": self.condition,
            "metadata": self.metadata,
        }

    @classmethod
    def from_dict(cls, data: dict) -> WorkflowEdge:
        return cls(
            edge_id=data["edge_id"],
            source_node_id=data["source_node_id"],
            target_node_id=data["target_node_id"],
            condition=data.get("condition"),
            metadata=data.get("metadata", {}),
        )


@dataclass
class Workflow:
    """Workflow tanımı"""

    workflow_id: str
    name: str
    description: str = ""
    nodes: list[WorkflowNode] = field(default_factory=list)
    edges: list[WorkflowEdge] = field(default_factory=list)
    variables: dict[str, Any] = field(default_factory=dict)
    status: str = "draft"
    version: int = 1
    created_at: datetime = field(default_factory=datetime.now)
    updated_at: datetime = field(default_factory=datetime.now)
    created_by: str | None = None
    tags: list[str] = field(default_factory=list)

    def to_dict(self) -> dict:
        return {
            "workflow_id": self.workflow_id,
            "name": self.name,
            "description": self.description,
            "nodes": [node.to_dict() for node in self.nodes],
            "edges": [edge.to_dict() for edge in self.edges],
            "variables": self.variables,
            "status": self.status,
            "version": self.version,
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat(),
            "created_by": self.created_by,
            "tags": self.tags,
        }

    @classmethod
    def from_dict(cls, data: dict) -> Workflow:
        return cls(
            workflow_id=data["workflow_id"],
            name=data["name"],
            description=data.get("description", ""),
            nodes=[WorkflowNode.from_dict(n) for n in data.get("nodes", [])],
            edges=[WorkflowEdge.from_dict(e) for e in data.get("edges", [])],
            variables=data.get("variables", {}),
            status=data.get("status", "draft"),
            version=data.get("version", 1),
            created_at=(
                datetime.fromisoformat(data["created_at"])
                if data.get("created_at")
                else datetime.now()
            ),
            updated_at=(
                datetime.fromisoformat(data["updated_at"])
                if data.get("updated_at")
                else datetime.now()
            ),
            created_by=data.get("created_by"),
            tags=data.get("tags", []),
        )

    def add_node(self, node: WorkflowNode):
        self.nodes.append(node)
        self.updated_at = datetime.now()

    def get_node(self, node_id: str) -> WorkflowNode | None:
        for node in self.nodes:
            if node.node_id == node_id:
                return node
        return None

    def get_graph(self) -> nx.DiGraph:
        graph = nx.DiGraph()
        for node in self.nodes:
            graph.add_node(node.node_id, **node.to_dict())
        for edge in self.edges:
            graph.add_edge(edge.source_node_id, edge.target_node_id, **edge.to_dict())
        return graph


class WorkflowRegistry:
    """Workflow Registry"""

    def __init__(self, storage_path: str = "./data/workflows"):
        self.storage_path = Path(storage_path)
        self.storage_path.mkdir(parents=True, exist_ok=True)
        self.workflows: dict[str, Workflow] = {}
        self.execution_history: dict[str, list[dict[str, Any]]] = {}
        self._load()

    async def create_workflow(
        self,
        name: str,
        description: str = "",
        template_id: str | None = None,
        created_by: str | None = None,
    ) -> str:
        workflow_id = f"wf_{uuid.uuid4().hex[:8]}"
        workflow = Workflow(
            workflow_id=workflow_id,
            name=name,
            description=description,
            created_by=created_by,
        )

        # Apply template nodes/edges if requested
        if template_id:
            template = WorkflowTemplate.get_template(template_id)
            if template:
                workflow.nodes = [
                    WorkflowNode(**node.to_dict()) for node in template.nodes
                ]
                workflow.edges = [
                    WorkflowEdge(**edge.to_dict()) for edge in template.edges
                ]

        self.workflows[workflow_id] = workflow
        self._save()
        return workflow_id

    def get_workflow(self, workflow_id: str) -> Workflow | None:
        return self.workflows.get(workflow_id)

    def list_workflows(self, status: str | None = None) -> list[dict]:
        return [
            {
                "workflow_id": wf_id,
                "name": wf.name,
                "description": wf.description,
                "status": wf.status,
                "version": wf.version,
                "node_count": len(wf.nodes),
                "edge_count": len(wf.edges),
                "created_at": wf.created_at.isoformat(),
                "updated_at": wf.updated_at.isoformat(),
            }
            for wf_id, wf in self.workflows.items()
            if status is None or wf.status == status
        ]

    def _load(self):
        storage_file = self.storage_path / "workflows.json"
        if storage_file.exists():
            try:
                with open(storage_file, "r", encoding="utf-8") as f:
                    data = json.load(f)
                for wf_data in data.get("workflows", []):
                    workflow = Workflow.from_dict(wf_data)
                    self.workflows[workflow.workflow_id] = workflow
            except Exception as e:
                logger.error(f"Error loading workflows: {e}")

    def _save(self):
        storage_file = self.storage_path / "workflows.json"
        try:
            data = {
                "workflows": [wf.to_dict() for wf in self.workflows.values()],
                "metadata": {
                    "count": len(self.workflows),
                    "updated_at": datetime.now().isoformat(),
                },
            }
            with open(storage_file, "w", encoding="utf-8") as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
        except Exception as e:
            logger.error(f"Error saving workflows: {e}")

    async def execute_workflow(
        self, workflow_id: str, input_data: dict[str, Any]
    ) -> dict[str, Any]:
        """Workflow çalıştır (basit sıralı node yürütme)."""
        workflow = self.workflows.get(workflow_id)
        if workflow is None:
            raise KeyError(f"Workflow not found: {workflow_id}")

        started_at = datetime.now().isoformat()
        nodes_executed: list[dict[str, Any]] = []
        for node in workflow.nodes:
            entry: dict[str, Any] = {
                "node_id": node.node_id,
                "name": node.name,
                "status": "executed",
            }
            if node.type == "tool" and node.config.get("tool") == "translation":
                text = input_data.get("text", "")
                entry["output"] = {"input_text": text}
            nodes_executed.append(entry)

        record = {
            "workflow_id": workflow_id,
            "status": "completed",
            "started_at": started_at,
            "completed_at": datetime.now().isoformat(),
            "nodes_executed": nodes_executed,
        }
        self.execution_history.setdefault(workflow_id, []).append(record)
        self._save()
        return record

    def get_execution_history(
        self, workflow_id: str, limit: int = 100
    ) -> list[dict[str, Any]]:
        """Workflow execution geçmişi."""
        return self.execution_history.get(workflow_id, [])[-limit:]

    async def clone_workflow(self, workflow_id: str, new_name: str) -> str | None:
        """Workflow klonla."""
        workflow = self.workflows.get(workflow_id)
        if workflow is None:
            return None
        new_id = f"wf_{uuid.uuid4().hex[:8]}"
        clone = Workflow(
            workflow_id=new_id,
            name=new_name,
            description=workflow.description,
            nodes=[WorkflowNode.from_dict(n.to_dict()) for n in workflow.nodes],
            edges=[WorkflowEdge.from_dict(e.to_dict()) for e in workflow.edges],
            created_by=workflow.created_by,
        )
        self.workflows[new_id] = clone
        self._save()
        return new_id

    async def delete_workflow(self, workflow_id: str) -> bool:
        """Workflow sil."""
        if workflow_id not in self.workflows:
            return False
        del self.workflows[workflow_id]
        self.execution_history.pop(workflow_id, None)
        self._save()
        return True


# Module-level singleton
_registry = None


def get_workflow_registry() -> WorkflowRegistry:
    """Global registry instance"""
    global _registry
    if _registry is None:
        _registry = WorkflowRegistry()
    return _registry


class WorkflowTemplate:
    """Workflow şablonları"""

    TEMPLATES: ClassVar[dict[str, Any]] = {
        "transliteration_pipeline": {
            "name": "Transliteration Pipeline",
            "description": "Ottoman Turkish to Modern Turkish",
            "nodes": [
                WorkflowNode(node_id="start", type="start", name="Start"),
                WorkflowNode(
                    node_id="transliterate",
                    type="tool",
                    name="Transliterate",
                    config={"tool": "translation"},
                ),
                WorkflowNode(node_id="output", type="end", name="Output"),
            ],
            "edges": [
                WorkflowEdge(
                    edge_id="e1", source_node_id="start", target_node_id="transliterate"
                ),
                WorkflowEdge(
                    edge_id="e2",
                    source_node_id="transliterate",
                    target_node_id="output",
                ),
            ],
        }
    }

    @classmethod
    def get_templates(cls) -> list[dict]:
        return [
            {
                "id": template_id,
                "name": template["name"],
                "description": template["description"],
            }
            for template_id, template in cls.TEMPLATES.items()
        ]

    @classmethod
    def get_template(cls, template_id: str) -> Workflow | None:
        template = cls.TEMPLATES.get(template_id)
        if not template:
            return None
        return Workflow(
            workflow_id=f"template_{template_id}",
            name=template["name"],
            description=template["description"],
            nodes=template["nodes"],
            edges=template["edges"],
        )
