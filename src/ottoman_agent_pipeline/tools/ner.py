"""
NER Tool - Named Entity Recognition for Ottoman Turkish
"""

import asyncio
import json
import logging
from typing import Any, Dict, List, Optional

from .base import BaseTool

logger = logging.getLogger(__name__)


class NERTool(BaseTool):
    """
    Tool for Named Entity Recognition in Ottoman Turkish text.
    
    Supports:
    - Person names
    - Locations
    - Organizations
    - Dates
    - Events
    """
    
    name = "ner"
    description = """
    Named Entity Recognition (NER) tool for Ottoman Turkish text.
    Use this tool to:
    - Extract person names
    - Identify locations
    - Detect organizations
    - Recognize dates and events
    """
    
    def __init__(self, model: str = "bert-base-turkish", **kwargs):
        super().__init__(**kwargs)
        self.model = model
        self._ner_model = None
    
    async def initialize(self) -> None:
        """Initialize NER model."""
        try:
            # Import here to avoid circular imports
            from turkicnlp import NLPToolkit
            
            self._ner_model = NLPToolkit(
                language="ottoman",
                model=self.model
            )
            
            logger.info(f"NER model initialized: {self.model}")
            
        except ImportError:
            logger.warning("turkicnlp not available, using mock NER")
            self._ner_model = MockNER()
        
        await super().initialize()
    
    async def close(self) -> None:
        """Cleanup resources."""
        self._ner_model = None
        await super().close()
    
    async def execute(
        self,
        action: str = "extract",
        text: str = "",
        entity_types: Optional[List[str]] = None,
        **kwargs
    ) -> Any:
        """
        Execute NER extraction.
        
        Args:
            action: Operation type
            text: Input text
            entity_types: Types of entities to extract
        """
        if not self._ner_model:
            await self.initialize()
        
        actions = {
            "extract": self._extract_entities,
            "annotate": self._annotate_text,
            "classify": self._classify_text
        }
        
        if action not in actions:
            raise ValueError(f"Unknown action: {action}")
        
        return await actions[action](text, entity_types=entity_types, **kwargs)
    
    async def _extract_entities(
        self,
        text: str,
        entity_types: Optional[List[str]] = None,
        **kwargs
    ) -> List[Dict[str, Any]]:
        """Extract entities from text."""
        if not text:
            raise ValueError("Text is required")
        
        try:
            # Use NER model
            entities = self._ner_model.extract_entities(
                text,
                entity_types=entity_types
            )
            
            return [
                {
                    "text": e.text,
                    "type": e.type,
                    "start": e.start,
                    "end": e.end,
                    "confidence": e.confidence
                }
                for e in entities
            ]
            
        except Exception as e:
            logger.error(f"NER extraction failed: {e}")
            return []
    
    async def _annotate_text(
        self,
        text: str,
        entity_types: Optional[List[str]] = None,
        **kwargs
    ) -> Dict[str, Any]:
        """Annotate text with entities."""
        entities = await self._extract_entities(text, entity_types)
        
        # Add annotations to text
        annotations = []
        for entity in entities:
            annotations.append({
                "start": entity["start"],
                "end": entity["end"],
                "text": entity["text"],
                "type": entity["type"],
                "context": text[max(0, entity["start"]-20):entity["end"]+20]
            })
        
        return {
            "text": text,
            "entities": entities,
            "annotations": annotations,
            "entity_count": len(entities)
        }
    
    async def _classify_text(
        self,
        text: str,
        entity_types: Optional[List[str]] = None,
        **kwargs
    ) -> Dict[str, Any]:
        """Classify text by entity types."""
        entities = await self._extract_entities(text, entity_types)
        
        # Count by type
        type_counts = {}
        for entity in entities:
            etype = entity["type"]
            type_counts[etype] = type_counts.get(etype, 0) + 1
        
        return {
            "text": text,
            "entity_types": type_counts,
            "total_entities": len(entities),
            "entities": entities
        }
    
    def get_info(self) -> Dict[str, Any]:
        """Get tool information."""
        return {
            "name": self.name,
            "model": self.model,
            "supported_entities": ["PERSON", "LOCATION", "ORGANIZATION", "DATE", "EVENT"]
        }
    
    def _get_input_schema(self) -> Dict[str, Any]:
        return {
            "action": {
                "type": "string",
                "enum": ["extract", "annotate", "classify"],
                "description": "Operation to perform"
            },
            "text": {
                "type": "string",
                "description": "Input text"
            },
            "entity_types": {
                "type": "array",
                "items": {"type": "string"},
                "description": "Entity types to extract"
            }
        }
    
    def _get_required_fields(self) -> List[str]:
        return ["action", "text"]


class MockNER:
    """Mock NER for testing when turkicnlp is not available."""
    
    def extract_entities(self, text: str, entity_types: Optional[List[str]] = None) -> List[Dict]:
        """Extract mock entities."""
        # Simple mock implementation
        entities = []
        
        # Look for capitalized words as potential persons
        import re
        persons = re.findall(r'\b[A-Z][a-z]{2,}\b', text)
        for person in persons[:5]:
            entities.append({
                "text": person,
                "type": "PERSON",
                "start": text.find(person),
                "end": text.find(person) + len(person),
                "confidence": 0.7
            })
        
        return entities
