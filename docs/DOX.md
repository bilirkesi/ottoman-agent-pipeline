# DOX - Osmanlica Agent Pipeline

> **Document eXchange** - Proje dokümantasyon ve koordinasyon sistemi

## 📚 Dokümanlar

### Proje Dokümantasyonu
| Doküman | Açıklama | Konum |
|---------|----------|-------|
| README.md | Proje tanıtımı ve kullanım | root |
| CONTRIBUTING.md | Katılım rehberi | root |
| LICENSE.md | MIT Lisans | root |
| BENCHMARK_REPORT_v1.md | Performans benchmark'ları | docs/ |
| PROJECT_PLAN.md | 12 aylık proje planı | docs/ |
| USE_CASES.md | Kullanım senaryoları | docs/ |

### Teknik Dokümantasyon
| Doküman | Açıklama | Konum |
|---------|----------|-------|
| API_REFERENCE.md | REST API referansı | docs/ |
| ARCHITECTURE.md | Mimari dokümantasyon | docs/ |
| DEPLOYMENT.md | Deployment rehberi | docs/ |
| AGENTS.md | Agent takımı dokümantasyonu | docs/ |

### OKF (Open Knowledge Format)
| Doküman | Açıklama | Konum |
|---------|----------|-------|
| okf/index.md | OKF index | okf/ |
| okf/services/index.md | Servis dizini | okf/services/ |
| okf/agents/osmanlica-agent.md | Agent tanımı | okf/agents/ |

---

## 🏗️ DOX Yapısı

```
ottoman-agent-pipeline/
├── docs/
│   ├── README.md
│   ├── CONTRIBUTING.md
│   ├── LICENSE.md
│   ├── BENCHMARK_REPORT_v1.md
│   ├── PROJECT_PLAN.md
│   ├── USE_CASES.md
│   ├── API_REFERENCE.md
│   ├── ARCHITECTURE.md
│   └── AGENTS.md
├── okf/
│   ├── index.md
│   ├── services/
│   │   ├── index.md
│   │   └── osmanlica-transliterator.md
│   └── agents/
│       └── osmanlica-agent.md
├── src/
│   └── ottoman_agent_pipeline/
│       ├── __init__.py
│       ├── core/
│       ├── tools/
│       ├── models/
│       └── agents/
└── tests/
```

---

## 📖 Agent Dokümantasyonu

### Osmanlica Agent
- **Ad:** osmanlica-agent
- **Versiyon:** 0.1.0
- **Aile:** NLP, Translation
- **Sorumluluk:** Ottoman Turkish transliteration
- **Araçlar:** filesystem, web_search, translation, ner
- **Modeller:** DeepSeek V4 Flash, DB-Mentat Gateway

### Agent Takımı
| Agent | Sorumluluk | Araçlar |
|-------|------------|---------|
| CodeAgent | Kod yazma, refactoring | write_file, edit_file, lint_code |
| TestAgent | Test yazma, çalıştırma | write_test, run_tests, coverage |
| DeployAgent | CI/CD, publishing | build_package, publish_pypi |
| ResearchAgent | Araştırma, benchmark | web_search, read_paper |
| DocsAgent | Dokümantasyon | write_readme, api_docs |

---

## 🔗 İlişkili Dokümanlar

- [OKF Index](./okf/index.md)
- [Agent Tanımı](./okf/agents/osmanlica-agent.md)
- [Benchmark Report](./docs/BENCHMARK_REPORT_v1.md)
- [Proje Planı](./docs/PROJECT_PLAN.md)

---

*Son güncelleme: 2026-08-04*
