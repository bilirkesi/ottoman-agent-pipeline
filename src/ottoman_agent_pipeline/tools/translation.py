"""
Translation Tool - Ottoman Turkish transliteration

Integrates with the ottoman-transliterator package (neural via DeepSeek API,
or rule-based fallback). When no DEEPSEEK_API_KEY is configured, a built-in
UTF-8 character map fallback is used so the tool always returns something
useful instead of failing.
"""

from __future__ import annotations

import logging
import os
from typing import Any

from ottoman_transliterator import (
    OttomanPipelineConfig,
    OttomanTransliterationPipeline,
    TransliterationResult,
)

from .base import BaseTool

logger = logging.getLogger(__name__)

# Built-in rule-based fallback: Arabic script -> Latin letters (correct UTF-8).
_CHAR_MAP: dict[str, str] = {
    "ا": "a",
    "أ": "a",
    "آ": "a",
    "إ": "e",
    "ب": "b",
    "پ": "p",
    "ت": "t",
    "ث": "s",
    "ج": "c",
    "چ": "ç",
    "ح": "h",
    "خ": "h",
    "د": "d",
    "ذ": "z",
    "ر": "r",
    "ز": "z",
    "ژ": "j",
    "س": "s",
    "ش": "ş",
    "ص": "s",
    "ض": "d",
    "ط": "t",
    "ظ": "z",
    "ع": "a",
    "غ": "ğ",
    "ف": "f",
    "ق": "k",
    "ک": "k",
    "گ": "g",
    "ل": "l",
    "م": "m",
    "ن": "n",
    "و": "v",
    "ه": "h",
    "ە": "e",
    "ی": "y",
    "ء": "",
    "ؤ": "u",
    "ئ": "i",
    "ں": "n",
    "ہ": "h",
    "ھ": "h",
    "ٹ": "t",
    "ڈ": "d",
    "ڑ": "r",
    "ے": "e",
    "٠": "0",
    "١": "1",
    "٢": "2",
    "٣": "3",
    "٤": "4",
    "٥": "5",
    "٦": "6",
    "٧": "7",
    "٨": "8",
    "٩": "9",
}

# Built-in reverse map: Latin letters -> Arabic script (simplified).
_REVERSE_MAP: dict[str, str] = {
    "a": "ا",
    "b": "ب",
    "c": "ج",
    "ç": "چ",
    "d": "د",
    "e": "ە",
    "f": "ف",
    "g": "گ",
    "ğ": "غ",
    "h": "ه",
    "ı": "ی",
    "i": "ی",
    "j": "ژ",
    "k": "ک",
    "l": "ل",
    "m": "م",
    "n": "ن",
    "o": "و",
    "ö": "ؤ",
    "p": "پ",
    "r": "ر",
    "s": "س",
    "ş": "ش",
    "t": "ت",
    "u": "و",
    "ü": "و",
    "v": "و",
    "y": "ی",
    "z": "ز",
}


def _rule_based_fallback(text: str) -> str:
    """Map Arabic-script characters to Latin letters (no API required)."""
    return "".join(_CHAR_MAP.get(ch, ch) for ch in text)


def _rule_based_reverse(text: str) -> str:
    """Map Latin letters to Arabic script (simplified, no API required)."""
    return "".join(_REVERSE_MAP.get(ch.lower(), ch) for ch in text)


