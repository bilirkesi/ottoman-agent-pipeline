"""
MCP (Model Context Protocol) Tool Registry

Özellikler:
- Tool registration ve discovery
- Key-based authentication
- Rate limiting
- Audit logging
- Hot reload
"""

import asyncio
import json
import logging
import time
from datetime import datetime, timedelta
from pathlib import Path
from typing import Any, Dict, List, Optional, Set
from dataclasses import dataclass, field

from loguru import logger

logger = logging.getLogger(__name__)


@dataclass
class ToolCall:
    """Tool çağrı kaydı"""
    call_id: str
    tool_name: str
    input_params: Dict[str, Any]
    output: Any
    started_at: datetime
    completed_at: Optional[datetime] = None
    duration_ms: float = 0.0
    error: Optional[str] = None
    key_id: Optional[str] = None
    
    def to_dict(self) -> Dict:
        return {
            "call_id": self.call_id,
            "tool_name": self.tool_name,
            "input_params": self.input_params,
            "output": str(self.output)[:500] if self.output else None,
            "started_at": self.started_at.isoformat(),
            "completed_at": self.completed_at.isoformat() if self.completed_at else None,
            "duration_ms": self.duration_ms,
            "error": self.error,
            "key_id": self.key_id
        }


@dataclass
class ToolConfig:
    """Tool konfigürasyonu"""
    tool_id: str
    name: str
    description: str
    parameters: Dict[str, Any]
    required_keys: List[str] = field(default_factory=list)
    rate_limit_per_minute: int = 60
    rate_limit_per_hour: int = 1000
    timeout_seconds: int = 30
    enabled: bool = True
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def to_dict(self) -> Dict:
        return {
            "tool_id": self.tool_id,
            "name": self.name,
            "description": self.description,
            "parameters": self.parameters,
            "required_keys": self.required_keys,
            "rate_limit_per_minute": self.rate_limit_per_minute,
            "rate_limit_per_hour": self.rate_limit_per_hour,
            "timeout_seconds": self.timeout_seconds,
            "enabled": self.enabled,
            "metadata": self.metadata
        }
    
    @classmethod
    def from_dict(cls, data: Dict) -> 'ToolConfig':
        return cls(
            tool_id=data["tool_id"],
            name=data["name"],
            description=data["description"],
            parameters=data["parameters"],
            required_keys=data.get("required_keys", []),
            rate_limit_per_minute=data.get("rate_limit_per_minute", 60),
            rate_limit_per_hour=data.get("rate_limit_per_hour", 1000),
            timeout_seconds=data.get("timeout_seconds", 30),
            enabled=data.get("enabled", True),
            metadata=data.get("metadata", {})
        )


