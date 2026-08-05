"""
Ottoman Agent Pipeline - Main Package
"""

__version__ = "0.1.0"
__author__ = "Bilirkesi AI Team"
__email__ = "research@bilirkesi.ai"

from .api.server import create_app

# BYOK
from .byok.keyvault import (
    KeyScope,
    KeyStatus,
    KeyVault,
    get_deepseek_manager,
    get_gateway_manager,
    get_keyvault,
)

# CodeGraph
from .codegraph import CodeGraph, GraphEdge, GraphNode, get_codegraph
from .core.orchestrator import AgentOrchestrator
from .core.session import AgentSession

# MCP
from .mcp.registry import MCPToolRegistry, ToolCall, ToolConfig, get_tool_registry
from .models.base import BaseModel

# NLP Graph
from .nlp_graph import (
    CharacterGraph,
    DocumentGraph,
    EntityGraph,
    NLPGraph,
    WordGraph,
    get_nlp_graph,
)
from .tools.base import BaseTool

# Workflow
from .workflow.registry import (
    Workflow,
    WorkflowEdge,
    WorkflowNode,
    WorkflowRegistry,
    get_workflow_registry,
)

__all__ = [
    # Core
    "AgentOrchestrator",
    "AgentSession",
    "BaseModel",
    "BaseTool",
    "CharacterGraph",
    # CodeGraph
    "CodeGraph",
    "DocumentGraph",
    "EntityGraph",
    "GraphEdge",
    "GraphNode",
    "KeyScope",
    "KeyStatus",
    # BYOK
    "KeyVault",
    # MCP
    "MCPToolRegistry",
    # NLP Graph
    "NLPGraph",
    "ToolCall",
    "ToolConfig",
    "WordGraph",
    "Workflow",
    "WorkflowEdge",
    "WorkflowNode",
    # Workflow
    "WorkflowRegistry",
    "create_app",
    "get_codegraph",
    "get_deepseek_manager",
    "get_gateway_manager",
    "get_keyvault",
    "get_nlp_graph",
    "get_tool_registry",
    "get_workflow_registry",
]
