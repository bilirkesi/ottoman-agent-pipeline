"""
Ottoman Agent Pipeline - Main Package
"""

__version__ = "0.1.0"
__author__ = "Bilirkesi AI Team"
__email__ = "research@bilirkesi.ai"

from .core.orchestrator import AgentOrchestrator
from .core.session import AgentSession
from .tools.base import BaseTool
from .models.base import BaseModel
from .api.server import create_app

# BYOK
from .byok.keyvault import (
    KeyVault,
    KeyScope,
    KeyStatus,
    get_keyvault,
    get_deepseek_manager,
    get_gateway_manager
)

# MCP
from .mcp.registry import (
    MCPToolRegistry,
    ToolConfig,
    ToolCall,
    get_tool_registry
)

# Workflow
from .workflow.registry import (
    WorkflowRegistry,
    Workflow,
    WorkflowNode,
    WorkflowEdge,
    get_workflow_registry
)

# CodeGraph
from .codegraph import (
    CodeGraph,
    GraphNode,
    GraphEdge,
    get_codegraph
)

# NLP Graph
from .nlp_graph import (
    NLPGraph,
    CharacterGraph,
    WordGraph,
    EntityGraph,
    DocumentGraph,
    get_nlp_graph
)

__all__ = [
    # Core
    "AgentOrchestrator",
    "AgentSession",
    "BaseTool",
    "BaseModel",
    "create_app",
    # BYOK
    "KeyVault",
    "KeyScope",
    "KeyStatus",
    "get_keyvault",
    "get_deepseek_manager",
    "get_gateway_manager",
    # MCP
    "MCPToolRegistry",
    "ToolConfig",
    "ToolCall",
    "get_tool_registry",
    # Workflow
    "WorkflowRegistry",
    "Workflow",
    "WorkflowNode",
    "WorkflowEdge",
    "get_workflow_registry",
    # CodeGraph
    "CodeGraph",
    "GraphNode",
    "GraphEdge",
    "get_codegraph",
    # NLP Graph
    "NLPGraph",
    "CharacterGraph",
    "WordGraph",
    "EntityGraph",
    "DocumentGraph",
    "get_nlp_graph",
]
