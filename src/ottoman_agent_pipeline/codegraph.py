"""
CodeGraph - Ottoman Agent Pipeline için Knowledge Graph ve Code Intelligence
"""

from __future__ import annotations

import json
import logging
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
from typing import Any

import aiofiles
import networkx as nx

logger = logging.getLogger(__name__)


@dataclass
class GraphNode:
    """Graph düğümü"""

    id: str
    type: str  # file, function, class, module, agent, tool, model
    name: str
    content: str = ""
    metadata: dict[str, Any] = field(default_factory=dict)
    created_at: str = field(default_factory=lambda: datetime.now().isoformat())
    updated_at: str = field(default_factory=lambda: datetime.now().isoformat())

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "type": self.type,
            "name": self.name,
            "content": (
                self.content[:500] if self.content else ""
            ),  # Truncate for storage
            "metadata": self.metadata,
            "created_at": self.created_at,
            "updated_at": self.updated_at,
        }


@dataclass
class GraphEdge:
    """Graph kenarı"""

    source: str
    target: str
    type: str  # imports, calls, depends_on, related_to, owns
    weight: float = 1.0
    metadata: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict:
        return {
            "source": self.source,
            "target": self.target,
            "type": self.type,
            "weight": self.weight,
            "metadata": self.metadata,
        }


