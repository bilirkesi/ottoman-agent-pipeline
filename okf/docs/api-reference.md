# API Reference - Osmanlica Agent Pipeline

## Base URL
```
http://localhost:8000/api/v1
```

## Authentication
All API endpoints require authentication via Bearer token:
```http
Authorization: Bearer <your-api-key>
```

---

## Endpoints

### Health Check
```http
GET /health
```

**Response:**
```json
{
  "status": "healthy",
  "timestamp": "2026-08-04T11:00:00Z",
  "version": "0.1.0"
}
```

---

### Transliterate
Convert Ottoman Turkish text to Modern Turkish.

```http
POST /transliterate
```

**Request Body:**
```json
{
  "text": "عثمانلي توركجهسى",
  "mode": "hybrid",
  "model": "deepseek-v4-flash"
}
```

**Parameters:**
| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `text` | string | Yes | Ottoman Turkish text |
| `mode` | string | No | `hybrid`, `neural`, or `nlp` (default: `hybrid`) |
| `model` | string | No | Model name (default: `deepseek-v4-flash`) |

**Response:**
```json
{
  "ottoman": "عثمانلي توركجهسى",
  "modern_turkish": "Osmanlı Türkçesi",
  "confidence": 0.95,
  "method": "hybrid",
  "uncertain_spans": [],
  "chunks": 1
}
```

**Examples:**
```bash
curl -X POST http://localhost:8000/api/v1/transliterate \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer sk-xxx" \
  -d '{"text": "بسم الله الرحمن الرحيم"}'
```

---

### Batch Transliterate
Process multiple texts in batch.

```http
POST /transliterate/batch
```

**Request Body:**
```json
{
  "texts": ["عثمانلي", "توركجهسى"],
  "mode": "hybrid"
}
```

**Response:**
```json
{
  "results": [
    {
      "ottoman": "عثمانلي",
      "modern_turkish": "Osmanlı",
      "confidence": 0.92
    },
    {
      "ottoman": "توركجهسى",
      "modern_turkish": "Türkçesi",
      "confidence": 0.88
    }
  ],
  "total": 2
}
```

---

### Chat
Chat with the agent.

```http
POST /chat
```

**Request Body:**
```json
{
  "message": "عثمانli توركجهسى",
  "model": "deepseek-v4-flash",
  "stream": false
}
```

**Response:**
```json
{
  "success": true,
  "output": "Osmanlı Türkçesi",
  "model_used": "deepseek-v4-flash",
  "tokens_used": 45,
  "latency_ms": 1200,
  "error": null
}
```

---

### Analyze
Analyze text with NER and POS tagging.

```http
POST /analyze
```

**Request Body:**
```json
{
  "text": "عثمانلي توركجهسى",
  "entities": true,
  "pos": true
}
```

**Response:**
```json
{
  "text": "عثمانli توركجهسى",
  "entities": [
    {"text": "Osmanlı", "type": "ADJECTIVE", "start": 0, "end": 7}
  ],
  "pos_tags": [
    {"word": "Osmanlı", "pos": "ADJ"},
    {"word": "Türkçesi", "pos": "NOUN"}
  ]
}
```

---

### Session Management

#### Get Session
```http
GET /sessions/{session_id}
```

**Response:**
```json
{
  "session_id": "20260804_110000",
  "message_count": 5,
  "created_at": "2026-08-04T11:00:00Z",
  "updated_at": "2026-08-04T11:05:00Z"
}
```

#### Reset Session
```http
POST /sessions/reset
```

**Response:**
```json
{
  "status": "reset",
  "session_id": "20260804_110000"
}
```

---

### Agent Status

#### Get Status
```http
GET /status
```

**Response:**
```json
{
  "session_id": "20260804_110000",
  "tools": ["filesystem", "web_search", "translation", "ner"],
  "models": ["deepseek", "gateway"],
  "session_messages": 5,
  "config": {
    "agent": {
      "name": "osmanlica-agent",
      "version": "0.1.0"
    }
  }
}
```

---

## Error Responses

### 400 Bad Request
```json
{
  "detail": "Text is required"
}
```

### 401 Unauthorized
```json
{
  "detail": "Invalid authentication token"
}
```

### 429 Too Many Requests
```json
{
  "detail": "Rate limit exceeded",
  "retry_after": 60
}
```

### 500 Internal Server Error
```json
{
  "detail": "Internal server error",
  "error": "Model API timeout"
}
```

---

## SDK Usage

### Python
```python
from ottoman_agent_pipeline import AgentOrchestrator

orch = AgentOrchestrator()
await orch.initialize()

# Transliterate
result = await orch.translate("عثمانli توركجهسى")
print(result.modern_turkish)

# Chat
result = await orch.chat("Merhaba")
print(result.output)
```

### JavaScript
```javascript
const { AgentOrchestrator } = require('ottoman-agent-pipeline');

const orch = new AgentOrchestrator();
await orch.initialize();

const result = await orch.translate('عثمانلي توركجهسى');
console.log(result.modern_turkish);
```

---

## Rate Limits

| Plan | Requests/min | Tokens/day |
|------|-------------|------------|
| Free | 60 | 100,000 |
| Pro | 600 | 1,000,000 |
| Enterprise | Custom | Custom |

---

## Webhooks

### Event: `transliteration.completed`
```json
{
  "event": "transliteration.completed",
  "data": {
    "session_id": "20260804_110000",
    "input": "عثمانli",
    "output": "Osmanlı",
    "confidence": 0.95
  }
}
```

---

*API Version: 1.0.0*
*Last Updated: 2026-08-04*
