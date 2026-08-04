# BYOK (Bring Your Own Key) Sistemi

Kullanıcıların kendi API key'lerini güvenli bir şekilde yönetmelerini sağlar.

## 🏗️ Mimari

```
┌─────────────────────────────────────────────────────────────┐
│                    BYOK System                              │
└─────────────────────────────────────────────────────────────┘
                           │
         ┌─────────────────┼─────────────────┐
         │                 │                 │
         ▼                 ▼                 ▼
┌──────────────┐ ┌──────────────┐ ┌──────────────┐
│  Key Vault   │ │  Encryption  │ │  Audit Log   │
│              │ │              │ │              │
│ • AES-256    │ │ • PBKDF2     │ │ • Create     │
│   GCM        │ │ • SHA-256    │ │ • Read       │
│ • Rotation   │ │ • Salt       │ │ • Rotate     │
│ • Scoping    │ │              │ │ • Revoke     │
└──────────────┘ └──────────────┘ └──────────────┘
```

## 🔐 Özellikler

- **AES-256-GCM Şifreleme**: Profesyonel şifreleme
- **Anahtar Rotasyonu**: Otomatik rotasyon policy'si
- **Scoping**: Per-agent, per-tool, per-user erişim
- **Audit Logging**: Tüm işlemler loglanır
- **Expiration**: Son kullanma tarihi takibi
- **Hardware Security**: HSM desteği (opsiyonel)

## 🚀 Kullanım

### Python API

```python
from ottoman_agent_pipeline.byok import get_keyvault, KeyScope

# Initialize
vault = get_keyvault()

# Create key
key_id = await vault.create_key(
    service="deepseek",
    api_key="sk-xxx",
    scope=KeyScope.AGENT,
    scope_id="agent_123",
    rotation_days=90
)

# Get key
api_key = await vault.get_key(key_id)

# Rotate key
await vault.rotate_key(key_id, "sk-new-key")

# Revoke key
await vault.revoke_key(key_id)

# List keys
keys = await vault.list_keys(service="deepseek")

# Get audit logs
logs = await vault.get_audit_logs(key_id=key_id)
```

### REST API

```bash
# Create key
curl -X POST http://localhost:8000/api/v1/byok/keys \
  -H "Content-Type: application/json" \
  -d '{
    "service": "deepseek",
    "api_key": "sk-xxx",
    "scope": "agent",
    "rotation_days": 90
  }'

# List keys
curl http://localhost:8000/api/v1/byok/keys

# Rotate key
curl -X POST http://localhost:8000/api/v1/byok/keys/{key_id}/rotate \
  -d '{"new_api_key": "sk-new"}'

# Revoke key
curl -X POST http://localhost:8000/api/v1/byok/keys/{key_id}/revoke

# Get audit logs
curl http://localhost:8000/api/v1/byok/keys/{key_id}/audit
```

## 📊 API Endpoints

### Keys
| Endpoint | Method | Açıklama |
|----------|--------|----------|
| `/api/v1/byok/keys` | GET | Key'leri listele |
| `/api/v1/byok/keys` | POST | Yeni key oluştur |
| `/api/v1/byok/keys/{id}` | GET | Key detayı |
| `/api/v1/byok/keys/{id}/rotate` | POST | Key rotasyonu |
| `/api/v1/byok/keys/{id}/revoke` | POST | Key iptal |
| `/api/v1/byok/keys/{id}/audit` | GET | Audit log |

### Stats
| Endpoint | Method | Açıklama |
|----------|--------|----------|
| `/api/v1/byok/keys/stats` | GET | İstatistikler |
| `/api/v1/byok/keys/audit` | GET | Tüm audit log |
| `/api/v1/byok/keys/rotation-needed` | GET | Rotasyon gerekenler |
| `/api/v1/byok/keys/cleanup` | POST | Eski key'leri temizle |

## 🔒 Güvenlik

### Encryption
```python
# Master key'den encryption key türet
derived_key = PBKDF2HMAC(
    algorithm=SHA256(),
    length=32,
    salt=b"ottoman-byok-salt",
    iterations=480000
).derive(master_key)

# AES-256-GCM ile şifrele
aesgcm = AESGCM(derived_key)
ciphertext = aesgcm.encrypt(iv, plaintext, None)
```

### Scoping
```python
# Key scope türleri
KeyScope.GLOBAL     # Tüm agent'lar için
KeyScope.AGENT      # Belirli agent için
KeyScope.TOOL       # Belirli tool için
KeyScope.USER       # Belirli kullanıcı için
KeyScope.SESSION    # Belirli session için
```

### Audit
```python
# Her işlem loglanır
AuditLog(
    action="create",  # create, read, rotate, revoke, use
    key_id="key_xxx",
    user_id="user_123",
    agent_id="agent_456",
    success=True
)
```

## 📚 Referanslar

- **Cryptography**: https://cryptography.io/
- **AES-GCM**: https://en.wikipedia.org/wiki/GCM_mode
- **PBKDF2**: https://en.wikipedia.org/wiki/PBKDF2

## 📄 License

MIT License