class MCPToolRegistry:
    """
    MCP Tool Registry
    
    Özellikler:
    - Tool registration
    - Key-based authentication
    - Rate limiting
    - Audit logging
    - Hot reload
    """
    
    def __init__(self, storage_path: str = "./data/mcp_tools"):
        self.storage_path = Path(storage_path)
        self.storage_path.mkdir(parents=True, exist_ok=True)
        
        # Tool registry
        self.tools: Dict[str, ToolConfig] = {}
        
        # Rate limit tracking
        self.rate_limits: Dict[str, List[float]] = {}  # tool_id -> [timestamps]
        
        # Call history
        self.call_history: List[ToolCall] = []
        self.max_history = 10000
        
        # Event handlers
        self._event_handlers: Dict[str, List[callable]] = {}
        
        # Load existing tools
        self._load()
        
        logger.info(f"MCPToolRegistry initialized with {len(self.tools)} tools")
    
    def register_tool(self, config: ToolConfig):
        """Tool kaydet"""
        self.tools[config.tool_id] = config
        self._save()
        
        logger.info(f"Registered tool: {config.name} ({config.tool_id})")
        
        # Emit event
        self._emit("tool_registered", config)
    
    def unregister_tool(self, tool_id: str) -> bool:
        """Tool kaldır"""
        if tool_id not in self.tools:
            return False
        
        del self.tools[tool_id]
        self._save()
        
        logger.info(f"Unregistered tool: {tool_id}")
        return True
    
    def get_tool(self, tool_id: str) -> Optional[ToolConfig]:
        """Tool getir"""
        return self.tools.get(tool_id)
    
    def list_tools(self, enabled_only: bool = True) -> List[Dict]:
        """Tool'ları listele"""
        results = []
        
        for tool_id, config in self.tools.items():
            if enabled_only and not config.enabled:
                continue
            
            results.append({
                "tool_id": tool_id,
                "name": config.name,
                "description": config.description,
                "parameters": config.parameters,
                "rate_limit_per_minute": config.rate_limit_per_minute,
                "enabled": config.enabled
            })
        
        return results
    
    async def execute_tool(
        self,
        tool_id: str,
        params: Dict[str, Any],
        key_id: Optional[str] = None,
        user_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Tool çalıştır
        
        Returns:
            {"success": bool, "output": Any, "error": str, "duration_ms": float}
        """
        start_time = time.time()
        call_id = f"call_{datetime.now().strftime('%Y%m%d_%H%M%S_%f')}"
        
        # Check tool exists
        if tool_id not in self.tools:
            return {
                "success": False,
                "error": f"Tool not found: {tool_id}",
                "duration_ms": 0
            }
        
        config = self.tools[tool_id]
        
        # Check enabled
        if not config.enabled:
            return {
                "success": False,
                "error": f"Tool disabled: {tool_id}",
                "duration_ms": 0
            }
        
        # Check rate limit
        if not await self._check_rate_limit(tool_id):
            return {
                "success": False,
                "error": "Rate limit exceeded",
                "duration_ms": 0
            }
        
        # Check required keys
        if config.required_keys and not key_id:
            return {
                "success": False,
                "error": f"Missing required keys: {config.required_keys}",
                "duration_ms": 0
            }
        
        # Create call record
        call = ToolCall(
            call_id=call_id,
            tool_name=config.name,
            input_params=params,
            output=None,
            started_at=datetime.now(),
            key_id=key_id
        )
        
        try:
            # Execute tool
            output = await self._execute(config, params, key_id)
            
            # Update call
            call.output = output
            call.completed_at = datetime.now()
            call.duration_ms = (time.time() - start_time) * 1000
            call.error = None
            
            # Success
            return {
                "success": True,
                "output": output,
                "duration_ms": call.duration_ms,
                "call_id": call_id
            }
            
        except Exception as e:
            # Error
            call.error = str(e)
            call.completed_at = datetime.now()
            call.duration_ms = (time.time() - start_time) * 1000
            
            logger.error(f"Tool execution failed: {tool_id} - {e}")
            
            return {
                "success": False,
                "error": str(e),
                "duration_ms": call.duration_ms,
                "call_id": call_id
            }
        
        finally:
            # Save call history
            self.call_history.append(call)
            if len(self.call_history) > self.max_history:
                self.call_history = self.call_history[-self.max_history:]
            
            # Emit event
            self._emit("tool_executed", {
                "tool_id": tool_id,
                "success": call.error is None,
                "duration_ms": call.duration_ms
            })
    
    async def _execute(self, config: ToolConfig, params: Dict, key_id: Optional[str]) -> Any:
        """Tool execute"""
        # Import tool implementation
        tool_module = f"ottoman_agent_pipeline.mcp.tools.{config.tool_id}"
        
        try:
            # Dynamic import
            import importlib
            module = importlib.import_module(tool_module)
            
            # Get execute function
            if hasattr(module, 'execute'):
                return await module.execute(params, key_id)
            else:
                raise ValueError(f"No execute function in {tool_module}")
                
        except ImportError:
            # Try built-in handlers
            handler = self._get_handler(config.tool_id)
            if handler:
                return await handler(params, key_id)
            else:
                raise ValueError(f"Tool not implemented: {config.tool_id}")
    
    def _get_handler(self, tool_id: str) -> Optional[callable]:
        """Handler bul"""
        # Built-in handlers
        handlers = {
            "filesystem": self._handle_filesystem,
            "web_search": self._handle_web_search,
            "translation": self._handle_translation,
            "ner": self._handle_ner
        }
        return handlers.get(tool_id)
    
    async def _handle_filesystem(self, params: Dict, key_id: Optional[str]) -> Dict:
        """Filesystem handler"""
        from ottoman_agent_pipeline.tools.filesystem import FileSystemTool
        
        tool = FileSystemTool()
        action = params.get("action", "read")
        
        if action == "read":
            content = await tool.execute("read", path=params.get("path", "."))
            return {"content": content}
        elif action == "write":
            result = await tool.execute("write", path=params.get("path"), content=params.get("content", ""))
            return {"result": result}
        elif action == "list":
            entries = await tool.execute("list", path=params.get("path", "."))
            return {"entries": entries}
        else:
            raise ValueError(f"Unknown filesystem action: {action}")
    
    async def _handle_web_search(self, params: Dict, key_id: Optional[str]) -> Dict:
        """Web search handler"""
        from ottoman_agent_pipeline.tools.web import WebSearchTool
        
        tool = WebSearchTool()
        query = params.get("query", "")
        
        results = await tool.execute("search", query=query)
        return {"results": results}
    
    async def _handle_translation(self, params: Dict, key_id: Optional[str]) -> Dict:
        """Translation handler"""
        from ottoman_agent_pipeline.tools.translation import TranslationTool
        
        tool = TranslationTool()
        text = params.get("text", "")
        
        result = await tool.execute("transliterate", text=text)
        return result
    
    async def _handle_ner(self, params: Dict, key_id: Optional[str]) -> Dict:
        """NER handler"""
        from ottoman_agent_pipeline.tools.ner import NERTool
        
        tool = NERTool()
        text = params.get("text", "")
        
        result = await tool.execute("extract", text=text)
        return result
    
    async def _check_rate_limit(self, tool_id: str) -> bool:
        """Rate limit kontrol"""
        if tool_id not in self.tools:
            return True
        
        config = self.tools[tool_id]
        now = time.time()
        
        # Initialize tracking
        if tool_id not in self.rate_limits:
            self.rate_limits[tool_id] = []
        
        # Clean old entries
        one_minute_ago = now - 60
        one_hour_ago = now - 3600
        
        self.rate_limits[tool_id] = [
            t for t in self.rate_limits[tool_id]
            if t > one_hour_ago
        ]
        
        # Check minute limit
        recent_calls = sum(1 for t in self.rate_limits[tool_id] if t > one_minute_ago)
        if recent_calls >= config.rate_limit_per_minute:
            return False
        
        # Check hour limit
        if len(self.rate_limits[tool_id]) >= config.rate_limit_per_hour:
            return False
        
        # Record call
        self.rate_limits[tool_id].append(now)
        return True
    
    def on(self, event: str, handler: callable):
        """Event handler ekle"""
        if event not in self._event_handlers:
            self._event_handlers[event] = []
        self._event_handlers[event].append(handler)
    
    def _emit(self, event: str, data: Dict):
        """Event gönder"""
        handlers = self._event_handlers.get(event, [])
        for handler in handlers:
            try:
                if asyncio.iscoroutinefunction(handler):
                    asyncio.create_task(handler(data))
                else:
                    handler(data)
            except Exception as e:
                logger.error(f"Event handler error: {e}")
    
    async def get_stats(self) -> Dict:
        """Registry istatistikleri"""
        total_calls = len(self.call_history)
        successful_calls = sum(1 for c in self.call_history if c.error is None)
        avg_duration = sum(c.duration_ms for c in self.call_history) / max(total_calls, 1)
        
        return {
            "total_tools": len(self.tools),
            "enabled_tools": sum(1 for t in self.tools.values() if t.enabled),
            "total_calls": total_calls,
            "successful_calls": successful_calls,
            "success_rate": successful_calls / max(total_calls, 1),
            "avg_duration_ms": avg_duration,
            "calls_by_tool": self._calls_by_tool()
        }
    
    def _calls_by_tool(self) -> Dict[str, int]:
        """Tool bazında çağrı sayısı"""
        counts = {}
        for call in self.call_history:
            counts[call.tool_name] = counts.get(call.tool_name, 0) + 1
        return counts
    
    async def _load(self):
        """Data'yı yükle"""
        storage_file = self.storage_path / "registry.json"
        
        if not storage_file.exists():
            # Initialize with default tools
            self._init_default_tools()
            return
        
        try:
            async with aiofiles.open(storage_file, 'r', encoding='utf-8') as f:
                data = json.loads(await f.read())
            
            # Load tools
            for tool_data in data.get("tools", []):
                config = ToolConfig.from_dict(tool_data)
                self.tools[config.tool_id] = config
            
            # Load call history
            for call_data in data.get("call_history", []):
                call = ToolCall(**call_data)
                self.call_history.append(call)
            
            logger.info(f"Loaded {len(self.tools)} tools, {len(self.call_history)} call history")
            
        except Exception as e:
            logger.error(f"Error loading registry: {e}")
            self._init_default_tools()
    
    async def _save(self):
        """Data'yı kaydet"""
        storage_file = self.storage_path / "registry.json"
        
        try:
            data = {
                "tools": [config.to_dict() for config in self.tools.values()],
                "call_history": [call.to_dict() for call in self.call_history[-1000:]],  # Keep last 1000
                "metadata": {
                    "version": "1.0.0",
                    "created_at": datetime.now().isoformat(),
                    "updated_at": datetime.now().isoformat()
                }
            }
            
            async with aiofiles.open(storage_file, 'w', encoding='utf-8') as f:
                await f.write(json.dumps(data, indent=2, ensure_ascii=False))
            
        except Exception as e:
            logger.error(f"Error saving registry: {e}")
    
    def _init_default_tools(self):
        """Varsayılan tool'ları başlat"""
        default_tools = [
            ToolConfig(
                tool_id="filesystem",
                name="File System",
                description="File system operations (read, write, list, search)",
                parameters={
                    "action": {"type": "string", "enum": ["read", "write", "list", "search"]},
                    "path": {"type": "string"},
                    "content": {"type": "string"}
                },
                enabled=True
            ),
            ToolConfig(
                tool_id="web_search",
                name="Web Search",
                description="Search the web for information",
                parameters={
                    "query": {"type": "string"},
                    "max_results": {"type": "integer", "default": 10}
                },
                enabled=True
            ),
            ToolConfig(
                tool_id="translation",
                name="Translation",
                description="Ottoman Turkish to Modern Turkish transliteration",
                parameters={
                    "text": {"type": "string"},
                    "mode": {"type": "string", "enum": ["hybrid", "neural", "nlp"]}
                },
                required_keys=["deepseek"],
                enabled=True
            ),
            ToolConfig(
                tool_id="ner",
                name="Named Entity Recognition",
                description="Extract named entities from text",
                parameters={
                    "text": {"type": "string"},
                    "entity_types": {"type": "array", "items": {"type": "string"}}
                },
                enabled=True
            )
        ]
        
        for tool in default_tools:
            self.tools[tool.tool_id] = tool
        
        self._save()
        logger.info("Initialized default tools")


# Module-level singleton
_registry = None

def get_tool_registry() -> MCPToolRegistry:
    """Global registry instance"""
    global _registry
    if _registry is None:
        _registry = MCPToolRegistry()
    return _registry
