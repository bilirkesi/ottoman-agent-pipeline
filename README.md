# Ottoman Agent Pipeline

**Ottoman Agent Pipeline** - Uçtan uca bağımsız çalışan AI ajan pipeline'ı.

## 🚀 Quick Start

```bash
# Install
pip install -e .

# Initialize
ottoman-agent init

# Chat
ottoman-agent chat "عثمانلي توركجهسى"

# Translate
ottoman-agent translate "بسم الله"

# Serve API
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
    gateway:
      url: "${GATEWAY_URL:http://localhost:3002}"
      api_key: "${GATEWAY_API_KEY}"

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

MIT License

## 🔗 Related

- **Main Repo:** https://github.com/bilirkesi/turkish-nlp
- **Transliteration Package:** https://pypi.org/project/ottoman-transliterator/
- **HuggingFace:** https://huggingface.co/bilirkesi
