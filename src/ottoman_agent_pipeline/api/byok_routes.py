"""
BYOK API Routes - Bring Your Own Key API endpoints
"""

from fastapi import APIRouter, HTTPException, Depends, Query
from pydantic import BaseModel, Field
from typing import List, Optional
from datetime import datetime

from ..byok.keyvault import (
    get_keyvault,
    KeyVault,
    KeyScope,
    KeyStatus
)

router = APIRouter(prefix="/api/v1/byok", tags=["BYOK - Bring Your Own Key"])


# Request/Response models
class CreateKeyRequest(BaseModel):
    service: str = Field(..., description="Servis adı (deepseek, anthropic, gateway, etc.)")
    api_key: str = Field(..., description="API key değeri")
    scope: str = Field("global", description="Erişim kapsamı (global, agent, tool, user, session)")
    scope_id: Optional[str] = None
    rotation_days: int = Field(90, description="Rotasyon süresi (gün)")
    expires_days: Optional[int] = None
    metadata: Optional[dict] = None


class CreateKeyResponse(BaseModel):
    key_id: str
    service: str
    scope: str
    created_at: str
    expires_at: Optional[str] = None


class ListKeysResponse(BaseModel):
    keys: List[dict]
    total: int


class KeyStatsResponse(BaseModel):
    total_keys: int
    active: int
    rotating: int
    revoked: int
    expired: int
    services: List[str]


class AuditLogResponse(BaseModel):
    log_id: str
    timestamp: str
    action: str
    key_id: Optional[str]
    user_id: Optional[str]
    agent_id: Optional[str]
    success: bool
    error_message: Optional[str]


@router.post("/keys", response_model=CreateKeyResponse)
async def create_key(request: CreateKeyRequest):
    """
    Yeni API key oluştur
    
    - **service**: Hangi servis için (deepseek, anthropic, openai, gateway, etc.)
    - **api_key**: Plaintext API key değeri (şifrelenecek)
    - **scope**: Erişim kapsamı (global, agent, tool, user, session)
    - **rotation_days**: Otomatik rotasyon süresi
    """
    try:
        vault = get_keyvault()
        
        # Parse scope
        scope = KeyScope.GLOBAL
        if request.scope:
            try:
                scope = KeyScope(request.scope)
            except ValueError:
                scope = KeyScope.GLOBAL
        
        # Create key
        key_id = await vault.create_key(
            service=request.service,
            api_key=request.api_key,
            scope=scope,
            scope_id=request.scope_id,
            rotation_days=request.rotation_days,
            expires_days=request.expires_days,
            metadata=request.metadata
        )
        
        # Get key metadata
        key_data = vault.keys[key_id]
        
        return CreateKeyResponse(
            key_id=key_id,
            service=key_data.metadata.service,
            scope=key_data.metadata.scope.value,
            created_at=key_data.metadata.created_at.isoformat(),
            expires_at=key_data.metadata.expires_at.isoformat() if key_data.metadata.expires_at else None
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/keys", response_model=ListKeysResponse)
async def list_keys(
    service: Optional[str] = None,
    scope: Optional[str] = None,
    status: Optional[str] = None,
    limit: int = Query(100, ge=1, le=1000)
):
    """
    Key'leri listele (sadece metadata, key value yok)
    
    - **service**: Servis filtresi
    - **scope**: Kapsam filtresi
    - **status**: Durum filtresi (active, rotating, revoked, expired)
    """
    try:
        vault = get_keyvault()
        
        # Parse filters
        scope_filter = None
        if scope:
            try:
                scope_filter = KeyScope(scope)
            except ValueError:
                pass
        
        status_filter = None
        if status:
            try:
                status_filter = KeyStatus(status)
            except ValueError:
                pass
        
        # List keys
        keys = await vault.list_keys(
            service=service,
            scope=scope_filter,
            status=status_filter
        )
        
        # Limit
        keys = keys[:limit]
        
        return ListKeysResponse(keys=keys, total=len(keys))
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/keys/{key_id}", response_model=dict)
async def get_key(key_id: str):
    """
    Key metadata getir (key value değil)
    """
    try:
        vault = get_keyvault()
        
        if key_id not in vault.keys:
            raise HTTPException(status_code=404, detail="Key not found")
        
        record = vault.keys[key_id]
        
        return {
            "key_id": key_id,
            "service": record.metadata.service,
            "scope": record.metadata.scope.value,
            "status": record.status.value,
            "created_at": record.metadata.created_at.isoformat(),
            "expires_at": record.metadata.expires_at.isoformat() if record.metadata.expires_at else None,
            "usage_count": record.metadata.usage_count,
            "last_used_at": record.metadata.last_used_at.isoformat() if record.metadata.last_used_at else None,
            "metadata": record.metadata.metadata
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/keys/{key_id}/rotate")
async def rotate_key(key_id: str, new_api_key: str = Field(..., description="Yeni API key")):
    """
    Key rotasyonu
    
    - **key_id**: Rotasyon yapılacak key ID
    - **new_api_key**: Yeni API key değeri
    """
    try:
        vault = get_keyvault()
        
        if key_id not in vault.keys:
            raise HTTPException(status_code=404, detail="Key not found")
        
        success = await vault.rotate_key(key_id, new_api_key)
        
        if not success:
            raise HTTPException(status_code=500, detail="Key rotation failed")
        
        return {"success": True, "key_id": key_id}
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/keys/{key_id}/revoke")
async def revoke_key(key_id: str):
    """
    Key iptal et
    """
    try:
        vault = get_keyvault()
        
        if key_id not in vault.keys:
            raise HTTPException(status_code=404, detail="Key not found")
        
        success = await vault.revoke_key(key_id)
        
        if not success:
            raise HTTPException(status_code=500, detail="Key revocation failed")
        
        return {"success": True, "key_id": key_id}
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/keys/{key_id}/audit")
async def get_key_audit(key_id: str, limit: int = Query(100, ge=1, le=1000)):
    """
    Key audit log'ları
    """
    try:
        vault = get_keyvault()
        
        logs = await vault.get_audit_logs(key_id=key_id, limit=limit)
        
        return {"key_id": key_id, "logs": logs, "total": len(logs)}
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/keys/stats", response_model=KeyStatsResponse)
async def get_key_stats():
    """
    Key vault istatistikleri
    """
    try:
        vault = get_keyvault()
        stats = await vault.get_stats()
        
        return KeyStatsResponse(**stats)
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/keys/audit")
async def get_all_audit_logs(
    action: Optional[str] = None,
    limit: int = Query(100, ge=1, le=1000)
):
    """
    Tüm audit log'ları
    """
    try:
        vault = get_keyvault()
        logs = await vault.get_audit_logs(action=action, limit=limit)
        
        return {"logs": logs, "total": len(logs)}
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/keys/cleanup")
async def cleanup_expired_keys():
    """
    Süresi dolmuş key'leri temizle
    """
    try:
        vault = get_keyvault()
        cleaned = await vault.cleanup_expired_keys()
        
        return {"cleaned": cleaned}
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/keys/rotation-needed")
async def get_rotation_needed():
    """
    Rotasyonu gerekli key'ler
    """
    try:
        vault = get_keyvault()
        needs_rotation = await vault.check_rotation_needed()
        
        return {
            "needs_rotation": needs_rotation,
            "count": len(needs_rotation)
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
