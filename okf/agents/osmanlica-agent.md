---
name: osmanlica-agent
version: 0.1.0
family: nlp
type: transliteration
status: production
updated: 2026-08-04
---

# Osmanlica Agent

Ottoman Turkish to Modern Turkish transliteration agent.

## Overview

Osmanlica Agent, Osmanlı Türkçesi metinleri Modern Türkçeye transliterate eden bir AI ajanıdır. DeepSeek V4 Flash, DB-Mentat Gateway ve TurkicNLP entegrasyonları ile çalışır.

## Capabilities

- **Transliteration**: Arap harfli Osmanlı Türkçesi → Latin Türkçe
- **Reverse Transliteration**: Latin Türkçe → Arap harfli Osmanlı
- **NER**: Named Entity Recognition (kişi, yer, kuruluş)
- **Analysis**: Metin analizi, confidence scoring
- **Batch Processing**: Toplu işleme desteği
- **Workflow**: Visual workflow execution
- **Key Management**: BYOK ile güvenli API key yönetimi

## Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    Agent Orchestrator                       │
└─────────────────────────────────────────────────────────────┘
                           │
         ┌─────────────────┼─────────────────┐
         │                 │                 │
         ▼                 ▼                 ▼
┌──────────────┐ ┌──────────────┐ ┌──────────────┐
│  Code Agent  │ │  Test Agent  │ │ Deploy Agent │
│              │ │              │ │              │
│ • Implement  │ │ • Unit Test  │ │ • Build      │
│ • Refactor   │ │ • Coverage   │ │ • Publish    │
│ • Review     │ │ • Benchmark  │ │ • Release    │
└──────────────┘ └──────────────┘ └──────────────┘
         │                 │                 │
         └─────────────────┼─────────────────┘
                           │
                           ▼
              ┌────────────────────────┐
              │      Agent Bus         │
              │    (Message Queue)     │
              └────────────────────────┘
                           │
         ┌─────────────────┼─────────────────┐
         │                 │                 │
         ▼                 ▼                 ▼
┌──────────────┐ ┌──────────────┐ ┌──────────────┐
│ Research     │ │   Docs       │ │   Tools      │
│  Agent       │ │  Agent       │ │              │
│              │ │              │ │ • Filesystem │
│ • Web Search │ │ • README     │ │ • Web Search │
│ • Papers     │ │ • API Docs   │ │ • Translation│
│ • Analysis   │ │ • Tutorials  │ │ • NER        │
└──────────────┘ └──────────────┘ └──────────────┘
                           │
                           ▼
              ┌────────────────────────┐
              │    Model Providers     │
              │                        │
              │ • DeepSeek V4 Flash    │
              │ • DB-Mentat Gateway    │
              │ • Reasonix (Cache)     │
              └────────────────────────┘
```

## Tools

| Tool | Açıklama | Kullanım |
|------|----------|----------|
| `filesystem` | Dosya okuma/yazma | `read_file`, `write_file` |
| `web_search` | Web arama | `search`, `fetch` |
| `translation` | Transliterasyon | `transliterate`, `batch` |
| `ner` | Varlık çıkarımı | `extract`, `annotate` |

## Models

| Model | Sağlayıcı | Özellikler |
|-------|-----------|------------|
| `deepseek-v4-flash` | DeepSeek API | 1M context, $0.14/1M |
| `deepseek-v4-pro` | DeepSeek API | 128K context, powerful |
| `gateway` | DB-Mentat | Multi-provider routing |
| `reasonix` | DeepSeek | Prefix-cache optimized |

## Configuration

```yaml
agent:
  name: "osmanlica-agent"
  version: "0.1.0"
  
models:
  default: "deepseek-v4-flash"
  providers:
    deepseek:
      api_key: "${DEEPSEEK_API_KEY}"
    gateway:
      url: "${GATEWAY_URL}"
    reasonix:
      cache_enabled: true

tools:
  translation:
    pipeline: "hybrid"
    confidence_threshold: 0.7
```

## Usage

### CLI
```bash
# Chat
ottoman-agent chat "عثمانلي توركجهسى"

# Transliterate
ottoman-agent translate "بسم الله"

# Analyze
ottoman-agent analyze "عثمانlı توركجهسى"

# Agent takımı
ottoman-agent agents

# Pipeline
ottoman-agent pipeline --type full
```

### Python
```python
from ottoman_agent_pipeline import AgentOrchestrator

orch = AgentOrchestrator()
await orch.initialize()

result = await orch.chat("عثمانli توركجهسى")
print(result.output)
```

### Desktop App
```bash
cd desktop
npm install
npm start
```

### Mobile App
```bash
cd mobile
npm install
npx expo start
```

## Performance

| Metric | Value |
|--------|-------|
| **CER** | < 5% |
| **WER** | < 15% |
| **BLEU** | > 80 |
| **F1-NER** | 83.8% |
| **Cache Hit Rate** | 99.82% (Reasonix) |

## Security (BYOK)

- **Encryption**: AES-256-GCM
- **Rotation**: 90-day automatic
- **Scoping**: Per-agent, per-tool, per-user
- **Audit**: Complete logging
- **Expiration**: Configurable

```python
from ottoman_agent_pipeline.byok import get_keyvault

vault = get_keyvault()
key_id = await vault.create_key(
    service="deepseek",
    api_key="sk-xxx",
    scope=KeyScope.AGENT
)
```

## Workflow

```python
from ottoman_agent_pipeline.workflow import get_workflow_registry

registry = get_workflow_registry()

# Create from template
workflow_id = await registry.create_workflow(
    name="My Pipeline",
    template_id="transliteration_pipeline"
)

# Execute
result = await registry.execute_workflow(
    workflow_id=workflow_id,
    input_data={"text": "عثmanli توركجهسى"}
)
```

## API Endpoints

### Transliteration
```
POST /api/v1/transliterate
POST /api/v1/transliterate/batch
```

### Chat
```
POST /api/v1/chat
```

### BYOK
```
POST   /api/v1/byok/keys
GET    /api/v1/byok/keys
POST   /api/v1/byok/keys/{id}/rotate
POST   /api/v1/byok/keys/{id}/revoke
GET    /api/v1/byok/keys/{id}/audit
```

### MCP Tools
```
GET    /api/v1/mcp/tools
POST   /api/v1/mcp/tools/{id}/execute
```

### Workflow
```
GET    /api/v1/workflows/
POST   /api/v1/workflows/
POST   /api/v1/workflows/{id}/execute
```

## References

- [GitHub](https://github.com/bilirkesi/ottoman-agent-pipeline)
- [PyPI](https://pypi.org/project/ottoman-agent-pipeline/)
- [HuggingFace](https://huggingface.co/bilirkesi/osmanlica-v1)
- [Zenodo](https://doi.org/10.5281/zenodo.21781872)
- [Reasonix](https://github.com/esengine/DeepSeek-Reasonix)
- [TurkicNLP](https://github.com/turkic-nlp/turkicnlp)
