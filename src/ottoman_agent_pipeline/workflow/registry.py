"""
Visual Workflow Editor - Ottoman Agent Pipeline için workflow yönetimi
"""

import asyncio
import json
import logging
import uuid
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple
from dataclasses import dataclass, field

import networkx as nx
from loguru import logger

logger = logging.getLogger(__name__)


@dataclass
class WorkflowNode:
    """Workflow düğümü"""
    node_id: str
    type: str
    name: str
    config: Dict[str, Any] = field(default_factory=dict)
    position: Tuple[int, int] = (0, 0)
    metadata: Dict[str, Any] = field(default_factory=dict)
    created_at: datetime = field(default_factory=datetime.now)
    updated_at: datetime = field(default_factory=datetime.now)
    
    def to_dict(self) -> Dict:
        return {
            "node_id": self.node_id,
            "type": self.type,
            "name": self.name,
            "config": self.config,
            "position": list(self.position),
            "metadata": self.metadata,
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat()
        }
    
    @classmethod
    def from_dict(cls, data: Dict) -> 'WorkflowNode':
        return cls(
            node_id=data["node_id"],
            type=data["type"],
            name=data["name"],
            config=data.get("config", {}),
            position=tuple(data.get("position", [0, 0])),
            metadata=data.get("metadata", {}),
            created_at=datetime.fromisoformat(data["created_at"]) if data.get("created_at") else datetime.now(),
            updated_at=datetime.fromisoformat(data["updated_at"]) if data.get("updated_at") else datetime.now()
        )


@dataclass
class WorkflowEdge:
    """Workflow kenarı"""
    edge_id: str
    source_node_id: str
    target_node_id: str
    condition: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def to_dict(self) -> Dict:
        return {
            "edge_id": self.edge_id,
            "source_node_id": self.source_node_id,
            "target_node_id": self.target_node_id,
            "condition": self.condition,
            "metadata": self.metadata
        }
    
    @classmethod
    def from_dict(cls, data: Dict) -> 'WorkflowEdge':
        return cls(
            edge_id=data["edge_id"],
            source_node_id=data["source_node_id"],
            target_node_id=data["target_node_id"],
            condition=data.get("condition"),
            metadata=data.get("metadata", {})
        )


@dataclass
class Workflow:
    """Workflow tanımı"""
    workflow_id: str
    name: str
    description: str = ""
    nodes: List[WorkflowNode] = field(default_factory=list)
    edges: List[WorkflowEdge] = field(default_factory=list)
    variables: Dict[str, Any] = field(default_factory=dict)
    status: str = "draft"
    version: int = 1
    created_at: datetime = field(default_factory=datetime.now)
    updated_at: datetime = field(default_factory=datetime.now)
    created_by: Optional[str] = None
    tags: List[str] = field(default_factory=list)
    
    def to_dict(self) -> Dict:
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
            "tags": self.tags
        }
    
    @classmethod
    def from_dict(cls, data: Dict) -> 'Workflow':
        return cls(
            workflow_id=data["workflow_id"],
            name=data["name"],
            description=data.get("description", ""),
            nodes=[WorkflowNode.from_dict(n) for n in data.get("nodes", [])],
            edges=[WorkflowEdge.from_dict(e) for e in data.get("edges", [])],
            variables=data.get("variables", {}),
            status=data.get("status", "draft"),
            version=data.get("version", 1),
            created_at=datetime.fromisoformat(data["created_at"]) if data.get("created_at") else datetime.now(),
            updated_at=datetime.fromisoformat(data["updated_at"]) if data.get("updated_at") else datetime.now(),
            created_by=data.get("created_by"),
            tags=data.get("tags", [])
        )
    
    def add_node(self, node: WorkflowNode):
        self.nodes.append(node)
        self.updated_at = datetime.now()
    
    def get_node(self, node_id: str) -> Optional[WorkflowNode]:
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
        self.workflows: Dict[str, Workflow] = {}
        self._load()
    
    async def create_workflow(self, name: str, description: str = "", 
                               created_by: Optional[str] = None) -> str:
        workflow_id = f"wf_{uuid.uuid4().hex[:8]}"
        workflow = Workflow(
            workflow_id=workflow_id,
            name=name,
            description=description,
            created_by=created_by
        )
        self.workflows[workflow_id] = workflow
        self._save()
        return workflow_id
    
    def get_workflow(self, workflow_id: str) -> Optional[Workflow]:
        return self.workflows.get(workflow_id)
    
    def list_workflows(self) -> List[Dict]:
        return [
            {
                "workflow_id": wf_id,
                "name": wf.name,
                "status": wf.status,
                "version": wf.version,
                "node_count": len(wf.nodes)
            }
            for wf_id, wf in self.workflows.items()
        ]
    
    async def _load(self):
        storage_file = self.storage_path / "workflows.json"
        if storage_file.exists():
            try:
                import aiofiles
                async with aiofiles.open(storage_file, 'r') as f:
                    data = json.loads(await f.read())
                for wf_data in data.get("workflows", []):
                    workflow = Workflow.from_dict(wf_data)
                    self.workflows[workflow.workflow_id] = workflow
            except Exception as e:
                logger.error(f"Error loading workflows: {e}")
    
    async def _save(self):
        storage_file = self.storage_path / "workflows.json"
        try:
            import aiofiles
            data = {
                "workflows": [wf.to_dict() for wf in self.workflows.values()],
                "metadata": {
                    "count": len(self.workflows),
                    "updated_at": datetime.now().isoformat()
                }
            }
            async with aiofiles.open(storage_file, 'w') as f:
                await f.write(json.dumps(data, indent=2))
        except Exception as e:
            logger.error(f"Error saving workflows: {e}")


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
    
    TEMPLATES = {
        "transliteration_pipeline": {
            "name": "Transliteration Pipeline",
            "description": "Ottoman Turkish to Modern Turkish",
            "nodes": [
                WorkflowNode(node_id="start", type="start", name="Start"),
                WorkflowNode(node_id="transliterate", type="tool", name="Transliterate", config={"tool": "translation"}),
                WorkflowNode(node_id="output", type="end", name="Output")
            ],
            "edges": [
                WorkflowEdge(edge_id="e1", source_node_id="start", target_node_id="transliterate"),
                WorkflowEdge(edge_id="e2", source_node_id="transliterate", target_node_id="output")
            ]
        }
    }
    
    @classmethod
    def get_templates(cls) -> List[Dict]:
        return [
            {
                "id": template_id,
                "name": template["name"],
                "description": template["description"]
            }
            for template_id, template in cls.TEMPLATES.items()
        ]
    
    @classmethod
    def get_template(cls, template_id: str) -> Optional[Workflow]:
        template = cls.TEMPLATES.get(template_id)
        if not template:
            return None
        return Workflow(
            workflow_id=f"template_{template_id}",
            name=template["name"],
            description=template["description"],
            nodes=template["nodes"],
            edges=template["edges"]
        )
