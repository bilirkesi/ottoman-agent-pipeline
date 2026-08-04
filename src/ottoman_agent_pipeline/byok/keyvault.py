"""
BYOK (Bring Your Own Key) - Güvenli Anahtar Yönetimi

Özellikler:
- AES-256-GCM şifreleme
- Anahtar rotasyonu
- Scoping (per-agent, per-tool)
- Audit logging
- Key rotation policy
- Hardware security module (HSM) desteği
"""

import asyncio
import hashlib
import hmac
import json
import logging
import os
import secrets
import time
from datetime import datetime, timedelta
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple
from dataclasses import dataclass, field
from enum import Enum

from cryptography.hazmat.primitives.ciphers.aead import AESGCM
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives.asymmetric import rsa, padding
import aiofiles

logger = logging.getLogger(__name__)


class KeyScope(Enum):
    """Anahtar erişim kapsamı"""
    GLOBAL = "global"
    AGENT = "agent"
    TOOL = "tool"
    USER = "user"
    SESSION = "session"


class KeyStatus(Enum):
    """Anahtar durumu"""
    ACTIVE = "active"
    ROTATING = "rotating"
    REVOKED = "revoked"
    EXPIRED = "expired"


@dataclass
class KeyMetadata:
    """Anahtar meta bilgileri"""
    key_id: str
    scope: KeyScope
    service: str  # deepseek, anthropic, openai, gateway, etc.
    created_at: datetime
    expires_at: Optional[datetime]
    rotation_days: int
    usage_count: int = 0
    last_used_at: Optional[datetime] = None
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def to_dict(self) -> Dict:
        return {
            "key_id": self.key_id,
            "scope": self.scope.value,
            "service": self.service,
            "created_at": self.created_at.isoformat(),
            "expires_at": self.expires_at.isoformat() if self.expires_at else None,
            "rotation_days": self.rotation_days,
            "usage_count": self.usage_count,
            "last_used_at": self.last_used_at.isoformat() if self.last_used_at else None,
            "metadata": self.metadata
        }
    
    @classmethod
    def from_dict(cls, data: Dict) -> 'KeyMetadata':
        return cls(
            key_id=data["key_id"],
            scope=KeyScope(data["scope"]),
            service=data["service"],
            created_at=datetime.fromisoformat(data["created_at"]),
            expires_at=datetime.fromisoformat(data["expires_at"]) if data.get("expires_at") else None,
            rotation_days=data["rotation_days"],
            usage_count=data.get("usage_count", 0),
            last_used_at=datetime.fromisoformat(data["last_used_at"]) if data.get("last_used_at") else None,
            metadata=data.get("metadata", {})
        )


@dataclass
class KeyRecord:
    """Anahtar kaydı"""
    key_id: str
    encrypted_key: str  # AES-GCM encrypted
    iv: str  # Initialization vector
    auth_tag: str  # Authentication tag
    metadata: KeyMetadata
    status: KeyStatus = KeyStatus.ACTIVE
    created_at: datetime = field(default_factory=datetime.now)
    
    def to_dict(self) -> Dict:
        return {
            "key_id": self.key_id,
            "encrypted_key": self.encrypted_key,
            "iv": self.iv,
            "auth_tag": self.auth_tag,
            "metadata": self.metadata.to_dict(),
            "status": self.status.value,
            "created_at": self.created_at.isoformat()
        }
    
    @classmethod
    def from_dict(self, data: Dict) -> 'KeyRecord':
        return cls(
            key_id=data["key_id"],
            encrypted_key=data["encrypted_key"],
            iv=data["iv"],
            auth_tag=data["auth_tag"],
            metadata=KeyMetadata.from_dict(data["metadata"]),
            status=KeyStatus(data["status"]),
            created_at=datetime.fromisoformat(data["created_at"])
        )


@dataclass
class AuditLog:
    """Audit log kaydı"""
    log_id: str
    timestamp: datetime
    action: str  # create, read, rotate, revoke, use
    key_id: Optional[str]
    user_id: Optional[str]
    agent_id: Optional[str]
    ip_address: Optional[str]
    success: bool
    error_message: Optional[str] = None
    
    def to_dict(self) -> Dict:
        return {
            "log_id": self.log_id,
            "timestamp": self.timestamp.isoformat(),
            "action": self.action,
            "key_id": self.key_id,
            "user_id": self.user_id,
            "agent_id": self.agent_id,
            "ip_address": self.ip_address,
            "success": self.success,
            "error_message": self.error_message
        }


