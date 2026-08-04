# Open Knowledge Format (OKF) - Ottoman Agent Pipeline

> **Open Knowledge Format** - Proje bilgi ve dokümantasyon standardı

## 📚 Index

### Servisler
- [Osmanlica Transliterator](./services/osmanlica-transliterator.md)
- [Agent Pipeline](./services/agent-pipeline.md)
- [API Server](./services/api-server.md)
- [BYOK Key Vault](./services/byok.md)
- [MCP Tool Registry](./services/mcp-registry.md)
- [Workflow Engine](./services/workflow-engine.md)

### Agent'lar
- [Osmanlica Agent](./agents/osmanlica-agent.md)
- [Code Agent](./agents/code-agent.md)
- [Test Agent](./agents/test-agent.md)
- [Deploy Agent](./agents/deploy-agent.md)
- [Research Agent](./agents/research-agent.md)
- [Docs Agent](./agents/docs-agent.md)

### Dokümanlar
- [README](./docs/README.md)
- [Architecture](./docs/architecture.md)
- [API Reference](./docs/api-reference.md)
- [Deployment](./docs/deployment.md)
- [CodeGraph](./docs/codegraph.md)
- [NLP Graph](./docs/nlp-graph.md)
- [BYOK](./docs/byok.md)
- [Desktop App](./docs/desktop-app.md)
- [Mobile App](./docs/mobile-app.md)

### Veri
- [Osmanlica-Bench Dataset](./datasets/osmanlica-bench-v1.md)

---

## 🏗️ Servisler

### Osmanlica Transliterator
Ottoman Turkish → Modern Turkish transliteration pipeline.

**Özellikler:**
- Hybrid neural + rule-based approach
- 5% CER, 80+ BLEU
- Confidence scoring
- Uncertainty marking

**Entegrasyonlar:**
- DeepSeek V4 Flash
- TurkicNLP
- BerTurk_Ottoman_DAPT

### Agent Pipeline
Multi-agent orchestration system.

**Agent'lar:**
- CodeAgent: Kod yazma
- TestAgent: Test çalıştırma
- DeployAgent: CI/CD
- ResearchAgent: Araştırma
- DocsAgent: Dokümantasyon

**Özellikler:**
- Message-based communication
- Task orchestration
- Error handling
- Logging

### BYOK Key Vault
Güvenli API key yönetimi.

**Özellikler:**
- AES-256-GCM encryption
- Automatic rotation
- Scoping (per-agent, per-tool)
- Complete audit logging

### MCP Tool Registry
Model Context Protocol tool management.

**Özellikler:**
- Tool registration
- Rate limiting
- Call history
- Dynamic loading

### Workflow Engine
Visual workflow editor and execution.

**Özellikler:**
- Drag-drop interface
- Template library
- Execution tracking
- Version control

---

## 🤖 Agent'lar

### Osmanlica Agent
Ana transliterasyon ajanı.

**Yetenekler:**
- Transliterasyon
- Reverse transliteration
- NER
- Metin analizi

**Araçlar:**
- filesystem
- web_search
- translation
- ner

### Code Agent
Kod yazma ve refactoring.

**Yetenekler:**
- Kod implementasyonu
- Refactoring
- Code review
- Linting

### Test Agent
Test yazma ve çalıştırma.

**Yetenekler:**
- Unit test
- Integration test
- Coverage raporlama
- Benchmark

### Deploy Agent
Deployment ve CI/CD.

**Yetenekler:**
- Package build
- PyPI publish
- GitHub release
- Docker deploy

---

## 📊 Benchmark Sonuçları

| Model | CER | WER | BLEU |
|-------|-----|-----|------|
| **Hybrid (Reasonix + Graph)** | < 5% | < 15% | > 80 |
| Character Graph | 6.46% | 20.69% | 77.18 |
| Neural-only | 5.8% | 18.2% | 79.4 |

---

## 🔗 İlişkili Kaynaklar

- [GitHub Repository](https://github.com/bilirkesi/ottoman-agent-pipeline)
- [PyPI Package](https://pypi.org/project/ottoman-agent-pipeline/)
- [HuggingFace Model](https://huggingface.co/bilirkesi/osmanlica-v1)
- [HuggingFace Dataset](https://huggingface.co/datasets/bilirkesi/osmanlica-bench-v1)
- [Zenodo Dataset](https://doi.org/10.5281/zenodo.21781872)

---

*Son güncelleme: 2026-08-04*
