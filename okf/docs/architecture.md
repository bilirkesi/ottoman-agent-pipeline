# Architecture - Osmanlica Agent Pipeline

## 🏗️ System Architecture

```
┌─────────────────────────────────────────────────────────────────────────┐
│                    OSMANLICA AGENT PIPELINE                               │
└─────────────────────────────────────────────────────────────────────────┘
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
              │   (ProjectCoordinator) │
              └────────────────────────┘
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
              │ • DeepSeek V4 Pro      │
              │ • DB-Mentat Gateway    │
              │ • Reasonix (Optional)  │
              └────────────────────────┘
```

## 🔄 Data Flow

### 1. Input
```
User Input
    │
    ▼
┌─────────────┐
│  Input Parser│
│  (Script Detection)│
└─────────────┘
    │
    ▼
┌─────────────┐
│  Chunking   │
│  (4000 chars)│
└─────────────┘
```

### 2. Processing
```
┌─────────────┐
│  Orchestrator│
│  (Route to Agent)│
└─────────────┘
    │
    ▼
┌─────────────┐     ┌─────────────┐
│  Code Agent │────▶│  Test Agent │
│  (Implement)│     │  (Validate) │
└─────────────┘     └─────────────┘
    │                   │
    └───────────────────┘
            │
            ▼
┌─────────────┐
│  Deploy Agent│
│  (Release)  │
└─────────────┘
```

### 3. Output
```
┌─────────────┐
│  Formatter  │
│  (JSON/Text)│
└─────────────┘
    │
    ▼
┌─────────────┐
│  Output     │
│  (Result)   │
└─────────────┘
```

## 🧬 Component Details

### Agent Orchestrator
- **Responsibility:** Coordinate agent tasks
- **Features:**
  - Task scheduling
  - Error handling
  - Session management
  - Logging

### Agent Bus
- **Responsibility:** Message routing
- **Features:**
  - Async queue
  - Message validation
  - Retry logic
  - Dead letter queue

### Model Providers
- **DeepSeek V4 Flash:** Primary model (cost-effective)
- **DeepSeek V4 Pro:** Fallback (higher quality)
- **DB-Mentat Gateway:** Multi-provider routing
- **Reasonix:** Cache-optimized (99.82% hit rate)

## 🔒 Security

### Authentication
- API Key based
- Virtual key management (DB-Mentat)
- Rate limiting per key

### Data Protection
- PII detection (llm-pii-detector)
- Prompt injection guard
- Content filtering

### Compliance
- GDPR ready
- Data encryption at rest
- Audit logging

## 📊 Performance

| Component | Latency | Throughput |
|-----------|---------|------------|
| **Transliterator** | ~1.2s/500chars | 100 req/s |
| **Agent Orchestrator** | ~50ms | 1000 req/s |
| **Model API** | ~800ms | Variable |
| **Total Pipeline** | ~2s | 50 req/s |

## 🚀 Scaling

### Horizontal Scaling
- Stateless agents
- Load balanced API
- Distributed task queue

### Vertical Scaling
- GPU acceleration (optional)
- Cache optimization
- Connection pooling

## 📈 Monitoring

### Metrics
- Token usage
- Latency
- Error rate
- Cost tracking

### Logging
- Structured logging (Loguru)
- Request tracing
- Audit logs

### Alerts
- Error rate > 5%
- Latency > 5s
- Cost threshold breach

## 🔗 Integration Points

### External APIs
- DeepSeek API
- DB-Mentat Gateway
- TurkicNLP
- HuggingFace Hub
- Zenodo API

### Internal Services
- CodeGraph (optional)
- NotebookLM (optional)
- VFS (optional)

## 📝 Versioning

### Semantic Versioning
- Major: Breaking changes
- Minor: New features
- Patch: Bug fixes

### API Versioning
- `/api/v1/*`
- Backward compatible
- Deprecation policy

---

*Last Updated: 2026-08-04*