class TranslationTool(BaseTool):
    """
    Tool for Ottoman Turkish to Modern Turkish transliteration.
    """

    name = "translation"
    description = """
    Ottoman Turkish to Modern Turkish transliteration tool.
    Use this tool to:
    - Convert Ottoman Turkish (Arabic script) to Modern Turkish (Latin script)
    - Get confidence scores for transliteration
    - Process batch transliterations
    - Access NER annotations
    """

    def __init__(
        self, pipeline: str = "hybrid", model: str = "deepseek-v4-flash", **kwargs
    ):
        super().__init__(**kwargs)
        self.pipeline = pipeline
        self.model = model
        self._transliterator: OttomanTransliterationPipeline | None = None

    async def initialize(self) -> None:
        """Initialize transliteration pipeline (lazy API client)."""
        config = OttomanPipelineConfig(
            model=self.model,
            api_key=os.environ.get("DEEPSEEK_API_KEY"),
        )
        self._transliterator = OttomanTransliterationPipeline(config)
        await super().initialize()
        logger.info(f"Translation tool initialized with {self.pipeline} pipeline")

    async def close(self) -> None:
        """Cleanup resources."""
        self._transliterator = None
        await super().close()

    async def execute(
        self,
        action: str = "transliterate",
        text: str = "",
        mode: str = "hybrid",
        batch: bool = False,
        **kwargs,
    ) -> Any:
        """
        Execute transliteration.

        Args:
            action: Operation type (transliterate/batch/analyze/reverse)
            text: Input Ottoman Turkish text
            mode: Transliteration mode (hybrid/neural/nlp)
            batch: Whether to process as batch
        """
        if not self._transliterator:
            await self.initialize()

        actions = {
            "transliterate": self._transliterate,
            "batch": self._batch_transliterate,
            "analyze": self._analyze,
            "reverse": self._reverse,
        }

        if action not in actions:
            raise ValueError(f"Unknown action: {action}")

        return await actions[action](text, mode=mode, **kwargs)

    def _result_to_dict(
        self, text: str, result: TransliterationResult
    ) -> dict[str, Any]:
        """Serialize TransliterationResult to API-friendly dict."""
        return {
            "ottoman": text,
            "modern_turkish": result.modern_turkish,
            "confidence": result.confidence,
            "method": result.method,
            "uncertainty_markers": list(result.uncertainty_markers),
            "ner_tags": dict(result.ner_tags),
            "pos_tags": list(result.pos_tags),
            "metrics": dict(result.metrics),
        }

    async def _transliterate(
        self, text: str, mode: str = "hybrid", **kwargs
    ) -> dict[str, Any]:
        """Transliterate single text with engine, falling back to char map."""
        text = (text or "").strip()
        if not text:
            raise ValueError("Text is required")

        assert self._transliterator is not None
        try:
            result = self._transliterator.transliterate(text, mode=mode)
            return self._result_to_dict(text, result)
        except Exception as e:
            logger.warning(
                f"Transliteration engine failed ({e}); using rule-based fallback"
            )
            return {
                "ottoman": text,
                "modern_turkish": _rule_based_fallback(text),
                "confidence": 0.5,
                "method": "fallback",
                "uncertainty_markers": [],
                "ner_tags": {},
                "pos_tags": [],
                "metrics": {"engine_error": str(e)},
            }

    async def _batch_transliterate(
        self,
        text: str = "",
        texts: list[str] | None = None,
        mode: str = "hybrid",
        **kwargs,
    ) -> list[dict[str, Any]]:
        """Batch transliterate multiple texts (engine has no batch API)."""
        if not texts:
            texts = [text]

        results: list[dict[str, Any]] = []
        for item in texts:
            results.append(await self._transliterate(item, mode=mode, **kwargs))
        return results

    async def _analyze(
        self, text: str = "", entities: bool = True, pos: bool = False, **kwargs
    ) -> dict[str, Any]:
        """Analyze text with NER and POS tagging."""
        result = await self._transliterate(text, **kwargs)

        if "error" in result:
            return result

        if not entities:
            result.pop("ner_tags", None)
        if not pos:
            result.pop("pos_tags", None)

        return result

    async def _reverse(self, text: str = "", **kwargs) -> dict[str, Any]:
        """
        Reverse transliteration: Modern Turkish to Ottoman.
        Uses the engine when available, otherwise the built-in char map.
        """
        if not text:
            raise ValueError("Text is required")

        try:
            # The engine only supports ot-to-tr; emulate reverse with the map.
            ottoman = _rule_based_reverse(text)
            method = "reverse_mapping"
        except Exception as e:  # pragma: no cover
            logger.error(f"Reverse transliteration failed: {e}")
            ottoman = _rule_based_reverse(text)
            method = "reverse_mapping"

        return {
            "modern_turkish": text,
            "ottoman": ottoman,
            "method": method,
            "confidence": 0.5,  # Simplified
        }

    def get_info(self) -> dict[str, Any]:
        """Get tool information."""
        return {
            "name": self.name,
            "pipeline": self.pipeline,
            "model": self.model,
            "supported_modes": ["hybrid", "neural", "nlp"],
            "api_key_configured": bool(os.environ.get("DEEPSEEK_API_KEY")),
        }

    def _get_input_schema(self) -> dict[str, Any]:
        return {
            "action": {
                "type": "string",
                "enum": ["transliterate", "batch", "analyze", "reverse"],
                "description": "Operation to perform",
            },
            "text": {"type": "string", "description": "Input text"},
            "mode": {
                "type": "string",
                "enum": ["hybrid", "neural", "nlp"],
                "description": "Transliteration mode",
            },
        }

    def _get_required_fields(self) -> list[str]:
        return ["action"]


# Module-level singleton
_translation_tool: TranslationTool | None = None


def get_translation_tool() -> TranslationTool:
    """Get the shared translation tool instance."""
    global _translation_tool
    if _translation_tool is None:
        _translation_tool = TranslationTool()
    return _translation_tool