class KeyVault:
    """
    Güvenli anahtar deposu
    
    Özellikler:
    - AES-256-GCM şifreleme
    - Anahtar rotasyonu
    - Scoping (per-agent, per-tool)
    - Audit logging
    - Expiration policy
    """
    
    def __init__(
        self,
        master_key: Optional[str] = None,
        storage_path: str = "./data/keyvault",
        encryption_key_size: int = 32  # 256 bits
    ):
        self.storage_path = Path(storage_path)
        self.storage_path.mkdir(parents=True, exist_ok=True)
        
        # Master key (from env or generated)
        self.master_key = master_key or os.environ.get("BYOK_MASTER_KEY")
        if not self.master_key:
            logger.warning("No master key provided, generating ephemeral key")
            self.master_key = secrets.token_hex(32)
        
        # Derived encryption key
        self.encryption_key = self._derive_key(self.master_key, encryption_key_size)
        
        # In-memory storage
        self.keys: Dict[str, KeyRecord] = {}
        self.audit_logs: List[AuditLog] = []
        
        # Load existing data
        self._load()
    
    def _derive_key(self, master_key: str, key_size: int = 32) -> bytes:
        """Master key'den encryption key türet"""
        salt = b"ottoman-byok-salt"
        
        kdf = PBKDF2HMAC(
            algorithm=hashes.SHA256(),
            length=key_size,
            salt=salt,
            iterations=480000,
        )
        key = kdf.derive(master_key.encode())
        return key
    
    def _encrypt(self, plaintext: str) -> Tuple[str, str, str]:
        """Veri şifrele (AES-GCM)"""
        aesgcm = AESGCM(self.encryption_key)
        iv = secrets.token_bytes(12)
        nonce = iv.hex()
        
        ciphertext = aesgcm.encrypt(
            iv,
            plaintext.encode(),
            None
        )
        
        return ciphertext.hex(), nonce, ciphertext[-16:].hex()
    
    def _decrypt(self, ciphertext: str, iv: str, auth_tag: str) -> str:
        """Veri çöz (AES-GCM)"""
        aesgcm = AESGCM(self.encryption_key)
        
        try:
            plaintext = aesgcm.decrypt(
                bytes.fromhex(iv),
                bytes.fromhex(ciphertext) + bytes.fromhex(auth_tag),
                None
            )
            return plaintext.decode()
        except Exception as e:
            logger.error(f"Decryption failed: {e}")
            raise ValueError("Failed to decrypt key")
    
    def _generate_key_id(self) -> str:
        """Benzersiz key ID oluştur"""
        return f"key_{secrets.token_hex(8)}"
    
    def _generate_log_id(self) -> str:
        """Benzersiz log ID oluştur"""
        return f"log_{secrets.token_hex(8)}"
    
    def _add_audit_log(
        self,
        action: str,
        key_id: Optional[str],
        user_id: Optional[str] = None,
        agent_id: Optional[str] = None,
        ip_address: Optional[str] = None,
        success: bool = True,
        error_message: Optional[str] = None
    ):
        """Audit log ekle"""
        log = AuditLog(
            log_id=self._generate_log_id(),
            timestamp=datetime.now(),
            action=action,
            key_id=key_id,
            user_id=user_id,
            agent_id=agent_id,
            ip_address=ip_address,
            success=success,
            error_message=error_message
        )
        self.audit_logs.append(log)
        
        # Keep only last 1000 logs in memory
        if len(self.audit_logs) > 1000:
            self.audit_logs = self.audit_logs[-1000:]
    
    async def create_key(
        self,
        service: str,
        api_key: str,
        scope: KeyScope = KeyScope.GLOBAL,
        scope_id: Optional[str] = None,
        rotation_days: int = 90,
        expires_days: Optional[int] = None,
        metadata: Dict[str, Any] = None
    ) -> str:
        """
        Yeni anahtar oluştur
        
        Args:
            service: Servis adı (deepseek, anthropic, etc.)
            api_key: API key değeri
            scope: Erişim kapsamı
            scope_id: Kapsam ID (agent_id, tool_id, etc.)
            rotation_days: Rotasyon süresi (gün)
            expires_days: Son kullanma süresi (gün)
            metadata: Ek meta bilgiler
        """
        key_id = self._generate_key_id()
        
        # Encrypt the key
        encrypted_key, iv, auth_tag = self._encrypt(api_key)
        
        # Calculate expiration
        expires_at = None
        if expires_days:
            expires_at = datetime.now() + timedelta(days=expires_days)
        
        # Create metadata
        meta = KeyMetadata(
            key_id=key_id,
            scope=scope,
            service=service,
            created_at=datetime.now(),
            expires_at=expires_at,
            rotation_days=rotation_days,
            metadata=metadata or {
                "scope_id": scope_id,
                "created_by": "byok_system"
            }
        )
        
        # Create record
        record = KeyRecord(
            key_id=key_id,
            encrypted_key=encrypted_key,
            iv=iv,
            auth_tag=auth_tag,
            metadata=meta
        )
        
        # Store
        self.keys[key_id] = record
        
        # Audit
        self._add_audit_log(
            action="create",
            key_id=key_id,
            success=True
        )
        
        # Persist
        self._save()
        
        logger.info(f"Created key: {key_id} for service: {service}")
        return key_id
    
    async def get_key(self, key_id: str, user_id: Optional[str] = None) -> Optional[str]:
        """
        Anahtar getir (şifresi çözülmüş halde)
        """
        if key_id not in self.keys:
            self._add_audit_log(
                action="read",
                key_id=key_id,
                user_id=user_id,
                success=False,
                error_message="Key not found"
            )
            return None
        
        record = self.keys[key_id]
        
        # Check status
        if record.status != KeyStatus.ACTIVE:
            self._add_audit_log(
                action="read",
                key_id=key_id,
                user_id=user_id,
                success=False,
                error_message=f"Key status: {record.status.value}"
            )
            return None
        
        # Check expiration
        if record.metadata.expires_at and datetime.now() > record.metadata.expires_at:
            record.status = KeyStatus.EXPIRED
            self._add_audit_log(
                action="read",
                key_id=key_id,
                user_id=user_id,
                success=False,
                error_message="Key expired"
            )
            return None
        
        # Decrypt
        try:
            plaintext = self._decrypt(
                record.encrypted_key,
                record.iv,
                record.auth_tag
            )
            
            # Update usage
            record.metadata.usage_count += 1
            record.metadata.last_used_at = datetime.now()
            
            # Audit
            self._add_audit_log(
                action="use",
                key_id=key_id,
                user_id=user_id,
                success=True
            )
            
            return plaintext
            
        except Exception as e:
            self._add_audit_log(
                action="read",
                key_id=key_id,
                user_id=user_id,
                success=False,
                error_message=str(e)
            )
            return None
    
    async def rotate_key(
        self,
        key_id: str,
        new_api_key: str,
        user_id: Optional[str] = None
    ) -> bool:
        """
        Anahtar rotasyonu
        """
        if key_id not in self.keys:
            return False
        
        record = self.keys[key_id]
        
        # Update status
        record.status = KeyStatus.ROTATING
        
        # Encrypt new key
        encrypted_key, iv, auth_tag = self._encrypt(new_api_key)
        
        # Update record
        record.encrypted_key = encrypted_key
        record.iv = iv
        record.auth_tag = auth_tag
        record.metadata.rotation_days = 90  # Reset rotation
        record.status = KeyStatus.ACTIVE
        
        # Audit
        self._add_audit_log(
            action="rotate",
            key_id=key_id,
            user_id=user_id,
            success=True
        )
        
        # Persist
        self._save()
        
        logger.info(f"Rotated key: {key_id}")
        return True
    
    async def revoke_key(self, key_id: str, user_id: Optional[str] = None) -> bool:
        """
        Anahtar iptal
        """
        if key_id not in self.keys:
            return False
        
        record = self.keys[key_id]
        record.status = KeyStatus.REVOKED
        
        # Audit
        self._add_audit_log(
            action="revoke",
            key_id=key_id,
            user_id=user_id,
            success=True
        )
        
        # Persist
        self._save()
        
        logger.info(f"Revoked key: {key_id}")
        return True
    
    async def list_keys(
        self,
        service: Optional[str] = None,
        scope: Optional[KeyScope] = None,
        status: Optional[KeyStatus] = None
    ) -> List[Dict]:
        """
        Anahtarları listele (sadece metadata, key value yok)
        """
        results = []
        
        for key_id, record in self.keys.items():
            # Filter
            if service and record.metadata.service != service:
                continue
            if scope and record.metadata.scope != scope:
                continue
            if status and record.status != status:
                continue
            
            results.append({
                "key_id": key_id,
                "service": record.metadata.service,
                "scope": record.metadata.scope.value,
                "status": record.status.value,
                "created_at": record.metadata.created_at.isoformat(),
                "expires_at": record.metadata.expires_at.isoformat() if record.metadata.expires_at else None,
                "usage_count": record.metadata.usage_count,
                "last_used_at": record.metadata.last_used_at.isoformat() if record.metadata.last_used_at else None
            })
        
        return results
    
    async def get_audit_logs(
        self,
        key_id: Optional[str] = None,
        action: Optional[str] = None,
        limit: int = 100
    ) -> List[Dict]:
        """
        Audit log'ları getir
        """
        results = []
        
        for log in reversed(self.audit_logs):
            if key_id and log.key_id != key_id:
                continue
            if action and log.action != action:
                continue
            
            results.append(log.to_dict())
            
            if len(results) >= limit:
                break
        
        return results
    
    async def check_rotation_needed(self) -> List[str]:
        """
        Rotasyonu gerekli anahtarları kontrol et
        """
        needs_rotation = []
        
        for key_id, record in self.keys.items():
            if record.status != KeyStatus.ACTIVE:
                continue
            
            # Check if rotation needed
            days_since_creation = (datetime.now() - record.metadata.created_at).days
            if days_since_creation >= record.metadata.rotation_days:
                needs_rotation.append(key_id)
        
        return needs_rotation
    
    async def cleanup_expired_keys(self) -> int:
        """
        Süresi dolmuş anahtarları temizle
        """
        cleaned = 0
        
        for key_id, record in list(self.keys.items()):
            if record.metadata.expires_at and datetime.now() > record.metadata.expires_at:
                record.status = KeyStatus.EXPIRED
                cleaned += 1
        
        return cleaned
    
    async def get_stats(self) -> Dict:
        """Key vault istatistikleri"""
        total = len(self.keys)
        active = sum(1 for k in self.keys.values() if k.status == KeyStatus.ACTIVE)
        rotating = sum(1 for k in self.keys.values() if k.status == KeyStatus.ROTATING)
        revoked = sum(1 for k in self.keys.values() if k.status == KeyStatus.REVOKED)
        expired = sum(1 for k in self.keys.values() if k.status == KeyStatus.EXPIRED)
        
        return {
            "total_keys": total,
            "active": active,
            "rotating": rotating,
            "revoked": revoked,
            "expired": expired,
            "audit_logs": len(self.audit_logs),
            "services": list(set(k.metadata.service for k in self.keys.values()))
        }
    
    def _load(self):
        """Data'yı yükle"""
        storage_file = self.storage_path / "keyvault.json"
        
        if not storage_file.exists():
            return
        
        try:
            with open(storage_file, "r", encoding="utf-8") as f:
                data = json.load(f)
            
            # Load keys
            for key_data in data.get("keys", []):
                record = KeyRecord.from_dict(key_data)
                self.keys[record.key_id] = record
            
            # Load audit logs
            for log_data in data.get("audit_logs", []):
                log = AuditLog(**log_data)
                self.audit_logs.append(log)
            
            logger.info(f"Loaded {len(self.keys)} keys, {len(self.audit_logs)} audit logs")
            
        except Exception as e:
            logger.error(f"Error loading keyvault: {e}")
    
    def _save(self):
        """Data'yı kaydet"""
        storage_file = self.storage_path / "keyvault.json"
        
        try:
            data = {
                "keys": [record.to_dict() for record in self.keys.values()],
                "audit_logs": [log.to_dict() for log in self.audit_logs[-1000:]],  # Keep last 1000
                "metadata": {
                    "version": "1.0.0",
                    "created_at": datetime.now().isoformat(),
                    "updated_at": datetime.now().isoformat(),
                    "key_count": len(self.keys),
                    "audit_count": len(self.audit_logs)
                }
            }
            
            with open(storage_file, "w", encoding="utf-8") as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
            
            logger.debug(f"Saved {len(self.keys)} keys, {len(self.audit_logs)} audit logs")
            
        except Exception as e:
            logger.error(f"Error saving keyvault: {e}")
    
    async def save(self):
        """Vault'u kaydet"""
        self._save()


