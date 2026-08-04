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
---

# Ottoman Agent Pipeline

Production-grade Ottoman Turkish transliteration agent pipeline with Desktop and Mobile support.

## 🚀 Quick Start

```bash
# Install
pip install -e .

# Initialize config
ottoman-agent init

# Run agent
ottoman-agent chat "عثمانلي توركجهسى"

# Or use API
ottoman-agent serve --port 8000
```

## 🏗️ Architecture

```
┌──────────────┐     ┌──────────────┐     ┌──────────────┐
│  Desktop App │────▶│  Agent Core  │────▶│  Gateway     │
│  (Electron)  │     │  (Python)    │     │  (DB-Mentat) │
└──────────────┘     └──────────────┘     └──────────────┘
                           │
                           ▼
┌─────────────────────────────────────────────────────────────┐
│                   AGENT CORE                                │
│                                                             │
│  • Input Parser → Orchestrator → Output Formatter          │
│  • Tools (MCP): File System, Web Search, Translation, NER  │
│  • Models: DeepSeek V4 Flash, Reasonix, DB-Mentat Gateway  │
└─────────────────────────────────────────────────────────────┘
```

## 📦 Features

- **Multi-platform**: Desktop (Electron) + Mobile (React Native)
- **Multi-model**: DeepSeek V4 Flash, DeepSeek V4 Pro, Reasonix
- **MCP Tools**: File system, web search, translation, NER, database
- **Session Management**: Persistent conversations with history
- **Pipeline Orchestration**: Configurable multi-stage processing
- **Error Handling**: Automatic fallback and retry logic
- **Logging**: Structured logging with Loguru
- **API**: REST API with FastAPI

## 🔧 Configuration

Create `~/.ottoman-agent/config.yaml`:

```yaml
agent:
  name: "osmanlica-agent"
  version: "0.1.0"
  
models:
  default: "deepseek-v4-flash"
  providers:
    deepseek:
      api_key: "${DEEPSEEK_API_KEY}"
      base_url: "https://api.deepseek.com/v1"
      models:
        - name: "deepseek-v4-flash"
          context: 1000000
          max_output: 384000
        - name: "deepseek-v4-pro"
          context: 128000
          max_output: 8000
    
    gateway:
      url: "${GATEWAY_URL:http://localhost:3002}"
      api_key: "${GATEWAY_API_KEY}"

tools:
  filesystem:
    enabled: true
    root_dir: "${OTTOMAN_AGENT_ROOT:./data}"
  
  web_search:
    enabled: true
    max_results: 10
  
  translation:
    enabled: true
    pipeline: "hybrid"
  
  ner:
    enabled: true
    model: "bert-base-turkish"

sessions:
  max_history: 50
  auto_save: true
  save_dir: "./data/sessions"
```

## 📱 Desktop App

Coming soon...

```bash
cd desktop
npm install
npm start
```

## 📱 Mobile App

Coming soon...

```bash
cd mobile
npm install
npm start
```

## 🧪 Testing

```bash
pytest tests/ -v --cov=ottoman_agent_pipeline
```

## 📄 License

MIT License - See LICENSE for details.

## 🙏 Acknowledgments

- [DeepSeek](https://www.deepseek.com) for V4 Flash
- [TurkicNLP](https://github.com/turkic-nlp/turkicnlp) for toolkit
- [DB-Mentat Gateway](https://github.com/bilirkesi/ai-dev-team) for integration
- [Osmanlica](https://github.com/bilirkesi/turkish-nlp) for transliteration pipeline
