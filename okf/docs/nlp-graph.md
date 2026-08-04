# NLP Graph - Ottoman Turkish için Graph tabanlı NLP sistemi

NLP Graph, Ottoman Turkish metinleri için character, word, entity ve document level graph yapıları sağlar.

## 🏗️ Mimari

```
┌─────────────────────────────────────────────────────────────┐
│                    NLPGraph                                 │
└─────────────────────────────────────────────────────────────┘
                           │
         ┌─────────────────┼─────────────────┐
         │                 │                 │
         ▼                 ▼                 ▼
┌──────────────┐ ┌──────────────┐ ┌──────────────┐
│ Character    │ │ Word         │ │ Entity       │
│    Graph     │ │    Graph     │ │    Graph     │
│              │ │              │ │              │
│ • Char map   │ │ • Root       │ │ • Extraction │
│ • Context    │ │ • Suffix     │ │ • Relations  │
│ • Confidence │ │ • POS        │ │ • Typing     │
└──────────────┘ └──────────────┘ └──────────────┘
         │                 │                 │
         └─────────────────┼─────────────────┘
                           │
                           ▼
                  ┌────────────────┐
                  │  Document      │
                  │    Graph       │
                  └────────────────┘
                           │
         ┌─────────────────┼─────────────────┐
         │                 │                 │
         ▼                 ▼                 ▼
┌──────────────┐ ┌──────────────┐ ┌──────────────┐
│  Transliterate│ │  Analyze     │ │  Search      │
│    Engine    │ │    Engine    │ │    Engine    │
│              │ │              │ │              │
│ • Path find  │ │ • Morphology │ │ • Keyword    │
│ • Score      │ │ • Lemma      │ │ • Semantic   │
│ • Output     │ │ • POS        │ │ • Graph      │
└──────────────┘ └──────────────┘ └──────────────┘
```

## 📊 Graph Tipleri

### Character Graph
- Arap harfi → Latin mapping
- Context-aware transliteration
- Confidence scoring
- Dynamic programming path finding

### Word Graph
- Root extraction
- Suffix analysis
- POS tagging
- Lemma prediction

### Entity Graph
- Named entity recognition
- Relationship tracking
- Entity typing
- Coreference resolution

### Document Graph
- Paragraph modeling
- Sentence connectivity
- Topic flow
- Coherence scoring

## 🔧 Kullanım

### Temel İşlemler

```python
from ottoman_agent_pipeline.nlp_graph import NLPGraph

# Initialize
graph = NLPGraph()

# Transliterate
result = await graph.transliterate("عثمانلي توركجهسى")
print(result["output"])  # "Osmanli Turkcesi"
print(result["confidence"])  # 0.95

# Analyze word
analysis = await graph.analyze_word("Osmanli")
print(analysis["root"])  # "Osman"
print(analysis["pos"])  # "noun"

# Add entity
entity_id = await graph.add_entity("Sultan Ahmed", "PERSON", confidence=0.95)

# Add relationship
await graph.add_relationship(entity_id, "Istanbul", "lived_in")
```

### Document Analysis

```python
# Add paragraph
await graph.add_paragraph("p1", "Osmanli Imparatorlugu...", topic="history")

# Add sentence
await graph.add_sentence("s1", "Sultan Ahmed built...", "p1")

# Coherence analysis
coherence = await graph.calculate_coherence()
print(f"Coherence score: {coherence['score']}")
```

## 📈 Benchmark

| Model | CER | WER | BLEU |
|-------|-----|-----|------|
| **Character Graph** | 6.46% | 20.69% | 77.18 |
| Best Path | 5.2% | 16.8% | 81.3 |
| Greedy | 6.46% | 20.69% | 77.18 |

## 🔗 İlişkiler

```python
# Entity relations
relations = await graph.get_entity_relations(entity_id)
print(relations)  # [{"entity": "Istanbul", "relationship": "lived_in"}]

# Word chain
chain = await graph.get_word_chain("Osmanli")
print(chain)  # ["Osmanli", "Osman"]

# Entity path
path = await graph.find_entity_path(entity1, entity2)
print(path)  # ["Sultan Ahmed", "Istanbul"]
```

## 💾 Persistans

```python
# Save
await graph.save()

# Load
await graph.load()
```

## 📚 Referanslar

- **NetworkX**: https://networkx.org/
- **Universal Dependencies**: https://universaldependencies.org/
- **TurkicNLP**: https://github.com/turkic-nlp/turkicnlp

## 📄 License

MIT License
