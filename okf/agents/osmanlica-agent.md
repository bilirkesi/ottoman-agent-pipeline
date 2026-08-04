---
name: osmanlica-agent
version: 0.1.0
family: nlp
type: transliteration
status: production
---

# Osmanlica Agent

Ottoman Turkish to Modern Turkish transliteration agent.

## Overview

Osmanlica Agent, Osmanlı Türkçesi metinleri Modern Türkçeye transliterate eden bir AI ajanıdır. DeepSeek V4 Flash, DB-Mentat Gateway ve TurkicNLP entegrasyonları ile çalışır.

## Capabilities

- **Transliteration**: Arap harfli Osmanlı Türkçesi → Latin Türkçe
- **Reverse Transliteration**: Latin Türkçe → Arap harfli Osmanlı
- **NER**: Named Entity Recognition (kişi, yer, kuruluş)
- **Analysis**: Metin analizi, confidence scoring
- **Batch Processing**: Toplu işleme desteği

## Tools

| Tool | Açıklama | Kullanım |
|------|----------|----------|
| `filesystem` | Dosya okuma/yazma | `read_file`, `write_file` |
| `web_search` | Web arama | `search`, `fetch` |
| `translation` | Transliterasyon | `transliterate`, `batch` |
| `ner` | Varlık çıkarımı | `extract`, `annotate` |

## Models

| Model | Sağlayıcı | Özellikler |
|-------|-----------|------------|
| `deepseek-v4-flash` | DeepSeek API | 1M context, $0.14/1M |
| `deepseek-v4-pro` | DeepSeek API | 128K context, powerful |
| `gateway` | DB-Mentat | Multi-provider routing |
| `reasonix` | DeepSeek | Prefix-cache optimized |

## Configuration

```yaml
agent:
  name: "osmanlica-agent"
  version: "0.1.0"
  
models:
  default: "deepseek-v4-flash"
  providers:
    deepseek:
      api_key: "${DEEPSEEK_API_KEY}"
    gateway:
      url: "${GATEWAY_URL}"

tools:
  translation:
    pipeline: "hybrid"
    confidence_threshold: 0.7
```

## Usage

### CLI
```bash
# Chat
ottoman-agent chat "عثمانلي توركجهسى"

# Transliterate
ottoman-agent translate "بسم الله"

# Analyze
ottoman-agent analyze "عثمانlı توركجهسى"

# Serve API
ottoman-agent serve --port 8000
```

### Python
```python
from ottoman_agent_pipeline import AgentOrchestrator

orch = AgentOrchestrator()
await orch.initialize()

result = await orch.chat("عثمانli توركجهسى")
print(result.output)
```

## Performance

| Metric | Value |
|--------|-------|
| CER | 6.46% |
| WER | 20.69% |
| BLEU | 77.18 |
| F1-NER | 83.8% |

## References

- [GitHub](https://github.com/bilirkesi/ottoman-agent-pipeline)
- [PyPI](https://pypi.org/project/ottoman-agent-pipeline/)
- [HuggingFace](https://huggingface.co/bilirkesi/osmanlica-v1)
- [Zenodo](https://doi.org/10.5281/zenodo.21781872)
