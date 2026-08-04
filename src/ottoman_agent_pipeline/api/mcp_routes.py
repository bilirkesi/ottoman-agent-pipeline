"""
MCP API Routes - Model Context Protocol endpoints
"""

from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel, Field
from typing import List, Optional, Any, Dict

from ..mcp.registry import get_tool_registry, MCPToolRegistry

router = APIRouter(prefix="/api/v1/mcp", tags=["MCP - Model Context Protocol"])


# Request/Response models
class ToolInfo(BaseModel):
    tool_id: str
    name: str
    description: str
    parameters: dict
    rate_limit_per_minute: int
    enabled: bool


class ToolResponse(BaseModel):
    success: bool
    output: Optional[Any] = None
    error: Optional[str] = None
    duration_ms: float
    call_id: Optional[str] = None


class ToolStatsResponse(BaseModel):
    total_tools: int
    enabled_tools: int
    total_calls: int
    successful_calls: int
    success_rate: float
    avg_duration_ms: float
    calls_by_tool: Dict[str, int]


@router.get("/tools", response_model=List[ToolInfo])
async def list_tools(enabled_only: bool = Query(True)):
    """
    Tüm tool'ları listele
    """
    try:
        registry = get_tool_registry()
        tools = registry.list_tools(enabled_only=enabled_only)
        
        return [ToolInfo(**tool) for tool in tools]
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/tools/{tool_id}", response_model=ToolInfo)
async def get_tool(tool_id: str):
    """
    Tool detayı
    """
    try:
        registry = get_tool_registry()
        config = registry.get_tool(tool_id)
        
        if not config:
            raise HTTPException(status_code=404, detail="Tool not found")
        
        return ToolInfo(
            tool_id=config.tool_id,
            name=config.name,
            description=config.description,
            parameters=config.parameters,
            rate_limit_per_minute=config.rate_limit_per_minute,
            enabled=config.enabled
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/tools/{tool_id}/execute", response_model=ToolResponse)
async def execute_tool(
    tool_id: str,
    params: Dict[str, Any] = Field(..., description="Tool parametreleri")
):
    """
    Tool çalıştır
    
    - **tool_id**: Tool ID
    - **params**: Tool parametreleri (service-specific)
    
    Örnek:
    ```json
    {
      "text": "عثمانلي توركجهسى"
    }
    ```
    """
    try:
        registry = get_tool_registry()
        
        result = await registry.execute_tool(
            tool_id=tool_id,
            params=params
        )
        
        return ToolResponse(
            success=result["success"],
            output=result.get("output"),
            error=result.get("error"),
            duration_ms=result.get("duration_ms", 0),
            call_id=result.get("call_id")
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/tools/{tool_id}/stats")
async def get_tool_stats(tool_id: str):
    """
    Tool istatistikleri
    """
    try:
        registry = get_tool_registry()
        
        # Calculate stats for specific tool
        calls = [c for c in registry.call_history if c.tool_name == tool_id]
        
        if not calls:
            return {
                "tool_id": tool_id,
                "total_calls": 0,
                "successful_calls": 0,
                "avg_duration_ms": 0
            }
        
        successful = sum(1 for c in calls if c.error is None)
        avg_duration = sum(c.duration_ms for c in calls) / len(calls)
        
        return {
            "tool_id": tool_id,
            "total_calls": len(calls),
            "successful_calls": successful,
            "success_rate": successful / len(calls),
            "avg_duration_ms": avg_duration
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/tools/stats", response_model=ToolStatsResponse)
async def get_tools_stats():
    """
    Tüm tool istatistikleri
    """
    try:
        registry = get_tool_registry()
        stats = await registry.get_stats()
        
        return ToolStatsResponse(**stats)
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/tools/history")
async def get_tool_history(
    tool_id: Optional[str] = None,
    limit: int = Query(100, ge=1, le=1000)
):
    """
    Tool çağrı geçmişi
    """
    try:
        registry = get_tool_registry()
        
        if tool_id:
            calls = [c for c in registry.call_history if c.tool_name == tool_id]
        else:
            calls = registry.call_history
        
        calls = calls[-limit:]
        
        return {
            "calls": [call.to_dict() for call in calls],
            "total": len(calls)
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/tools/{tool_id}/enable")
async def enable_tool(tool_id: str):
    """
    Tool'u etkinleştir
    """
    try:
        registry = get_tool_registry()
        config = registry.get_tool(tool_id)
        
        if not config:
            raise HTTPException(status_code=404, detail="Tool not found")
        
        config.enabled = True
        registry._save()
        
        return {"success": True, "tool_id": tool_id, "enabled": True}
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/tools/{tool_id}/disable")
async def disable_tool(tool_id: str):
    """
    Tool'u devre dışı bırak
    """
    try:
        registry = get_tool_registry()
        config = registry.get_tool(tool_id)
        
        if not config:
            raise HTTPException(status_code=404, detail="Tool not found")
        
        config.enabled = False
        registry._save()
        
        return {"success": True, "tool_id": tool_id, "enabled": False}
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/tools/register")
async def register_tool(tool_config: dict):
    """
    Yeni tool kaydet
    
    ```json
    {
      "tool_id": "my_tool",
      "name": "My Tool",
      "description": "Description",
      "parameters": {...},
      "required_keys": ["deepseek"],
      "rate_limit_per_minute": 60
    }
    ```
    """
    try:
        from ..mcp.registry import ToolConfig
        
        registry = get_tool_registry()
        config = ToolConfig(**tool_config)
        
        registry.register_tool(config)
        
        return {"success": True, "tool_id": config.tool_id}
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/tools/{tool_id}")
async def unregister_tool(tool_id: str):
    """
    Tool kaldır
    """
    try:
        registry = get_tool_registry()
        success = registry.unregister_tool(tool_id)
        
        if not success:
            raise HTTPException(status_code=404, detail="Tool not found")
        
        return {"success": True, "tool_id": tool_id}
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