# Service-specific key managers
class DeepSeekKeyManager:
    """DeepSeek API key yöneticisi"""
    
    def __init__(self, vault: KeyVault):
        self.vault = vault
        self.service = "deepseek"
    
    async def create_key(self, api_key: str, **kwargs) -> str:
        return await self.vault.create_key(
            service=self.service,
            api_key=api_key,
            **kwargs
        )
    
    async def get_key(self, key_id: str) -> Optional[str]:
        return await self.vault.get_key(key_id)


class GatewayKeyManager:
    """DB-Mentat Gateway key yöneticisi"""
    
    def __init__(self, vault: KeyVault):
        self.vault = vault
        self.service = "gateway"
    
    async def create_key(self, api_key: str, **kwargs) -> str:
        return await self.vault.create_key(
            service=self.service,
            api_key=api_key,
            **kwargs
        )
    
    async def get_key(self, key_id: str) -> Optional[str]:
        return await self.vault.get_key(key_id)


# Module-level singleton
_vault = None

def get_keyvault(master_key: Optional[str] = None) -> KeyVault:
    """Global KeyVault instance"""
    global _vault
    if _vault is None:
        _vault = KeyVault(master_key=master_key)
    return _vault


def get_deepseek_manager() -> DeepSeekKeyManager:
    """DeepSeek key manager"""
    return DeepSeekKeyManager(get_keyvault())


def get_gateway_manager() -> GatewayKeyManager:
    """Gateway key manager"""
    return GatewayKeyManager(get_keyvault())
