"""
NLP Graph - Ottoman Turkish için Graph tabanlı NLP sistemi

Özellikler:
- Character Graph: Transliterasyon mapping
- Word Graph: Morphological analysis
- Entity Graph: Named entity recognition
- Document Graph: Coherence analysis
"""

from __future__ import annotations

import json
import logging
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

import aiofiles
import networkx as nx

logger = logging.getLogger(__name__)


@dataclass
class GraphNode:
    """Graph düğümü"""

    id: str
    type: str  # char, word, entity, paragraph, sentence
    text: str
    metadata: dict[str, Any] = field(default_factory=dict)
    confidence: float = 1.0
    embeddings: list[float] | None = None

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "type": self.type,
            "text": self.text,
            "metadata": self.metadata,
            "confidence": self.confidence,
            "embeddings": self.embeddings,
        }


@dataclass
class GraphEdge:
    """Graph kenarı"""

    source: str
    target: str
    type: str  # map, contains, related_to, coherent
    weight: float = 1.0
    metadata: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict:
        return {
            "source": self.source,
            "target": self.target,
            "type": self.type,
            "weight": self.weight,
            "metadata": self.metadata,
        }


class CharacterGraph:
    """
    Character-level graph for transliteration

    Kullanım:
    - Arap harfi → Latin mapping
    - Context-aware transliteration
    - Confidence scoring
    - Uncertainty tracking
    """

    def __init__(self):
        self.graph = nx.DiGraph()
        self.char_mappings: dict[str, list[dict]] = {}
        self.context_rules: dict[str, dict] = {}

        # Initialize with common mappings
        self._init_mappings()

    def _init_mappings(self):
        """Default mapping'leri başlat"""
        # Common Ottoman Turkish character mappings
        mappings = {
            "ا": [
                {"text": "a", "confidence": 0.95, "context": "initial"},
                {"text": "ə", "confidence": 0.85, "context": "medial"},
            ],
            "ب": [{"text": "b", "confidence": 0.98}],
            "ت": [{"text": "t", "confidence": 0.98}],
            "ث": [{"text": "s", "confidence": 0.95}],
            "ج": [{"text": "c", "confidence": 0.95}],
            "چ": [{"text": "ç", "confidence": 0.98}],
            "ح": [{"text": "h", "confidence": 0.90}],
            "خ": [{"text": "x", "confidence": 0.95}],
            "د": [{"text": "d", "confidence": 0.98}],
            "ذ": [{"text": "z", "confidence": 0.95}],
            "ر": [{"text": "r", "confidence": 0.98}],
            "ز": [{"text": "z", "confidence": 0.98}],
            "س": [{"text": "s", "confidence": 0.98}],
            "ش": [{"text": "ş", "confidence": 0.98}],
            "ص": [{"text": "s", "confidence": 0.90, "note": "emphasized"}],
            "ض": [{"text": "d", "confidence": 0.90, "note": "emphasized"}],
            "ط": [{"text": "t", "confidence": 0.90, "note": "emphasized"}],
            "ظ": [{"text": "z", "confidence": 0.90, "note": "emphasized"}],
            "ع": [{"text": "a", "confidence": 0.85}, {"text": "ə", "confidence": 0.80}],
            "غ": [{"text": "ğ", "confidence": 0.95}],
            "ف": [{"text": "f", "confidence": 0.98}],
            "ق": [{"text": "k", "confidence": 0.95}],
            "ک": [{"text": "k", "confidence": 0.98}],
            "گ": [{"text": "g", "confidence": 0.98}],
            "ل": [{"text": "l", "confidence": 0.98}],
            "م": [{"text": "m", "confidence": 0.98}],
            "ن": [{"text": "n", "confidence": 0.98}],
            "و": [
                {"text": "v", "confidence": 0.90},
                {"text": "o", "confidence": 0.85},
                {"text": "u", "confidence": 0.85},
            ],
            "ه": [{"text": "h", "confidence": 0.95}, {"text": "e", "confidence": 0.90}],
            "ء": [{"text": "'", "confidence": 0.70}],
            "ي": [{"text": "y", "confidence": 0.95}, {"text": "i", "confidence": 0.90}],
            "ى": [{"text": "ı", "confidence": 0.95}, {"text": "i", "confidence": 0.90}],
            "ئ": [{"text": "e", "confidence": 0.85}, {"text": "ə", "confidence": 0.80}],
        }

        for char, variants in mappings.items():
            self.add_char_mapping(char, variants)

    def add_char_mapping(self, arabic_char: str, variants: list[dict]):
        """Character mapping ekle"""
        node_id = f"char_{arabic_char}"

        # Add node
        self.graph.add_node(node_id, type="char", arabic=arabic_char, variants=variants)

        # Add edges to variants
        for i, variant in enumerate(variants):
            variant_id = f"variant_{arabic_char}_{i}"
            self.graph.add_node(
                variant_id,
                type="variant",
                text=variant["text"],
                confidence=variant.get("confidence", 0.9),
            )
            self.graph.add_edge(
                node_id,
                variant_id,
                type="map",
                weight=variant.get("confidence", 0.9),
                metadata=variant,
            )

        # Store mapping
        self.char_mappings[arabic_char] = variants

    def transliterate(self, text: str, use_best_path: bool = True) -> dict:
        """
        Transliterasyon yap

        Args:
            text: Arap harfli metin
            use_best_path: En iyi yolu kullan (dynamic programming)

        Returns:
            Transliteration result with confidence scores
        """
        if not text:
            return {"text": "", "confidence": 1.0, "method": "empty"}

        # Method 1: Best path (dynamic programming)
        if use_best_path:
            result = self._best_path_transliteration(text)
        else:
            result = self._greedy_transliteration(text)

        return result

    def _best_path_transliteration(self, text: str) -> dict:
        """En iyi yol bul (dynamic programming)"""
        chars = list(text)
        n = len(chars)

        # DP table
        dp = [{} for _ in range(n + 1)]
        dp[0] = {"path": [], "confidence": 1.0}

        for i in range(n):
            char = chars[i]

            if char in self.char_mappings:
                variants = self.char_mappings[char]

                for variant in variants:
                    variant_text = variant["text"]
                    confidence = variant.get("confidence", 0.9)

                    # Update DP
                    new_confidence = dp[i]["confidence"] * confidence
                    new_path = dp[i]["path"] + [variant_text]

                    if i + 1 not in dp or new_confidence > dp[i + 1].get(
                        "confidence", 0
                    ):
                        dp[i + 1] = {"path": new_path, "confidence": new_confidence}
            else:
                # Unknown char, pass through
                dp[i + 1] = {
                    "path": dp[i]["path"] + [char],
                    "confidence": dp[i]["confidence"] * 0.5,
                }

        # Get best result
        result = dp[n]
        transliterated = "".join(result["path"])

        return {
            "input": text,
            "output": transliterated,
            "confidence": result["confidence"],
            "method": "best_path",
            "chars_processed": n,
        }

    def _greedy_transliteration(self, text: str) -> dict:
        """Greedy transliteration"""
        chars = list(text)
        result = []
        total_confidence = 1.0

        for char in chars:
            if char in self.char_mappings:
                # Get best variant
                variants = self.char_mappings[char]
                best = max(variants, key=lambda v: v.get("confidence", 0))
                result.append(best["text"])
                total_confidence *= best.get("confidence", 0.9)
            else:
                result.append(char)
                total_confidence *= 0.5

        return {
            "input": text,
            "output": "".join(result),
            "confidence": total_confidence,
            "method": "greedy",
            "chars_processed": len(chars),
        }

    def get_alternatives(self, char: str, limit: int = 5) -> list[dict]:
        """Character alternatifleri"""
        if char not in self.char_mappings:
            return []

        variants = self.char_mappings[char]
        return sorted(variants, key=lambda v: v.get("confidence", 0), reverse=True)[
            :limit
        ]

    def get_graph_stats(self) -> dict:
        """Graph istatistikleri"""
        return {
            "total_nodes": self.graph.number_of_nodes(),
            "total_edges": self.graph.number_of_edges(),
            "char_mappings": len(self.char_mappings),
            "node_types": (
                dict(self.graph.nodes(data="type")) if self.graph.nodes else {}
            ),
        }


