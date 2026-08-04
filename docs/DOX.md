# DOX - Ottoman Agent Pipeline

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
| API_REFERENCE.md | REST API referansı | okf/docs/ |
| ARCHITECTURE.md | Mimari dokümantasyon | okf/docs/ |
| DEPLOYMENT.md | Deployment rehberi | okf/docs/ |
| CODEGRAPH.md | CodeGraph sistemi | okf/docs/ |
| NLP_GRAPH.md | NLP Graph sistemi | okf/docs/ |
| BYOK.md | BYOK sistemi | okf/docs/ |
| DESKTOP_APP.md | Desktop uygulama | okf/docs/ |
| MOBILE_APP.md | Mobile uygulama | okf/docs/ |

### OKF (Open Knowledge Format)
| Doküman | Açıklama | Konum |
|---------|----------|-------|
| okf/index.md | OKF index | okf/ |
| okf/services/*.md | Servis tanımları | okf/services/ |
| okf/agents/*.md | Agent tanımları | okf/agents/ |
| okf/docs/*.md | Teknik dokümanlar | okf/docs/ |
| okf/datasets/*.md | Dataset tanımları | okf/datasets/ |

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
│   ├── DOX.md
│   └── DOX_CHAIN.md
├── okf/
│   ├── index.md
│   ├── services/
│   │   ├── index.md
│   │   ├── osmanlica-transliterator.md
│   │   ├── agent-pipeline.md
│   │   ├── api-server.md
│   │   ├── byok.md
│   │   ├── mcp-registry.md
│   │   └── workflow-engine.md
│   ├── agents/
│   │   └── osmanlica-agent.md
│   └── docs/
│       ├── README.md
│       ├── architecture.md
│       ├── api-reference.md
│       ├── deployment.md
│       ├── codegraph.md
│       ├── nlp-graph.md
│       ├── byok.md
│       ├── desktop-app.md
│       └── mobile-app.md
├── src/
│   └── ottoman_agent_pipeline/
│       ├── __init__.py
│       ├── agents/
│       ├── core/
│       ├── tools/
│       ├── models/
│       ├── byok/
│       ├── mcp/
│       ├── workflow/
│       ├── codegraph.py
│       ├── nlp_graph.py
│       ├── cli.py
│       └── api/
├── desktop/
├── mobile/
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
- **Modeller:** DeepSeek V4 Flash, DB-Mentat Gateway, Reasonix

### Agent Takımı
| Agent | Sorumluluk | Araçlar |
|-------|------------|---------|
| CodeAgent | Kod yazma, refactoring | write_file, edit_file, lint_code |
| TestAgent | Test yazma, çalıştırma | write_test, run_tests, benchmark |
| DeployAgent | CI/CD, publishing | build_package, publish_pypi |
| ResearchAgent | Araştırma, benchmark | web_search, read_paper |
| DocsAgent | Dokümantasyon | write_readme, api_docs |

---

## 🔗 İlişkili Dokümanlar

- [OKF Index](./okf/index.md)
- [Agent Tanımı](./okf/agents/osmanlica-agent.md)
- [Benchmark Report](./docs/BENCHMARK_REPORT_v1.md)
- [Proje Planı](./docs/PROJECT_PLAN.md)
- [DOX Chain](./DOX_CHAIN.md)

---

## 📝 Yönetim Kuralları

1. **Doküman Güncellemeleri**: Her kod değişikliğinde ilgili doküman güncellenmeli
2. **OKF Formatı**: Tüm sistem dokümanları OKF formatında olmalı
3. **Link Bakımı**: Broken link'ler düzenli kontrol edilmeli
4. **Version Control**: Doküman versiyonları takip edilmeli
5. **Audit Trail**: Büyük değişiklikler DOX_CHAIN.md'ye kaydedilmeli

---

*Son güncelleme: 2026-08-04*
