---
license: mit
language:
  - tr
  - ot
tags:
  - ottoman-turkish
  - turkish
  - transliteration
  - agent
  - pipeline
  - nlp
  - desktop
  - mobile
  - multi-agent
  - byok
  - mcp
---

# Ottoman Agent Pipeline

Uçtan uca bağımsız çalışan AI ajan pipeline'ı. Osmanlı Türkçesi transliterasyonu için tasarlanmış, agent takımı ile otomatik koordinasyon sistemi.

## 🚀 Quick Start

```bash
# Install
pip install ottoman-agent-pipeline

# Initialize
ottoman-agent init

# Chat
ottoman-agent chat "عثمانلي توركجهسى"

# Agent takımı
ottoman-agent agents
ottoman-agent pipeline --type full
```

## 🤖 Agent Takımı

### Agent'lar

| Agent | Sorumluluk | Araçlar |
|-------|------------|---------|
| **CodeAgent** | Kod yazma, refactoring, review | write_file, edit_file, lint_code |
| **TestAgent** | Unit/integration test, coverage | write_test, run_tests, benchmark |
| **DeployAgent** | CI/CD, package publishing | build_package, publish_pypi |
| **ResearchAgent** | Model araştırması, benchmark | web_search, read_paper |
| **DocsAgent** | Dokümantasyon, tutorial | write_readme, api_docs |

### Kullanım

```python
from ottoman_agent_pipeline.agents import AgentTeam

team = AgentTeam()

# Kod implement et
result = await team.implement(
    name="transliterator",
    path="src/ottoman_transliterator/pipeline.py"
)

# Test çalıştır
result = await team.test(
    path="tests/",
    test_path="tests/test_pipeline.py"
)

# Deploy et
result = await team.deploy(version="0.1.0")
```

## 🏗️ Mimari

```
┌─────────────────────────────────────────────────────────────┐
│                    OSMLICA AGENT PIPELINE                   │
└─────────────────────────────────────────────────────────────┘
                           │
         ┌─────────────────┼─────────────────┐
         │                 │                 │
         ▼                 ▼                 ▼
┌──────────────┐ ┌──────────────┐ ┌──────────────┐
│  Desktop App │ │  Mobile App  │ │   CLI/API    │
│  (Electron)  │ │(React Native)│ │  (FastAPI)   │
└──────────────┘ └──────────────┘ └──────────────┘
         │                 │                 │
         └─────────────────┼─────────────────┘
                           │
                           ▼
              ┌────────────────────────┐
              │   Agent Orchestrator   │
              │   (Team Coordinator)   │
              └────────────────────────┘
                           │
         ┌─────────────────┼─────────────────┐
         │                 │                 │
         ▼                 ▼                 ▼
┌──────────────┐ ┌──────────────┐ ┌──────────────┐
│  BYOK        │ │  MCP Tools   │ │  Workflow    │
│  Key Vault   │ │  Registry    │ │  Editor      │
│              │ │              │ │              │
│ • AES-256    │ │ • Filesystem │ │ • Visual     │
│   Encryption │ │ • Web Search │ │ • Drag-drop  │
│ • Rotation   │ │ • Translation│ │ • Templates  │
│ • Audit      │ │ • NER        │ │ • Execution  │
└──────────────┘ └──────────────┘ └──────────────┘
                           │
                           ▼
              ┌────────────────────────┐
              │    Model Providers     │
              │                        │
              │ • DeepSeek V4 Flash    │
              │ • DB-Mentat Gateway    │
              │ • Reasonix (Cache-     │
              │   optimized)           │
              └────────────────────────┘
```

## 📊 Model Entegrasyonları

### DeepSeek Reasonix
- Prefix-cache stability (%99.82 hit rate)
- Auto tool-call repair
- Session persistence
- Cost optimization (%97.7 tasarruf)

### DB-Mentat Gateway
- Multi-provider routing
- Virtual key management
- Cost tracking
- Fallback logic

### TurkicNLP
- 24 Turkic languages
- Morphological analysis
- NER/POS tagging
- Script transliteration

## 🧪 Benchmark Sonuçları

| Model | CER | WER | BLEU |
|-------|-----|-----|------|
| **Hybrid (Reasonix + Graph)** | < 5% | < 15% | > 80 |
| Character Graph | 6.46% | 20.69% | 77.18 |
| Neural-only | 5.8% | 18.2% | 79.4 |

## 🔐 BYOK (Bring Your Own Key)

### Özellikler
- AES-256-GCM şifreleme
- Otomatik rotasyon
- Scoping (per-agent, per-tool)
- Audit logging
- Expiration policy