class WordGraph:
    """
    Word-level graph for morphological analysis

    Özellikler:
    - Root extraction
    - Suffix analysis
    - POS tagging
    - Lemma prediction
    """

    def __init__(self):
        self.graph = nx.DiGraph()
        self.word_cache: dict[str, dict] = {}

    def add_word(
        self,
        word: str,
        root: str,
        pos: str,
        suffixes: list[str] | None = None,
        confidence: float = 0.9,
    ):
        """Kelime ekle"""
        node_id = f"word_{word}"

        self.graph.add_node(
            node_id,
            type="word",
            text=word,
            root=root,
            pos=pos,
            suffixes=suffixes or [],
            confidence=confidence,
        )

        # Connect to root
        root_id = f"root_{root}"
        self.graph.add_node(root_id, type="root", text=root, pos=pos)
        self.graph.add_edge(node_id, root_id, type="derives_from", weight=confidence)

        # Cache
        self.word_cache[word] = {"root": root, "pos": pos, "suffixes": suffixes or []}

    def analyze(self, word: str) -> dict:
        """Kelime analizi"""
        if word in self.word_cache:
            return self.word_cache[word]

        # Try to infer from graph
        node_id = f"word_{word}"
        if self.graph.has_node(node_id):
            node_data = self.graph.nodes[node_id]
            return {
                "word": word,
                "root": node_data.get("root", word),
                "pos": node_data.get("pos", "unknown"),
                "suffixes": node_data.get("suffixes", []),
            }

        return {"word": word, "root": word, "pos": "unknown", "suffixes": []}

    def get_word_chain(self, word: str) -> list[str]:
        """Kelime zinciri (kök → türetilmiş kelimeler)"""
        node_id = f"word_{word}"
        if not self.graph.has_node(node_id):
            return [word]

        chain = [word]
        for successor in self.graph.successors(node_id):
            if self.graph.nodes[successor].get("type") == "root":
                chain.append(self.graph.nodes[successor]["text"])

        return chain

    def get_graph_stats(self) -> dict:
        """Graph istatistikleri"""
        return {
            "total_nodes": self.graph.number_of_nodes(),
            "total_edges": self.graph.number_of_edges(),
            "words": len(
                [n for n, d in self.graph.nodes(data=True) if d.get("type") == "word"]
            ),
            "roots": len(
                [n for n, d in self.graph.nodes(data=True) if d.get("type") == "root"]
            ),
        }


