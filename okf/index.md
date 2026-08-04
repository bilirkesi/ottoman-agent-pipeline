# Open Knowledge Format (OKF) - Osmanlica Agent Pipeline

> **Open Knowledge Format** - Proje bilgi ve dokümantasyon standardı

## 📚 Index

### Servisler
- [Osmanlica Transliterator](./services/osmanlica-transliterator.md)
- [Agent Pipeline](./services/agent-pipeline.md)
- [API Server](./services/api-server.md)

### Agent'lar
- [Osmanlica Agent](./agents/osmanlica-agent.md)
- [Code Agent](./agents/code-agent.md)
- [Test Agent](./agents/test-agent.md)
- [Deploy Agent](./agents/deploy-agent.md)
- [Research Agent](./agents/research-agent.md)
- [Docs Agent](./agents/docs-agent.md)

### Dokümanlar
- [Architecture](./docs/architecture.md)
- [API Reference](./docs/api-reference.md)
- [Deployment](./docs/deployment.md)
- [Benchmark Report](./docs/benchmark-report.md)
- [CodeGraph](./docs/codegraph.md)
- [NLP Graph](./docs/nlp-graph.md)
- [BYOK](./docs/byok.md)

### Veri
- [Osmanlica-Bench Dataset](./datasets/osmanlica-bench-v1.md)

---

## 🏗️ Servisler

### Osmanlica Transliterator
Ottoman Turkish → Modern Turkish transliteration pipeline.

**Özellikler:**
- Hybrid neural + rule-based approach
- 6.46% CER, 77.18 BLEU
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
| **Hybrid** | 6.46% | 20.69% | 77.18 |
| Neural-only | 5.8% | 18.2% | 79.4 |
| NLP-only | 6.46% | 20.69% | 77.18 |

---

## 🔗 İlişkili Kaynaklar

- [GitHub Repository](https://github.com/bilirkesi/ottoman-agent-pipeline)
- [PyPI Package](https://pypi.org/project/ottoman-agent-pipeline/)
- [HuggingFace Model](https://huggingface.co/bilirkesi/osmanlica-v1)
- [HuggingFace Dataset](https://huggingface.co/datasets/bilirkesi/osmanlica-bench-v1)
- [Zenodo Dataset](https://doi.org/10.5281/zenodo.21781872)

---

*Son güncelleme: 2026-08-04*
