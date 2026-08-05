"""
DeepSeek Model Provider
"""

from __future__ import annotations

import json
import logging
import os
from collections.abc import AsyncGenerator
from typing import Any, ClassVar

from openai import AsyncOpenAI

from .base import BaseModel

logger = logging.getLogger(__name__)


class DeepSeekModel(BaseModel):
    """
    DeepSeek API model provider.

    Supports:
    - DeepSeek V4 Flash (fast, cheap)
    - DeepSeek V4 Pro (powerful)
    - Streaming responses
    """

    name = "deepseek"
    description = "DeepSeek API model provider with V4 Flash and V4 Pro support"

    DEFAULT_MODELS: ClassVar[list[dict[str, Any]]] = [
        {
            "name": "deepseek-v4-flash",
            "context": 1000000,
            "max_output": 384000,
            "cost_per_1m": {"input": 0.14, "output": 0.28},
        },
        {
            "name": "deepseek-v4-pro",
            "context": 128000,
            "max_output": 8000,
            "cost_per_1m": {"input": 0.50, "output": 2.00},
        },
    ]

    def __init__(
        self,
        api_key: str | None = None,
        base_url: str = "https://api.deepseek.com/v1",
        models: list[dict[str, Any]] | None = None,
        **kwargs,
    ):
        super().__init__(api_key=api_key, base_url=base_url, **kwargs)
        self.models = models or self.DEFAULT_MODELS
        self._default_model = "deepseek-v4-flash"

    async def initialize(self) -> None:
        """Initialize DeepSeek client."""
        api_key = self.api_key or os.environ.get("DEEPSEEK_API_KEY")

        if not api_key:
            raise ValueError("DeepSeek API key not provided")

        self._client = AsyncOpenAI(api_key=api_key, base_url=self.base_url)

        await super().initialize()
        logger.info("DeepSeek model initialized")

    async def chat(
        self,
        messages: list[dict[str, str]],
        model: str | None = None,
        stream: bool = False,
        **kwargs,
    ) -> dict[str, Any]:
        """
        Send chat completion request.

        Args:
            messages: List of chat messages
            model: Model name
            stream: Whether to stream
            **kwargs: Additional parameters
        """
        if not self._client:
            await self.initialize()

        active_model = model or self._default_model

        try:
            response = await self._client.chat.completions.create(
                model=active_model, messages=messages, stream=stream, **kwargs
            )

            if stream:
                # Handle streaming
                return await self._process_stream(response)
            else:
                # Handle regular response
                return self._parse_response(response)

        except Exception as e:
            logger.error(f"DeepSeek chat error: {e}")
            raise

    async def chat_stream(
        self, messages: list[dict[str, str]], model: str | None = None, **kwargs
    ) -> AsyncGenerator[dict[str, Any], None]:
        """
        Stream chat completion.

        Yields:
            Response chunks
        """
        if not self._client:
            await self.initialize()

        active_model = model or self._default_model

        try:
            response = await self._client.chat.completions.create(
                model=active_model, messages=messages, stream=True, **kwargs
            )

            async for chunk in response:
                if chunk.choices:
                    yield {
                        "content": chunk.choices[0].delta.content or "",
                        "finish_reason": chunk.choices[0].finish_reason,
                        "model": active_model,
                    }

        except Exception as e:
            logger.error(f"DeepSeek stream error: {e}")
            raise

    def _parse_response(self, response) -> dict[str, Any]:
        """Parse API response."""
        choice = response.choices[0]
        message = choice.message

        result = {
            "content": message.content or "",
            "model": response.model,
            "usage": {
                "prompt_tokens": response.usage.prompt_tokens if response.usage else 0,
                "completion_tokens": (
                    response.usage.completion_tokens if response.usage else 0
                ),
                "total_tokens": response.usage.total_tokens if response.usage else 0,
            },
        }

        # Handle tool calls
        if message.tool_calls:
            result["tool_calls"] = []
            for tc in message.tool_calls:
                result["tool_calls"].append(
                    {
                        "id": tc.id,
                        "name": tc.function.name,
                        "input": json.loads(tc.function.arguments),
                    }
                )

        return result

    async def _process_stream(self, response) -> dict[str, Any]:
        """Process streaming response into final result."""
        content_parts = []
        finish_reason = None
        model = None

        async for chunk in response:
            if chunk.choices:
                choice = chunk.choices[0]

                if choice.delta.content:
                    content_parts.append(choice.delta.content)

                if choice.finish_reason:
                    finish_reason = choice.finish_reason

                if choice.delta.model:
                    model = choice.delta.model

        return {
            "content": "".join(content_parts),
            "model": model or self._default_model,
            "finish_reason": finish_reason,
            "usage": {"total_tokens": 0},
        }

    def get_model_info(self, model_name: str | None = None) -> dict[str, Any]:
        """Get model information."""
        name = model_name or self._default_model
        for m in self.models:
            if m["name"] == name:
                return m
        return {"name": name, "context": 128000, "max_output": 8000}

    def _get_input_schema(self) -> dict[str, Any]:
        return {
            "model": {
                "type": "string",
                "description": "Model name (default: deepseek-v4-flash)",
            }
        }