class EntityGraph:
    """
    Named Entity Recognition için graph

    Özellikler:
    - Entity extraction
    - Relationship tracking
    - Entity typing
    - Coreference resolution
    """

    def __init__(self):
        self.graph = nx.Graph()
        self.word_cache: dict[str, Any] = {}
        self.entity_types = {
            "PERSON",
            "LOCATION",
            "ORGANIZATION",
            "DATE",
            "EVENT",
            "TITLE",
        }

    def add_entity(
        self,
        text: str,
        entity_type: str,
        start: int = 0,
        end: int = 0,
        confidence: float = 0.9,
        metadata: dict | None = None,
    ):
        """Entity ekle"""
        node_id = f"entity_{start}_{end}_{text[:20]}"

        self.graph.add_node(
            node_id,
            type="entity",
            text=text,
            entity_type=entity_type,
            span=(start, end),
            confidence=confidence,
            metadata=metadata or {},
        )

        return node_id

    def add_relationship(
        self,
        entity1_id: str,
        entity2_id: str,
        relationship: str,
        confidence: float = 0.8,
    ):
        """İlişki ekle"""
        if entity1_id not in self.graph or entity2_id not in self.graph:
            raise ValueError("Entity not found")

        self.graph.add_edge(
            entity1_id, entity2_id, type=relationship, weight=confidence
        )

    def get_entity(self, entity_id: str) -> dict | None:
        """Entity getir"""
        if entity_id not in self.graph:
            return None

        node_data = self.graph.nodes[entity_id]
        return {
            "id": entity_id,
            "text": node_data.get("text", ""),
            "entity_type": node_data.get("entity_type", ""),
            "confidence": node_data.get("confidence", 0.0),
            "metadata": node_data.get("metadata", {}),
        }

    def get_entity_relations(self, entity_id: str) -> list[dict]:
        """Entity ilişkileri"""
        if entity_id not in self.graph:
            return []

        relations = []
        for neighbor in self.graph.neighbors(entity_id):
            edge_data = self.graph.edges[entity_id, neighbor]
            neighbor_data = self.graph.nodes[neighbor]

            relations.append(
                {
                    "entity": neighbor_data.get("text", ""),
                    "entity_type": neighbor_data.get("entity_type", ""),
                    "relationship": edge_data.get("type", ""),
                    "confidence": edge_data.get("weight", 0.0),
                }
            )

        return relations

    def get_entities_by_type(self, entity_type: str) -> list[dict]:
        """Tip bazında entity'ler"""
        entities = []
        for node_id, data in self.graph.nodes(data=True):
            if data.get("entity_type") == entity_type:
                entities.append(
                    {
                        "id": node_id,
                        "text": data.get("text", ""),
                        "confidence": data.get("confidence", 0.0),
                    }
                )
        return entities

    def find_entity_path(self, entity1_id: str, entity2_id: str) -> list[str] | None:
        """Entity'ler arası yol"""
        try:
            path = nx.shortest_path(self.graph, entity1_id, entity2_id)
            return [self.graph.nodes[n].get("text", n) for n in path]
        except nx.NetworkXNoPath:
            return None

    def get_graph_stats(self) -> dict:
        """Graph istatistikleri"""
        entity_counts = {}
        for node_id, data in self.graph.nodes(data=True):
            etype = data.get("entity_type", "unknown")
            entity_counts[etype] = entity_counts.get(etype, 0) + 1

        return {
            "total_nodes": self.graph.number_of_nodes(),
            "total_edges": self.graph.number_of_edges(),
            "entities_by_type": entity_counts,
        }


