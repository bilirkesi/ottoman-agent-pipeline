"""
Translation Tool - Ottoman Turkish transliteration
"""

import asyncio
import json
import logging
from typing import Any, Dict, List, Optional

from ottoman_transliterator import OttomanTransliterationPipeline

from .base import BaseTool

logger = logging.getLogger(__name__)


class TranslationTool(BaseTool):
    """
    Tool for Ottoman Turkish to Modern Turkish transliteration.
    
    Integrates with the ottoman-transliterator package.
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
        self,
        pipeline: str = "hybrid",
        model: str = "deepseek-v4-flash",
        **kwargs
    ):
        super().__init__(**kwargs)
        self.pipeline = pipeline
        self.model = model
        self._transliterator: Optional[OttomanTransliterationPipeline] = None
    
    async def initialize(self) -> None:
        """Initialize transliteration pipeline."""
        self._transliterator = OttomanTransliterationPipeline()
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
        **kwargs
    ) -> Any:
        """
        Execute transliteration.
        
        Args:
            action: Operation type
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
            "reverse": self._reverse
        }
        
        if action not in actions:
            raise ValueError(f"Unknown action: {action}")
        
        return await actions[action](text, mode=mode, **kwargs)
    
    async def _transliterate(self, text: str, mode: str = "hybrid", **kwargs) -> Dict[str, Any]:
        """Transliterate single text."""
        if not text:
            raise ValueError("Text is required")
        
        try:
            result = self._transliterator.transliterate(text, mode=mode)
            
            return {
                "ottoman": text,
                "modern_turkish": result.modern_turkish,
                "confidence": result.confidence,
                "method": result.method,
                "uncertain_spans": result.uncertain_spans,
                "chunks": result.chunks
            }
            
        except Exception as e:
            logger.error(f"Transliteration failed: {e}")
            return {
                "ottoman": text,
                "error": str(e)
            }
    
    async def _batch_transliterate(
        self,
        text: str = "",
        texts: Optional[List[str]] = None,
        mode: str = "hybrid",
        **kwargs
    ) -> List[Dict[str, Any]]:
        """Batch transliterate multiple texts."""
        if not texts:
            texts = [text]
        
        try:
            results = self._transliterator.batch_transliterate(texts, mode=mode)
            
            return [
                {
                    "ottoman": r.ottoman,
                    "modern_turkish": r.modern_turkish,
                    "confidence": r.confidence,
                    "method": r.method
                }
                for r in results
            ]
            
        except Exception as e:
            logger.error(f"Batch transliteration failed: {e}")
            return [{"error": str(e)}]
    
    async def _analyze(
        self,
        text: str = "",
        entities: bool = True,
        pos: bool = False,
        **kwargs
    ) -> Dict[str, Any]:
        """Analyze text with NER and POS tagging."""
        result = await self._transliterate(text, **kwargs)
        
        if "error" in result:
            return result
        
        # Add analysis if available
        if entities and hasattr(result, 'entities'):
            result["entities"] = result.entities
        
        if pos and hasattr(result, 'pos_tags'):
            result["pos_tags"] = result.pos_tags
        
        return result
    
    async def _reverse(self, text: str = "", **kwargs) -> Dict[str, Any]:
        """
        Reverse transliteration: Modern Turkish to Ottoman.
        
        Note: This is a simplified implementation.
        Full reverse transliteration requires complex mapping.
        """
        if not text:
            raise ValueError("Text is required")
        
        # Simple reverse mapping (expand in future)
        reverse_map = {
            "ç": "چ",
            "ğ": "غ",
            "ı": "ي",
            "ö": "اوه",
            "ş": "ش",
            "ü": "و",
            "c": "ج",
            "ğ": "غ",
            "ı": "ي",
            "ö": "اوه",
            "ş": "ش",
            "ü": "و"
        }
        
        # Apply mapping
        ottoman = ""
        for char in text.lower():
            ottoman += reverse_map.get(char, char)
        
        return {
            "modern_turkish": text,
            "ottoman": ottoman,
            "method": "reverse_mapping",
            "confidence": 0.5  # Simplified
        }
    
    def get_info(self) -> Dict[str, Any]:
        """Get tool information."""
        return {
            "name": self.name,
            "pipeline": self.pipeline,
            "model": self.model,
            "supported_modes": ["hybrid", "neural", "nlp"]
        }
    
    def _get_input_schema(self) -> Dict[str, Any]:
        return {
            "action": {
                "type": "string",
                "enum": ["transliterate", "batch", "analyze", "reverse"],
                "description": "Operation to perform"
            },
            "text": {
                "type": "string",
                "description": "Input text"
            },
            "mode": {
                "type": "string",
                "enum": ["hybrid", "neural", "nlp"],
                "description": "Transliteration mode"
            }
        }
    
    def _get_required_fields(self) -> List[str]:
        return ["action"]
