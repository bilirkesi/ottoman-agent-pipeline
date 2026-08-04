"""
Base Model - Abstract class for all model providers
"""

import asyncio
import json
import logging
from abc import ABC, abstractmethod
from typing import Any, AsyncGenerator, Dict, List, Optional

logger = logging.getLogger(__name__)


class BaseModel(ABC):
    """
    Abstract base class for all model providers.
    
    Model providers wrap different LLM APIs (DeepSeek, OpenAI, etc.)
    and provide a unified interface for the agent.
    """
    
    name: str = "base_model"
    description: str = "Base model provider"
    
    def __init__(self, api_key: Optional[str] = None, base_url: Optional[str] = None, **kwargs):
        self.api_key = api_key
        self.base_url = base_url
        self._client = None
        self._initialized = False
    
    @abstractmethod
    async def chat(
        self,
        messages: List[Dict[str, str]],
        model: Optional[str] = None,
        **kwargs
    ) -> Dict[str, Any]:
        """
        Send chat completion request.
        
        Args:
            messages: List of chat messages
            model: Model name (optional)
            **kwargs: Additional parameters
            
        Returns:
            Response dict with content, tool_calls, usage
        """
        pass
    
    @abstractmethod
    async def chat_stream(
        self,
        messages: List[Dict[str, str]],
        model: Optional[str] = None,
        **kwargs
    ) -> AsyncGenerator[Dict[str, Any], None]:
        """
        Stream chat completion.
        
        Args:
            messages: List of chat messages
            model: Model name (optional)
            **kwargs: Additional parameters
            
        Yields:
            Response chunks
        """
        pass
    
    async def initialize(self) -> None:
        """Initialize model client."""
        self._initialized = True
        logger.debug(f"Model '{self.name}' initialized")
    
    async def close(self) -> None:
        """Cleanup model resources."""
        self._initialized = False
        self._client = None
        logger.debug(f"Model '{self.name}' closed")
    
    def get_info(self) -> Dict[str, Any]:
        """Get model information."""
        return {
            "name": self.name,
            "description": self.description,
            "initialized": self._initialized
        }
    
    def _validate_messages(self, messages: List[Dict[str, str]]) -> bool:
        """Validate message format."""
        if not messages:
            return False
        
        for msg in messages:
            if "role" not in msg or "content" not in msg:
                return False
        
        return True
    
    async def __call__(
        self,
        messages: List[Dict[str, str]],
        **kwargs
    ) -> Dict[str, Any]:
        """Allow model to be called like a function."""
        return await self.chat(messages, **kwargs)
