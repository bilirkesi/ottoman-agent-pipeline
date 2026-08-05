"""
Reasonix Model - DeepSeek prefix-cache-first model provider

Reasonix, DeepSeek'in prefix-cache mimarisini kullanan OpenAI-uyumlu
bir model sağlayıcısıdır. Aynı system prompt / konuşma öneki tekrar
gönderildiğinde cache hit sağlayarak maliyeti düşürür.
"""

from __future__ import annotations

import logging
from typing import Any, ClassVar

from .deepseek import DeepSeekModel

logger = logging.getLogger(__name__)


class ReasonixModel(DeepSeekModel):
    """
    Reasonix model provider - DeepSeek prefix-cache mimarisi.

    DeepSeekModel'in OpenAI-uyumlu API'sini kullanır; farklı olarak
    cache-bilinci parametreler ekler:

    - cache_enabled: Prefix-cache optimizasyonu (varsayılan: True)
    - cacheable_prefix: Tekrar kullanılacak sistem promptu/önek
    """

    name = "reasonix"
    description = "DeepSeek Reasonix model provider with prefix-cache optimization"

    DEFAULT_MODELS: ClassVar[list[dict[str, Any]]] = [
        {
            "name": "reasonix-v4-flash",
            "context": 1000000,
            "max_output": 384000,
            "cost_per_1m": {"input": 0.14, "output": 0.28},
        },
        {
            "name": "deepseek-v4-flash",
            "context": 1000000,
            "max_output": 384000,
            "cost_per_1m": {"input": 0.14, "output": 0.28},
        },
    ]

    def __init__(
        self,
        api_key: str | None = None,
        base_url: str | None = None,
        models: list[dict[str, Any]] | None = None,
        cache_enabled: bool = True,
        cacheable_prefix: str | None = None,
        **kwargs,
    ):
        super().__init__(
            api_key=api_key,
            base_url=base_url or "https://api.deepseek.com/v1",
            models=models or self.DEFAULT_MODELS,
            **kwargs,
        )
        self.cache_enabled = cache_enabled
        self.cacheable_prefix = cacheable_prefix
        self._default_model = "deepseek-v4-flash"

    async def chat(
        self,
        messages: list[dict[str, str]],
        model: str | None = None,
        **kwargs,
    ) -> dict[str, Any]:
        """
        Chat completion - prefix-cache bilinciyle.

        cacheable_prefix verildiğinde system mesajı olarak öne eklenir,
        böylece tekrarlanan isteklerde provider prefix-cache'ten yanıt verir.
        """
        if self.cache_enabled and self.cacheable_prefix and messages:
            messages = [
                {"role": "system", "content": self.cacheable_prefix},
                *messages,
            ]

        return await super().chat(messages, model=model, **kwargs)

    def get_info(self) -> dict[str, Any]:
        """Model bilgisi."""
        return {
            "name": self.name,
            "cache_enabled": self.cache_enabled,
            "cacheable_prefix": bool(self.cacheable_prefix),
            "models": [m.get("name") for m in self.models],
        }
