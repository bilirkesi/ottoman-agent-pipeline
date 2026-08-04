"""
DB-Mentat Gateway Model Provider
"""

import asyncio
import json
import logging
import os
from typing import Any, AsyncGenerator, Dict, List, Optional

import httpx

from .base import BaseModel

logger = logging.getLogger(__name__)


class GatewayModel(BaseModel):
    """
    DB-Mentat Gateway model provider.
    
    Routes requests to the local gateway which manages
    multiple providers (OpenAI, Anthropic, etc.)
    """
    
    name = "gateway"
    description = "DB-Mentat Gateway model provider for multi-provider routing"
    
    DEFAULT_URL = "http://localhost:3002"
    
    def __init__(
        self,
        api_key: Optional[str] = None,
        url: str = DEFAULT_URL,
        **kwargs
    ):
        super().__init__(api_key=api_key, base_url=url, **kwargs)
        self.url = url.rstrip("/")
    
    async def initialize(self) -> None:
        """Initialize gateway client."""
        self._client = httpx.AsyncClient(
            base_url=self.url,
            timeout=60.0,
            headers={
                "Authorization": f"Bearer {self.api_key or os.environ.get('GATEWAY_API_KEY', '')}",
                "Content-Type": "application/json"
            }
        )
        
        await super().initialize()
        logger.info(f"Gateway model initialized: {self.url}")
    
    async def close(self) -> None:
        """Cleanup client."""
        if self._client:
            await self._client.aclose()
            self._client = None
        await super().close()
    
    async def chat(
        self,
        messages: List[Dict[str, str]],
        model: Optional[str] = None,
        stream: bool = False,
        **kwargs
    ) -> Dict[str, Any]:
        """
        Send chat completion through gateway.
        
        Args:
            messages: List of chat messages
            model: Model name (optional, uses gateway default)
            stream: Whether to stream
            **kwargs: Additional parameters
        """
        if not self._client:
            await self.initialize()
        
        payload = {
            "model": model or "gpt-4o",
            "messages": messages,
            "stream": stream,
            **kwargs
        }
        
        try:
            if stream:
                return await self._chat_stream(payload)
            else:
                return await self._chat_completion(payload)
                
        except Exception as e:
            logger.error(f"Gateway chat error: {e}")
            raise
    
    async def chat_stream(
        self,
        messages: List[Dict[str, str]],
        model: Optional[str] = None,
        **kwargs
    ) -> AsyncGenerator[Dict[str, Any], None]:
        """
        Stream chat completion through gateway.
        """
        if not self._client:
            await self.initialize()
        
        payload = {
            "model": model or "gpt-4o",
            "messages": messages,
            "stream": True,
            **kwargs
        }
        
        try:
            async with self._client.stream("POST", "/v1/chat/completions", json=payload) as response:
                response.raise_for_status()
                
                async for line in response.aiter_lines():
                    if line.startswith("data: "):
                        data = line[6:]
                        if data.strip() == "[DONE]":
                            break
                        try:
                            chunk = json.loads(data)
                            if chunk.get("choices"):
                                yield {
                                    "content": chunk["choices"][0].get("delta", {}).get("content", ""),
                                    "finish_reason": chunk["choices"][0].get("finish_reason"),
                                    "model": model or "gpt-4o"
                                }
                        except json.JSONDecodeError:
                            pass
                            
        except Exception as e:
            logger.error(f"Gateway stream error: {e}")
            raise
    
    async def _chat_completion(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        """Handle non-streaming completion."""
        response = await self._client.post("/v1/chat/completions", json=payload)
        response.raise_for_status()
        
        data = response.json()
        
        return {
            "content": data["choices"][0]["message"]["content"],
            "model": data["model"],
            "usage": data.get("usage", {}),
            "tool_calls": data["choices"][0]["message"].get("tool_calls", [])
        }
    
    async def _chat_stream(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        """Handle streaming completion."""
        content_parts = []
        model = None
        finish_reason = None
        
        async with self._client.stream("POST", "/v1/chat/completions", json=payload) as response:
            response.raise_for_status()
            
            async for line in response.aiter_lines():
                if line.startswith("data: "):
                    data = line[6:]
                    if data.strip() == "[DONE]":
                        break
                    try:
                        chunk = json.loads(data)
                        if chunk.get("choices"):
                            choice = chunk["choices"][0]
                            if choice.get("delta", {}).get("content"):
                                content_parts.append(choice["delta"]["content"])
                            if choice.get("finish_reason"):
                                finish_reason = choice["finish_reason"]
                            if chunk.get("model"):
                                model = chunk["model"]
                    except json.JSONDecodeError:
                        pass
        
        return {
            "content": "".join(content_parts),
            "model": model or payload.get("model", "unknown"),
            "finish_reason": finish_reason,
            "usage": {"total_tokens": 0}
        }
    
    async def health_check(self) -> Dict[str, Any]:
        """Check gateway health."""
        try:
            response = await self._client.get("/health")
            response.raise_for_status()
            return {"status": "healthy", "data": response.json()}
        except Exception as e:
            return {"status": "unhealthy", "error": str(e)}
    
    def get_info(self) -> Dict[str, Any]:
        """Get model information."""
        return {
            "name": self.name,
            "url": self.url,
            "description": self.description
        }
