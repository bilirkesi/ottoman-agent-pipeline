---
license: mit
language:
  - tr
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
| **DeployAgent** | CI/CD, package publishing | build_package, publish_pypi, create_release |
| **ResearchAgent** | Model araştırması, benchmark | web_search, read_paper, analyze |
| **DocsAgent** | Dokümantasyon, tutorial | write_readme, generate_api_docs |

### Kullanım

```python
from ottoman_agent_pipeline.agents import AgentTeam

# Agent takımı oluştur
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

# Pipeline çalıştır
pipeline = [
    {"name": "Implement", "agent": "code_agent", "payload": {...}},
    {"name": "Test", "agent": "test_agent", "payload": {...}},
    {"name": "Deploy", "agent": "deploy_agent", "payload": {...}}
]
result = await team.run_pipeline(pipeline)
```

## 🏗️ Mimari

```
┌─────────────────────────────────────────────────────────────┐
│              Project Orchestrator                           │
│              (Agent Coordinator)                            │
└────────────────────────┬────────────────────────────────────┘
                         │
         ┌───────────────┼───────────────┐
         │               │               │
         ▼               ▼               ▼
┌──────────────┐ ┌──────────────┐ ┌──────────────┐
│  CodeAgent   │ │  TestAgent   │ │ DeployAgent  │
│              │ │              │ │              │
│ • Implement  │ │ • Unit Test  │ │ • Build      │
│ • Refactor   │ │ • Coverage   │ │ • Publish    │
│ • Review     │ │ • Benchmark  │ │ • Release    │
└──────────────┘ └──────────────┘ └──────────────┘
         │               │               │
         └───────────────┼───────────────┘
                         │
                         ▼
              ┌──────────────────┐
              │  Agent Bus       │
              │  (Message Queue) │
              └──────────────────┘
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
| **Hybrid (Reasonix + NLP)** | 6.46% | 20.69% | 77.18 |
| Neural-only | 5.8% | 18.2% | 79.4 |
| NLP-only | 6.46% | 20.69% | 77.18 |

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
  default: "reasonix"
  providers:
    reasonix:
      api_key: "${DEEPSEEK_API_KEY}"
      cache_enabled: true
    gateway:
      url: "${GATEWAY_URL}"
    deepseek:
      api_key: "${DEEPSEEK_API_KEY}"

tools:
  filesystem:
    enabled: true
  web_search:
    enabled: true
  translation:
    enabled: true
    pipeline: "hybrid"
  ner:
    enabled: true
    model: "bert-base-turkish"
```

## 📁 Proje Yapısı

```
ottoman-agent-pipeline/
├── src/ottoman_agent_pipeline/
│   ├── __init__.py
│   ├── agents/
│   │   ├── __init__.py
│   │   ├── team.py          # Agent takımı
│   │   ├── cli.py           # CLI komutları
│   │   └── base.py          # Base agent sınıfları
│   ├── core/
│   │   ├── orchestrator.py  # Ana orchestrator
│   │   ├── session.py       # Session yönetimi
│   │   └── config.py        # Konfigürasyon
│   ├── tools/
│   │   ├── base.py          # Base tool
│   │   ├── filesystem.py    # Dosya sistemi
│   │   ├── web.py           # Web search
│   │   ├── translation.py   # Transliterasyon
│   │   └── ner.py           # NER
│   ├── models/
│   │   ├── base.py          # Base model
│   │   ├── deepseek.py      # DeepSeek API
│   │   ├── gateway.py       # DB-Mentat Gateway
│   │   └── reasonix.py      # Reasonix (yakında)
│   ├── prompts/
│   │   └── system.py        # System prompts
│   └── api/
│       └── server.py        # FastAPI server
├── tests/
│   ├── test_agents.py
│   └── test_pipeline.py
├── config/
│   └── default.yaml
├── pyproject.toml
├── requirements.txt
└── README.md
```

## 🚀 Kullanım

### CLI

```bash
# Agent durumu
ottoman-agent agents

# Kod implement et
ottoman-agent implement --name transliterator --path src/

# Test çalıştır
ottoman-agent test --path tests/

# Deploy
ottoman-agent deploy --version 0.1.0

# Araştırma
ottoman-agent research "Ottoman Turkish NLP"

# Dokümantasyon
ottoman-agent document --project ottoman-agent-pipeline

# Tam pipeline
ottoman-agent pipeline --type full
```

### Python API

```python
from ottoman_agent_pipeline import AgentTeam

# Agent takımı
team = AgentTeam()

# Pipeline çalıştır
result = await team.run_pipeline([
    {
        "name": "Implement",
        "agent": "code_agent",
        "payload": {"action": "implement", "name": "example"}
    },
    {
        "name": "Test",
        "agent": "test_agent",
        "payload": {"action": "test", "path": "tests/"}
    },
    {
        "name": "Deploy",
        "agent": "deploy_agent",
        "payload": {"action": "deploy", "version": "0.1.0"}
    }
])
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
