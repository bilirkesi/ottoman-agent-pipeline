"""
Agent Session - Persistent conversation state management
"""

import json
import logging
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional

from pydantic import BaseModel, ConfigDict, Field

logger = logging.getLogger(__name__)


class Message(BaseModel):
    """Chat message."""
    
    role: str  # "user", "assistant", "system"
    content: str
    timestamp: datetime = Field(default_factory=datetime.now)
    metadata: Dict[str, Any] = Field(default_factory=dict)
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "role": self.role,
            "content": self.content,
            "timestamp": self.timestamp.isoformat(),
            "metadata": self.metadata
        }


class AgentSession(BaseModel):
    """
    Manages conversation state for an agent session.
    
    Features:
    - Message history with rotation
    - Persistent storage to disk
    - Context window management
    - Metadata tracking
    """
    
    session_id: str
    messages: List[Message] = Field(default_factory=list)
    metadata: Dict[str, Any] = Field(default_factory=dict)
    created_at: datetime = Field(default_factory=datetime.now)
    updated_at: datetime = Field(default_factory=datetime.now)
    
    # Configuration
    max_messages: int = 50
    auto_save: bool = True
    save_dir: Path = Path("./data/sessions")
    
    model_config = ConfigDict(arbitrary_types_allowed=True)
    
    def add_message(self, role: str, content: str, **kwargs) -> None:
        """Add a message to the session."""
        message = Message(
            role=role,
            content=content,
            metadata=kwargs
        )
        self.messages.append(message)
        self.updated_at = datetime.now()
        
        # Auto-save if enabled
        if self.auto_save:
            self.save()
        
        # Rotate if exceeding max
        if len(self.messages) > self.max_messages:
            self.messages = self.messages[-self.max_messages:]
    
    def get_history(
        self,
        limit: Optional[int] = None,
        roles: Optional[List[str]] = None
    ) -> List[Dict[str, str]]:
        """
        Get conversation history.
        
        Args:
            limit: Maximum number of messages to return
            roles: Filter by roles (e.g., ["user", "assistant"])
        """
        messages = self.messages
        
        # Filter by roles
        if roles:
            messages = [m for m in messages if m.role in roles]
        
        # Limit
        if limit:
            messages = messages[-limit:]
        
        # Format for API
        return [{"role": m.role, "content": m.content} for m in messages]
    
    def save(self, path: Optional[Path] = None) -> Path:
        """Save session to disk."""
        save_path = path or self.save_dir / f"{self.session_id}.json"
        save_path.parent.mkdir(parents=True, exist_ok=True)
        
        data = {
            "session_id": self.session_id,
            "messages": [m.to_dict() for m in self.messages],
            "metadata": self.metadata,
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat()
        }
        
        with open(save_path, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        
        logger.debug(f"Session saved to {save_path}")
        return save_path
    
    def load(self, path: Optional[Path] = None) -> bool:
        """Load session from disk."""
        load_path = path or self.save_dir / f"{self.session_id}.json"
        
        if not load_path.exists():
            logger.warning(f"Session file not found: {load_path}")
            return False
        
        try:
            with open(load_path, "r", encoding="utf-8") as f:
                data = json.load(f)
            
            self.messages = [Message(**m) for m in data.get("messages", [])]
            self.metadata = data.get("metadata", {})
            self.created_at = datetime.fromisoformat(data["created_at"])
            self.updated_at = datetime.fromisoformat(data["updated_at"])
            
            logger.debug(f"Session loaded from {load_path}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to load session: {e}")
            return False
    
    def get_stats(self) -> Dict[str, Any]:
        """Get session statistics."""
        return {
            "session_id": self.session_id,
            "message_count": len(self.messages),
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat(),
            "roles": {
                "user": sum(1 for m in self.messages if m.role == "user"),
                "assistant": sum(1 for m in self.messages if m.role == "assistant"),
                "system": sum(1 for m in self.messages if m.role == "system")
            }
        }
    
    def clear(self) -> None:
        """Clear all messages."""
        self.messages.clear()
        self.updated_at = datetime.now()
        if self.auto_save:
            self.save()
    
    def __len__(self) -> int:
        return len(self.messages)
    
    def __bool__(self) -> bool:
        return len(self.messages) > 0