class CodeGraph:
    """
    CodeGraph - Code ve Knowledge Graph sistemi

    Özellikler:
    - Dependency graph oluşturma
    - Code intelligence (call graph, call chain)
    - Semantic search
    - Impact analysis
    - Agent/tool/model relationship tracking
    """

    def __init__(self, db_path: str = "./data/codegraph.db"):
        self.db_path = Path(db_path)
        self.db_path.parent.mkdir(parents=True, exist_ok=True)

        # NetworkX graph
        self.graph = nx.DiGraph()

        # Node store (for persistence)
        self.nodes: dict[str, GraphNode] = {}

        # Edge store
        self.edges: list[GraphEdge] = []

        # Indexes for fast lookup
        self._type_index: dict[str, set[str]] = {}  # type -> node_ids
        self._name_index: dict[str, str] = {}  # name -> node_id
        self._file_index: dict[str, set[str]] = {}  # file -> node_ids

        # Load existing data
        self._load()

        logger.info(f"CodeGraph initialized: {db_path}")

    async def add_node(self, node: GraphNode) -> str:
        """
        Graph'e düğüm ekle
        """
        # Check if exists
        if node.id in self.nodes:
            # Update existing
            old_node = self.nodes[node.id]
            node.created_at = old_node.created_at
            self.graph.remove_node(node.id)

        # Add to graph
        self.graph.add_node(
            node.id,
            type=node.type,
            name=node.name,
            content=node.content,
            metadata=node.metadata,
            created_at=node.created_at,
            updated_at=node.updated_at,
        )

        # Update stores
        self.nodes[node.id] = node
        self._update_indexes(node)

        logger.debug(f"Added node: {node.id} ({node.type})")
        return node.id

    async def add_edge(self, edge: GraphEdge) -> None:
        """
        Graph'e kenar ekle
        """
        # Validate nodes exist
        if edge.source not in self.nodes:
            raise ValueError(f"Source node not found: {edge.source}")
        if edge.target not in self.nodes:
            raise ValueError(f"Target node not found: {edge.target}")

        # Add to graph
        self.graph.add_edge(
            edge.source,
            edge.target,
            type=edge.type,
            weight=edge.weight,
            metadata=edge.metadata,
        )

        # Update stores
        self.edges.append(edge)

        logger.debug(f"Added edge: {edge.source} -> {edge.target} ({edge.type})")

    async def remove_node(self, node_id: str) -> bool:
        """Düğüm sil"""
        if node_id not in self.nodes:
            return False

        # Remove from graph
        self.graph.remove_node(node_id)

        # Remove from stores
        del self.nodes[node_id]
        self.edges = [
            e for e in self.edges if e.source != node_id and e.target != node_id
        ]

        # Update indexes
        node = self.nodes.get(node_id)
        if node:
            self._remove_from_indexes(node)

        logger.debug(f"Removed node: {node_id}")
        return True

    async def get_node(self, node_id: str) -> GraphNode | None:
        """Düğüm getir"""
        return self.nodes.get(node_id)

    async def get_neighbors(self, node_id: str, direction: str = "both") -> list[str]:
        """Komşu düğümler"""
        if node_id not in self.nodes:
            return []

        if direction == "out":
            return list(self.graph.successors(node_id))
        elif direction == "in":
            return list(self.graph.predecessors(node_id))
        else:
            # Both
            return list(
                set(
                    list(self.graph.successors(node_id))
                    + list(self.graph.predecessors(node_id))
                )
            )

    async def get_callers(self, node_id: str) -> list[str]:
        """Call eden düğümler (predecessors)"""
        return list(self.graph.predecessors(node_id))

    async def get_callees(self, node_id: str) -> list[str]:
        """Call edilen düğümler (successors)"""
        return list(self.graph.successors(node_id))

    async def get_dependencies(self, node_id: str) -> list[tuple[str, str, float]]:
        """Bağımlılıklar (type='imports' veya 'depends_on')"""
        deps = []
        for neighbor in self.graph.successors(node_id):
            edge_data = self.graph.edges[node_id, neighbor]
            if edge_data.get("type") in ["imports", "depends_on"]:
                deps.append(
                    (neighbor, edge_data.get("type"), edge_data.get("weight", 1.0))
                )
        return deps

    async def get_dependents(self, node_id: str) -> list[tuple[str, str, float]]:
        """Bağımlı olanlar (type='imports' veya 'depends_on')"""
        deps = []
        for neighbor in self.graph.predecessors(node_id):
            edge_data = self.graph.edges[neighbor, node_id]
            if edge_data.get("type") in ["imports", "depends_on"]:
                deps.append(
                    (neighbor, edge_data.get("type"), edge_data.get("weight", 1.0))
                )
        return deps

    async def get_all_nodes_of_type(self, node_type: str) -> list[GraphNode]:
        """Belirli tipte tüm düğümler"""
        node_ids = self._type_index.get(node_type, set())
        return [self.nodes[nid] for nid in node_ids if nid in self.nodes]

    async def search_nodes(self, query: str, limit: int = 10) -> list[GraphNode]:
        """
        Node arama (basit string match)
        """
        results = []
        query_lower = query.lower()

        for node in self.nodes.values():
            if (
                query_lower in node.name.lower()
                or query_lower in node.content.lower()
                or query_lower in node.type.lower()
            ):
                results.append(node)
                if len(results) >= limit:
                    break

        return results

    async def find_shortest_path(self, source: str, target: str) -> list[str] | None:
        """En kısa yol bul"""
        if source not in self.nodes or target not in self.nodes:
            return None

        try:
            path = nx.shortest_path(self.graph, source, target)
            return path
        except nx.NetworkXNoPath:
            return None

    async def get_component_map(self) -> dict[str, Any]:
        """
        Component map - agent/tool/model relationships
        """
        components = {
            "agents": [],
            "tools": [],
            "models": [],
            "files": [],
            "relationships": [],
        }

        # Collect agents
        for node in await self.get_all_nodes_of_type("agent"):
            components["agents"].append(node.to_dict())

        # Collect tools
        for node in await self.get_all_nodes_of_type("tool"):
            components["tools"].append(node.to_dict())

        # Collect models
        for node in await self.get_all_nodes_of_type("model"):
            components["models"].append(node.to_dict())

        # Collect files
        for node in await self.get_all_nodes_of_type("file"):
            components["files"].append(node.to_dict())

        # Collect relationships
        for edge in self.edges:
            if edge.type in ["uses", "calls", "depends_on", "owns"]:
                components["relationships"].append(edge.to_dict())

        return components

    async def get_impact_analysis(self, node_id: str) -> dict[str, Any]:
        """
        Impact analizi - bu node değişirse ne etkilenir?
        """
        if node_id not in self.nodes:
            return {"error": "Node not found"}

        # Get all downstream dependencies
        affected = set()
        queue = [node_id]
        visited = set()

        while queue:
            current = queue.pop(0)
            if current in visited:
                continue
            visited.add(current)

            for neighbor in self.graph.successors(current):
                edge_data = self.graph.edges[current, neighbor]
                if edge_data.get("type") in ["depends_on", "calls", "imports"]:
                    affected.add(neighbor)
                    queue.append(neighbor)

        # Get all upstream dependencies
        upstream = set()
        queue = [node_id]
        visited = set()

        while queue:
            current = queue.pop(0)
            if current in visited:
                continue
            visited.add(current)

            for neighbor in self.graph.predecessors(current):
                edge_data = self.graph.edges[neighbor, current]
                if edge_data.get("type") in ["depends_on", "calls", "imports"]:
                    upstream.add(neighbor)
                    queue.append(neighbor)

        return {
            "node_id": node_id,
            "node_name": self.nodes[node_id].name,
            "node_type": self.nodes[node_id].type,
            "affected_count": len(affected),
            "affected_nodes": list(affected),
            "upstream_count": len(upstream),
            "upstream_nodes": list(upstream),
        }

    async def get_file_diff(self, file_path: str, node_id: str) -> dict[str, Any]:
        """
        Dosya diff - değişiklik analizi
        """
        if node_id not in self.nodes:
            return {"error": "Node not found"}

        node = self.nodes[node_id]

        # Get related nodes
        related = await self.get_neighbors(node_id, "both")

        # Get dependencies
        deps = await self.get_dependencies(node_id)

        return {
            "file_path": file_path,
            "node_id": node_id,
            "node_name": node.name,
            "changes": [],  # Will be populated with actual diff
            "related_nodes": related[:10],
            "dependencies": deps,
        }

    async def get_agent_tool_usage(self, agent_id: str) -> dict[str, Any]:
        """
        Agent'ın kullandığı tool'lar
        """
        if agent_id not in self.nodes:
            return {"error": "Agent not found"}

        # Get tools used by agent
        tools = []
        for neighbor in self.graph.successors(agent_id):
            edge_data = self.graph.edges[agent_id, neighbor]
            if edge_data.get("type") == "uses":
                tool_node = self.nodes.get(neighbor)
                if tool_node:
                    tools.append(tool_node.to_dict())

        # Get models used by agent
        models = []
        for neighbor in self.graph.successors(agent_id):
            edge_data = self.graph.edges[agent_id, neighbor]
            if edge_data.get("type") == "uses":
                model_node = self.nodes.get(neighbor)
                if model_node and model_node.type == "model":
                    models.append(model_node.to_dict())

        return {
            "agent_id": agent_id,
            "agent_name": self.nodes[agent_id].name,
            "tools": tools,
            "models": models,
            "total_tools": len(tools),
            "total_models": len(models),
        }

    async def get_model_calls(self, model_id: str) -> dict[str, Any]:
        """
        Model'in çağrı analizi
        """
        if model_id not in self.nodes:
            return {"error": "Model not found"}

        # Get callers
        callers = await self.get_callers(model_id)

        # Get callees
        callees = await self.get_callees(model_id)

        return {
            "model_id": model_id,
            "model_name": self.nodes[model_id].name,
            "callers": callers,
            "callees": callees,
            "total_callers": len(callers),
            "total_callees": len(callees),
        }

    async def get_orphan_nodes(self) -> list[str]:
        """
        Bağlantısız düğümler (isolated nodes)
        """
        orphans = []
        for node_id in self.nodes:
            has_deps = self.graph.has_predecessors(node_id) or self.graph.has_successors(  # type: ignore[reportAttributeAccessIssue]
                node_id
            )
            if not has_deps:
                orphans.append(node_id)
        return orphans

    async def get_circular_dependencies(self) -> list[list[str]]:
        """
        Döngüsel bağımlılıklar
        """
        cycles = []
        try:
            cycles = list(nx.simple_cycles(self.graph))
        except Exception as e:
            logger.warning(f"Error finding cycles: {e}")

        return cycles[:10]  # Limit results

    async def get_graph_stats(self) -> dict[str, Any]:
        """
        Graph istatistikleri
        """
        stats = {
            "total_nodes": len(self.nodes),
            "total_edges": len(self.edges),
            "nodes_by_type": {},
            "edges_by_type": {},
            "orphan_nodes": len(await self.get_orphan_nodes()),
            "circular_dependencies": len(await self.get_circular_dependencies()),
            "average_degree": (
                sum(dict(self.graph.degree()).values()) / len(self.graph)
                if self.graph.number_of_nodes() > 0
                else 0
            ),
            "density": nx.density(self.graph),
        }

        # Count by type
        for node in self.nodes.values():
            stats["nodes_by_type"][node.type] = (
                stats["nodes_by_type"].get(node.type, 0) + 1
            )

        for edge in self.edges:
            stats["edges_by_type"][edge.type] = (
                stats["edges_by_type"].get(edge.type, 0) + 1
            )

        return stats

    def _update_indexes(self, node: GraphNode) -> None:
        """Index'leri güncelle"""
        # Type index
        if node.type not in self._type_index:
            self._type_index[node.type] = set()
        self._type_index[node.type].add(node.id)

        # Name index
        self._name_index[node.name.lower()] = node.id

        # File index
        if node.metadata.get("file_path"):
            fp = node.metadata["file_path"]
            if fp not in self._file_index:
                self._file_index[fp] = set()
            self._file_index[fp].add(node.id)

    def _remove_from_indexes(self, node: GraphNode) -> None:
        """Index'lerden çıkar"""
        # Type index
        if node.type in self._type_index:
            self._type_index[node.type].discard(node.id)
            if not self._type_index[node.type]:
                del self._type_index[node.type]

        # Name index
        self._name_index.pop(node.name.lower(), None)

        # File index
        if node.metadata.get("file_path"):
            fp = node.metadata["file_path"]
            if fp in self._file_index:
                self._file_index[fp].discard(node.id)
                if not self._file_index[fp]:
                    del self._file_index[fp]

    def _load(self) -> None:
        """Data'yı yükle"""
        db_file = self.db_path
        if db_file.exists():
            try:
                with open(db_file, "r", encoding="utf-8") as f:
                    data = json.load(f)

                # Load nodes
                for node_data in data.get("nodes", []):
                    node = GraphNode(**node_data)
                    self.nodes[node.id] = node
                    self._update_indexes(node)

                # Load edges
                for edge_data in data.get("edges", []):
                    edge = GraphEdge(**edge_data)
                    self.edges.append(edge)

                # Rebuild graph
                for node in self.nodes.values():
                    self.graph.add_node(
                        node.id,
                        type=node.type,
                        name=node.name,
                        content=node.content,
                        metadata=node.metadata,
                        created_at=node.created_at,
                        updated_at=node.updated_at,
                    )

                for edge in self.edges:
                    self.graph.add_edge(
                        edge.source,
                        edge.target,
                        type=edge.type,
                        weight=edge.weight,
                        metadata=edge.metadata,
                    )

                logger.info(
                    f"Loaded {len(self.nodes)} nodes, {len(self.edges)} edges from {db_file}"
                )

            except Exception as e:
                logger.error(f"Error loading graph: {e}")

    async def _save(self) -> None:
        """Data'yı kaydet"""
        try:
            data = {
                "nodes": [node.to_dict() for node in self.nodes.values()],
                "edges": [edge.to_dict() for edge in self.edges],
                "metadata": {
                    "version": "1.0.0",
                    "created_at": datetime.now().isoformat(),
                    "updated_at": datetime.now().isoformat(),
                    "node_count": len(self.nodes),
                    "edge_count": len(self.edges),
                },
            }

            async with aiofiles.open(self.db_path, "w", encoding="utf-8") as f:
                await f.write(json.dumps(data, indent=2, ensure_ascii=False))

            logger.debug(
                f"Saved {len(self.nodes)} nodes, {len(self.edges)} edges to {self.db_path}"
            )

        except Exception as e:
            logger.error(f"Error saving graph: {e}")

    async def save(self) -> None:
        """Graph'i kaydet"""
        await self._save()

    async def export_to_json(self) -> str:
        """JSON formatında export"""
        data = {
            "nodes": [node.to_dict() for node in self.nodes.values()],
            "edges": [edge.to_dict() for edge in self.edges],
            "stats": await self.get_graph_stats(),
        }
        return json.dumps(data, indent=2, ensure_ascii=False)

    async def import_from_json(self, data: str) -> None:
        """JSON formatında import"""
        try:
            json_data = json.loads(data)

            # Clear existing
            self.nodes.clear()
            self.edges.clear()
            self.graph.clear()
            self._type_index.clear()
            self._name_index.clear()
            self._file_index.clear()

            # Import nodes
            for node_data in json_data.get("nodes", []):
                node = GraphNode(**node_data)
                self.nodes[node.id] = node
                self._update_indexes(node)
                self.graph.add_node(
                    node.id,
                    type=node.type,
                    name=node.name,
                    content=node.content,
                    metadata=node.metadata,
                    created_at=node.created_at,
                    updated_at=node.updated_at,
                )

            # Import edges
            for edge_data in json_data.get("edges", []):
                edge = GraphEdge(**edge_data)
                self.edges.append(edge)
                self.graph.add_edge(
                    edge.source,
                    edge.target,
                    type=edge.type,
                    weight=edge.weight,
                    metadata=edge.metadata,
                )

            logger.info(f"Imported {len(self.nodes)} nodes, {len(self.edges)} edges")

        except Exception as e:
            logger.error(f"Error importing graph: {e}")
            raise


# Factory function
def create_codegraph(db_path: str = "./data/codegraph.db") -> CodeGraph:
    """CodeGraph instance oluştur"""
    return CodeGraph(db_path=db_path)


# Module-level singleton
_codegraph = None


def get_codegraph() -> CodeGraph:
    """Global CodeGraph instance"""
    global _codegraph
    if _codegraph is None:
        _codegraph = CodeGraph()
    return _codegraph
