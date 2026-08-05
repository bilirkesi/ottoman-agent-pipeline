# Ottoman Agent Pipeline - README

> Uçtan uca Osmanlı Türkçesi transliterasyon ajan pipeline'ı

## 🚀 Quick Start

```bash
# Kurulum (paket henüz PyPI'da yayınlanmadı — kaynaktan kurun)
git clone https://github.com/bilirkesi/ottoman-agent-pipeline.git
cd ottoman-agent-pipeline
python -m venv .venv && .venv/bin/activate   # Windows: .venv\Scripts\activate
pip install -e ".[dev]"

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

## 🤖 Agent Team

### Agents
| Agent | Sorumluluk | Araçlar |
|-------|------------|---------|
| **CodeAgent** | Kod yazma, refactoring, linting | write_file, edit_file, lint_code |
| **TestAgent** | Test yazma, coverage, benchmark | write_test, run_tests, benchmark |
| **DeployAgent** | CI/CD, package publishing | build_package, publish_pypi |
| **ResearchAgent** | Model araştırması, literature | web_search, read_paper |
| **DocsAgent** | Dokümantasyon, API docs | write_readme, api_docs |

### Usage
```python
from ottoman_agent_pipeline.agents import AgentTeam

team = AgentTeam()

# Implement code
result = await team.implement(
    name="transliterator",
    path="src/ottoman_transliterator/pipeline.py"
)

# Run tests
result = await team.test(
    path="tests/",
    test_path="tests/test_pipeline.py"
)

# Deploy
result = await team.deploy(version="0.1.0")
```

## 📊 Benchmarks

| Model | CER | WER | BLEU |
|-------|-----|-----|------|
| **Hybrid (Reasonix + Graph)** | < 5% | < 15% | > 80 |
| Character Graph | 6.46% | 20.69% | 77.18 |
| Neural-only | 5.8% | 18.2% | 79.4 |

## 🔐 BYOK (Bring Your Own Key)

### Features
- AES-256-GCM encryption
- Automatic rotation
- Scoping (per-agent, per-tool, per-user)
- Complete audit logging
- Expiration policy

### Usage
```python
from ottoman_agent_pipeline.byok import get_keyvault, KeyScope

vault = get_keyvault()

# Create key
key_id = await vault.create_key(
    service="deepseek",
    api_key="sk-xxx",
    scope=KeyScope.AGENT,
    scope_id="agent_123"
)

# Get key
api_key = await vault.get_key(key_id)

# Rotate key
await vault.rotate_key(key_id, "sk-new-key")

# Revoke key
await vault.revoke_key(key_id)
```

### API
```bash
# Create key
curl -X POST http://localhost:8000/api/v1/byok/keys \
  -H "Content-Type: application/json" \
  -d '{"service":"deepseek","api_key":"sk-xxx","scope":"global"}'

# List keys
curl http://localhost:8000/api/v1/byok/keys

# Rotate key
curl -X POST http://localhost:8000/api/v1/byok/keys/{id}/rotate \
  -d '{"new_api_key":"sk-new"}'
```

## 🛠️ MCP Tools

### Available Tools
| Tool | Description |
|------|-------------|
| `filesystem` | File operations (read, write, list) |
| `web_search` | Web search and content extraction |
| `translation` | Ottoman Turkish transliteration |
| `ner` | Named entity recognition |

### Usage
```python
from ottoman_agent_pipeline.mcp import get_tool_registry

registry = get_tool_registry()

# List tools
tools = await registry.list_tools()

# Execute tool
result = await registry.execute_tool(
    tool_id="translation",
    params={"text": "عثمانli توركجهسى"}
)
```

### API
```bash
# List tools
curl http://localhost:8000/api/v1/mcp/tools

# Execute tool
curl -X POST http://localhost:8000/api/v1/mcp/tools/translation/execute \
  -d '{"text":"عثمانلي توركجهسى"}'
```

## 📊 Workflow Editor

### Features
- Visual drag-drop interface
- Template library
- Execution tracking
- Version control

### Templates
- `transliteration_pipeline` - Ottoman Turkish transliteration
- `ner_pipeline` - Named entity recognition
- `agent_orchestration` - Multi-agent coordination

### Usage
```python
from ottoman_agent_pipeline.workflow import get_workflow_registry

registry = get_workflow_registry()

# Create workflow
workflow_id = await registry.create_workflow(
    name="My Pipeline",
    template_id="transliteration_pipeline"
)

# Execute workflow
result = await registry.execute_workflow(
    workflow_id=workflow_id,
    input_data={"text": "عثمانli توركجهسى"}
)
```

## 🖥️ Desktop App

### Features
- Electron + React
- Dark theme UI
- Transliteration
- Agent Chat
- Workflow execution
- Key management
- History tracking

### Installation
```bash
cd desktop
npm install
npm start
```

## 📱 Mobile App

### Features
- React Native + Expo
- Tab navigation
- Transliteration
- Chat interface
- Key management
- History view

### Installation
```bash
cd mobile
npm install
npx expo start
```

## 🔧 Configuration

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

## 📁 Project Structure

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
│   ├── workflow/         # Workflow engine
│   ├── codegraph.py      # Code intelligence
│   ├── nlp_graph.py      # NLP graph
│   ├── cli.py            # CLI interface
│   └── api/              # REST API
├── desktop/              # Electron app
├── mobile/               # React Native app
├── docs/                 # Documentation
├── okf/                  # OKF documentation
├── tests/                # Tests
└── config/               # Configuration
```

## 📚 References

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

4. **Osmanlica Transliterator** - Bilirkesi (2026)
   - Hybrid neural + rule-based
   - 5% CER, 80+ BLEU
   - URL: https://github.com/bilirkesi/turkish-nlp

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
*Version: 0.1.0*
