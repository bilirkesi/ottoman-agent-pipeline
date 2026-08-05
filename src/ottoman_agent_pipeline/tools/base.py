"""Base Tool - Abstract class for all agent tools"""

import json
import logging
from abc import ABC, abstractmethod
from collections.abc import AsyncGenerator
from typing import Any

logger = logging.getLogger(__name__)


class BaseTool(ABC):
    """
    Abstract base class for all agent tools.

    Tools are MCP-compatible functions that the agent can call to perform
    actions like file operations, web searches, etc.
    """

    name: str = "base_tool"
    description: str = "Base tool for agent operations"

    def __init__(self, **kwargs):
        self.config = kwargs
        self._initialized = False

    @abstractmethod
    async def execute(self, **kwargs) -> Any:
        """
        Execute the tool with given parameters.

        Args:
            **kwargs: Tool-specific parameters

        Returns:
            Tool execution result
        """

    async def execute_stream(self, **kwargs) -> AsyncGenerator[str, None]:
        """
        Stream execution results.

        Args:
            **kwargs: Tool-specific parameters

        Yields:
            Streaming output chunks
        """
        result = await self.execute(**kwargs)
        if isinstance(result, str):
            yield result
        elif isinstance(result, dict):
            yield json.dumps(result, ensure_ascii=False)
        else:
            yield str(result)

    def get_schema(self) -> dict[str, Any]:
        """Get tool schema for MCP/Function calling."""
        return {
            "name": self.name,
            "description": self.description,
            "input_schema": {
                "type": "object",
                "properties": self._get_input_schema(),
                "required": self._get_required_fields(),
            },
        }

    def _get_input_schema(self) -> dict[str, Any]:
        """Get input schema (override in subclass)."""
        return {}

    def _get_required_fields(self) -> list[str]:
        """Get required fields (override in subclass)."""
        return []

    async def initialize(self) -> None:
        """Initialize tool resources."""
        self._initialized = True
        logger.debug(f"Tool '{self.name}' initialized")

    async def close(self) -> None:
        """Cleanup tool resources."""
        self._initialized = False
        logger.debug(f"Tool '{self.name}' closed")

    async def __call__(self, **kwargs) -> Any:
        """Allow tool to be called like a function."""
        return await self.execute(**kwargs)

    def __repr__(self) -> str:
        return f"<{self.__class__.__name__}: {self.name}>"