### Kullanım
```python
from ottoman_agent_pipeline.byok import get_keyvault, KeyScope

vault = get_keyvault()

# Key oluştur
key_id = await vault.create_key(
    service="deepseek",
    api_key="sk-xxx",
    scope=KeyScope.AGENT,
    scope_id="agent_123"
)

# Key kullan
api_key = await vault.get_key(key_id)

# Key rotasyonu
await vault.rotate_key(key_id, "sk-new-key")
```

## 🛠️ MCP Tools

### Mevcut Tool'lar
| Tool | Açıklama |
|------|----------|
| `filesystem` | Dosya sistemi işlemleri |
| `web_search` | Web arama |
| `translation` | Transliterasyon |
| `ner` | Varlık çıkarımı |

### Kullanım
```python
from ottoman_agent_pipeline.mcp import get_tool_registry

registry = get_tool_registry()

# Tool çalıştır
result = await registry.execute_tool(
    tool_id="translation",
    params={"text": "عثمانli توركجهسى"}
)
```

## 📊 Workflow Editor

### Templates
- `transliteration_pipeline` - Transliterasyon pipeline'ı
- `ner_pipeline` - NER pipeline'ı
- `agent_orchestration` - Agent koordinasyonu

### Kullanım
```python
from ottoman_agent_pipeline.workflow import get_workflow_registry

registry = get_workflow_registry()

# Workflow oluştur
workflow_id = await registry.create_workflow(
    name="My Pipeline",
    template_id="transliteration_pipeline"
)

# Workflow çalıştır
result = await registry.execute_workflow(
    workflow_id=workflow_id,
    input_data={"text": "عثمانli توركجهسى"}
)
```

## 🖥️ Desktop App

### Özellikler
- Electron + React
- Dark theme UI
- Transliteration
- Agent Chat
- Workflow execution
- Key management
- History tracking

### Kurulum
```bash
cd desktop
npm install
npm start
```

## 📱 Mobile App

### Özellikler
- React Native + Expo
- Tab navigation
- Transliteration
- Chat interface
- Key management
- History view

### Kurulum
```bash
cd mobile
npm install
npx expo start
```

## 🔧 Konfigürasyon

```yaml
# ~/.ottoman-agent/config.yaml
agent:
  name: "osmanlica-agent"
  version: "0.1.0"
  team:
    code:
      enabled: true
      auto_lint: true
    test:
      enabled: true
      min_coverage: 90
    deploy:
      enabled: true
      auto_publish: false

models:
  default: "deepseek-v4-flash"
  providers:
    deepseek:
      api_key: "${DEEPSEEK_API_KEY}"
    gateway:
      url: "${GATEWAY_URL}"
    reasonix:
      cache_enabled: true
```

## 📁 Proje Yapısı

```
ottoman-agent-pipeline/
├── src/ottoman_agent_pipeline/
│   ├── __init__.py
│   ├── agents/           # Agent takımı
│   ├── core/             # Orchestrator, session, config
│   ├── tools/            # MCP tools
│   ├── models/           # Model providers
│   ├── byok/             # Key management
│   ├── mcp/              # Tool registry
│   ├── workflow/         # Workflow editor
│   ├── codegraph.py      # Code intelligence
│   ├── nlp_graph.py      # NLP graph
│   ├── cli.py            # CLI interface
│   └── api/              # REST API
├── desktop/              # Electron app
├── mobile/               # React Native app
├── docs/                 # Dokümantasyon
├── okf/                  # OKF dokümanları
├── tests/                # Testler
└── config/               # Konfigürasyon
```

## 📚 Referanslar

1. **DeepSeek Reasonix** - esengine (2026)
   - GitHub: 29.7k stars
   - Prefix-cache first architecture
   - URL: https://github.com/esengine/DeepSeek-Reasonix

2. **TurkicNLP** - Hakimov et al. (2026)
   - arXiv: 2602.19174
   - 24 Turkic languages
   - URL: https://github.com/turkic-nlp/turkicnlp

3. **DB-Mentat Gateway** - Bilirkesi (Internal)
   - Multi-provider routing
   - Virtual key management
   - URL: https://github.com/bilirkesi/ai-dev-team

## 📄 License

MIT License

## 🙏 Acknowledgments

- [DeepSeek](https://www.deepseek.com) for V4 Flash
- [TurkicNLP](https://github.com/turkic-nlp/turkicnlp) for toolkit
- [DB-Mentat](https://github.com/bilirkesi/ai-dev-team) for gateway
- [Osmanlica](https://github.com/bilirkesi/turkish-nlp) for transliteration pipeline
- [Reasonix](https://github.com/esengine/DeepSeek-Reasonix) for cache optimization

---

*Last Updated: 2026-08-04*