class DocumentGraph:
    """
    Document-level graph for coherence analysis

    Özellikler:
    - Paragraph modeling
    - Sentence connectivity
    - Topic flow
    - Coherence scoring
    """

    def __init__(self):
        self.graph = nx.DiGraph()
        self.paragraphs: dict[str, dict] = {}
        self.sentences: dict[str, dict] = {}

    def add_paragraph(
        self,
        para_id: str,
        text: str,
        topic: str = "",
        embeddings: list[float] | None = None,
    ):
        """Paragraph ekle"""
        self.graph.add_node(
            para_id, type="paragraph", text=text, topic=topic, embeddings=embeddings
        )

        self.paragraphs[para_id] = {"text": text, "topic": topic, "sentence_count": 0}

    def add_sentence(
        self, sent_id: str, text: str, para_id: str, pos_tags: list[str] | None = None
    ):
        """Sentence ekle"""
        self.graph.add_node(
            sent_id, type="sentence", text=text, pos_tags=pos_tags or []
        )

        self.graph.add_edge(para_id, sent_id, type="contains")

        if para_id in self.paragraphs:
            self.paragraphs[para_id]["sentence_count"] += 1

    def calculate_coherence(self) -> dict:
        """Coherence skoru hesapla"""
        if len(self.paragraphs) < 2:
            return {"score": 1.0, "method": "single_paragraph"}

        # Calculate paragraph similarity
        para_ids = list(self.paragraphs.keys())
        similarities = []

        for i in range(len(para_ids) - 1):
            para1 = para_ids[i]
            para2 = para_ids[i + 1]

            # Topic similarity
            topic1 = self.paragraphs[para1].get("topic", "")
            topic2 = self.paragraphs[para2].get("topic", "")

            if topic1 and topic2:
                # Simple overlap
                words1 = set(topic1.lower().split())
                words2 = set(topic2.lower().split())
                similarity = len(words1 & words2) / max(len(words1), len(words2), 1)
                similarities.append(similarity)

        if not similarities:
            return {"score": 0.5, "method": "no_topic_data"}

        avg_similarity = sum(similarities) / len(similarities)

        return {
            "score": avg_similarity,
            "method": "topic_similarity",
            "paragraph_count": len(para_ids),
            "similarities": similarities,
        }

    def get_flow_analysis(self) -> dict:
        """Akış analizi"""
        # Find paragraph sequence
        para_ids = [
            pid
            for pid, data in self.graph.nodes(data=True)
            if data.get("type") == "paragraph"
        ]

        # Calculate transitions
        transitions = []
        for i in range(len(para_ids) - 1):
            para1 = para_ids[i]
            para2 = para_ids[i + 1]

            # Check if connected
            if self.graph.has_edge(para1, para2):
                transitions.append({"from": para1, "to": para2, "connected": True})
            else:
                transitions.append({"from": para1, "to": para2, "connected": False})

        return {
            "paragraphs": para_ids,
            "transitions": transitions,
            "total_transitions": len(transitions),
            "connected_transitions": sum(1 for t in transitions if t["connected"]),
        }

    def get_graph_stats(self) -> dict:
        """Graph istatistikleri"""
        return {
            "total_nodes": self.graph.number_of_nodes(),
            "total_edges": self.graph.number_of_edges(),
            "paragraphs": len(self.paragraphs),
            "total_sentences": sum(
                p.get("sentence_count", 0) for p in self.paragraphs.values()
            ),
        }


