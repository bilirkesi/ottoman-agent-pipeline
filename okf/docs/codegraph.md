# CodeGraph - Knowledge Graph ve Code Intelligence

CodeGraph, Ottoman Agent Pipeline için code intelligence, dependency tracking ve knowledge graph sistemi sağlar.

## 🏗️ Mimari

```
┌─────────────────────────────────────────────────────────────┐
│                    CodeGraph Engine                        │
└─────────────────────────────────────────────────────────────┘
                           │
         ┌─────────────────┼─────────────────┐
         │                 │                 │
         ▼                 ▼                 ▼
┌──────────────┐ ┌──────────────┐ ┌──────────────┐
│  Dependency  │ │  Code        │ │  Knowledge   │
│    Graph     │ │  Intelligence│ │    Graph     │
│              │ │              │ │              │
│ • Imports    │ │ • Call Graph │ │ • Agents     │
│ • Calls      │ │ • Call Chain │ │ • Tools      │
│ • Depends    │ │ • Impact     │ │ • Models     │
│              │ │   Analysis   │ │ • Files      │
└──────────────┘ └──────────────┘ └──────────────┘
         │                 │                 │
         └─────────────────┼─────────────────┘
                           │
                           ▼
                  ┌────────────────┐
                  │  Storage       │
                  │  (JSON/SQLite) │
                  └────────────────┘
```

## 📊 Graph Yapısı

### Node Tipleri
| Tip | Açıklama | Örnek |
|-----|----------|-------|
| `file` | Python dosyası | `pipeline.py` |
| `class` | Sınıf tanımı | `AgentOrchestrator` |
| `function` | Fonksiyon tanımı | `transliterate()` |
| `module` | Python modülü | `ottoman_agent_pipeline` |
| `agent` | Agent tanımı | `CodeAgent` |
| `tool` | Tool tanımı | `FileSystemTool` |
| `model` | Model tanımı | `DeepSeekModel` |

### Edge Tipleri
| Tip | Açıklama | Yön |
|-----|----------|-----|
| `imports` | Import ilişkisi | A → B |
| `calls` | Çağrı ilişkisi | A → B |
| `depends_on` | Bağımlılık | A → B |
| `owns` | Sahiplik | A → B |
| `uses` | Kullanım | A → B |
| `related_to` | İlişki | A ↔ B |

## 🔧 Kullanım

### Temel İşlemler

```python
from ottoman_agent_pipeline.codegraph import CodeGraph

# Create graph
graph = CodeGraph(db_path="./data/codegraph.db")

# Add node
from ottoman_agent_pipeline.codegraph import GraphNode
node = GraphNode(
    id="file-pipeline",
    type="file",
    name="pipeline.py",
    content=open("src/.../pipeline.py").read(),
    metadata={"file_path": "src/.../pipeline.py"}
)
await graph.add_node(node)

# Add edge
from ottoman_agent_pipeline.codegraph import GraphEdge
edge = GraphEdge(
    source="file-pipeline",
    target="class-orchestrator",
    type="imports",
    weight=1.0
)
await graph.add_edge(edge)

# Query
callers = await graph.get_callers("class-orchestrator")
callees = await graph.get_callees("class-orchestrator")
deps = await graph.get_dependencies("file-pipeline")
```

### Agent Analizi

```python
# Agent'ın kullandığı tool'lar
result = await graph.get_agent_tool_usage("agent-code")
print(f"Tools: {result['tools']}")
print(f"Models: {result['models']}")

# Impact analysis
result = await graph.get_impact_analysis("class-orchestrator")
print(f"Affected: {result['affected_count']}")
print(f"Upstream: {result['upstream_count']}")
```

### Code Intelligence

```python
# Call graph
callers = await graph.get_callers("function-transliterate")
callees = await graph.get_callees("function-transliterate")

# Shortest path
path = await graph.find_shortest_path("file-pipeline", "class-orchestrator")
print(f"Path: {path}")

# Circular dependencies
cycles = await graph.get_circular_dependencies()
print(f"Cycles: {cycles}")
```

## 📈 Graph İstatistikleri

```python
# Graph stats
stats = await graph.get_graph_stats()
print(f"Nodes: {stats['total_nodes']}")
print(f"Edges: {stats['total_edges']}")
print(f"Density: {stats['density']}")
print(f"Avg Degree: {stats['average_degree']}")

# Nodes by type
for type, count in stats['nodes_by_type'].items():
    print(f"{type}: {count}")
```

## 🔍 Arama

```python
# Search nodes
results = await graph.search_nodes("transliterate", limit=10)
for node in results:
    print(f"{node.name} ({node.type})")

# Get by type
files = await graph.get_all_nodes_of_type("file")
agents = await graph.get_all_nodes_of_type("agent")
```

## 💾 Persistans

```python
# Save graph
await graph.save()

# Export to JSON
json_data = await graph.export_to_json()
with open("codegraph.json", "w") as f:
    f.write(json_data)

# Import from JSON
with open("codegraph.json", "r") as f:
    await graph.import_from_json(f.read())
```

## 🔌 API Endpoints

### Health
```http
GET /api/v1/codegraph/health
```

### Stats
```http
GET /api/v1/codegraph/stats
```

### Nodes
```http
GET /api/v1/codegraph/nodes
GET /api/v1/codegraph/nodes/{node_id}
POST /api/v1/codegraph/nodes
DELETE /api/v1/codegraph/nodes/{node_id}
```

### Edges
```http
GET /api/v1/codegraph/edges
POST /api/v1/codegraph/edges
DELETE /api/v1/codegraph/edges/{source}/{target}
```

### Queries
```http
GET /api/v1/codegraph/analyze/impact/{node_id}
GET /api/v1/codegraph/analyze/dependencies/{node_id}
GET /api/v1/codegraph/analyze/circular
GET /api/v1/codegraph/agent/{agent_id}/tools
GET /api/v1/codegraph/model/{model_id}/calls
```

### Search
```http
GET /api/v1/codegraph/search?q=transliterate&limit=10
```

## 🧪 Benchmark

| Metric | Value |
|--------|-------|
| **Node Capacity** | 100,000+ |
| **Edge Capacity** | 1,000,000+ |
| **Query Latency** | < 100ms |
| **Graph Build** | ~1s/1000 nodes |
| **Memory Usage** | ~50MB (10k nodes) |

## 📚 Referanslar

- **NetworkX**: https://networkx.org/
- **CodeGraph Concept**: Inspired by GitHub's code mapping
- **Dependency Analysis**: Static analysis techniques

## 📄 License

MIT License