class NLPGraph:
    """
    Ana NLP Graph sınıfı - tüm alt graph'ları yönetir
    """

    def __init__(self, db_path: str = "./data/nlp_graph.db"):
        self.db_path = Path(db_path)
        self.db_path.parent.mkdir(parents=True, exist_ok=True)

        # Sub-graphs
        self.char_graph = CharacterGraph()
        self.word_graph = WordGraph()
        self.entity_graph = EntityGraph()
        self.doc_graph = DocumentGraph()
        self.word_cache: dict[str, Any] = {}

        # Cross-graph relationships
        self.cross_graph = nx.Graph()

        logger.info("NLPGraph initialized")

    async def transliterate(self, text: str, use_best_path: bool = True) -> dict:
        """Transliterasyon"""
        return self.char_graph.transliterate(text, use_best_path)

    async def analyze_word(self, word: str) -> dict:
        """Kelime analizi"""
        return self.word_graph.analyze(word)

    async def add_entity(
        self,
        text: str,
        entity_type: str,
        start: int = 0,
        end: int = 0,
        confidence: float = 0.9,
    ) -> str:
        """Entity ekle"""
        return self.entity_graph.add_entity(text, entity_type, start, end, confidence)

    async def add_relationship(
        self,
        entity1_id: str,
        entity2_id: str,
        relationship: str,
        confidence: float = 0.8,
    ):
        """İlişki ekle"""
        self.entity_graph.add_relationship(
            entity1_id, entity2_id, relationship, confidence
        )

        # Cross-graph connection
        self.cross_graph.add_edge(entity1_id, entity2_id, type=relationship)

    async def add_paragraph(
        self,
        para_id: str,
        text: str,
        topic: str = "",
        embeddings: list[float] | None = None,
    ):
        """Paragraph ekle"""
        self.doc_graph.add_paragraph(para_id, text, topic, embeddings)

    async def add_sentence(
        self, sent_id: str, text: str, para_id: str, pos_tags: list[str] | None = None
    ):
        """Sentence ekle"""
        self.doc_graph.add_sentence(sent_id, text, para_id, pos_tags)

    async def get_all_stats(self) -> dict:
        """Tüm graph istatistikleri"""
        return {
            "character_graph": self.char_graph.get_graph_stats(),
            "word_graph": self.word_graph.get_graph_stats(),
            "entity_graph": self.entity_graph.get_graph_stats(),
            "document_graph": self.doc_graph.get_graph_stats(),
            "cross_graph": {
                "nodes": self.cross_graph.number_of_nodes(),
                "edges": self.cross_graph.number_of_edges(),
            },
        }

    async def get_transliteration_result(self, text: str) -> dict:
        """Transliterasyon sonucu"""
        result = self.char_graph.transliterate(text)

        # Add word analysis
        words = result["output"].split()
        word_analysis = []
        for word in words:
            analysis = self.word_graph.analyze(word)
            word_analysis.append(analysis)

        result["word_analysis"] = word_analysis
        return result

    async def save(self):
        """Graph'i kaydet"""
        data = {
            "char_graph": {
                "mappings": self.char_graph.char_mappings,
                "context_rules": self.char_graph.context_rules,
            },
            "word_graph": {"words": self.word_cache},
            "entity_graph": {"entities": dict(self.entity_graph.word_cache)},
        }

        async with aiofiles.open(self.db_path, "w", encoding="utf-8") as f:
            await f.write(json.dumps(data, ensure_ascii=False, indent=2))

    async def load(self):
        """Graph'i yükle"""
        if not self.db_path.exists():
            return

        try:
            async with aiofiles.open(self.db_path, "r", encoding="utf-8") as f:
                data = json.loads(await f.read())

            # Restore char graph
            if "char_graph" in data:
                self.char_graph.char_mappings = data["char_graph"].get("mappings", {})
                self.char_graph.context_rules = data["char_graph"].get(
                    "context_rules", {}
                )

            # Restore word graph
            if "word_graph" in data:
                self.word_graph.word_cache = data["word_graph"].get("words", {})

            # Restore entity graph
            if "entity_graph" in data:
                self.entity_graph.word_cache = data["entity_graph"].get("entities", {})

            logger.info(f"Loaded NLPGraph from {self.db_path}")

        except Exception as e:
            logger.error(f"Error loading NLPGraph: {e}")


# Singleton
_nlp_graph = None


def get_nlp_graph() -> NLPGraph:
    """Global NLPGraph instance"""
    global _nlp_graph
    if _nlp_graph is None:
        _nlp_graph = NLPGraph()
    return _nlp_graph


# Module exports
__all__ = [
    "CharacterGraph",
    "DocumentGraph",
    "EntityGraph",
    "GraphEdge",
    "GraphNode",
    "NLPGraph",
    "WordGraph",
    "get_nlp_graph",
]
