"""
Configuration management
"""

import os
import yaml
from pathlib import Path
from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field


class ModelConfig(BaseModel):
    """Model provider configuration."""
    
    api_key: Optional[str] = None
    base_url: Optional[str] = None
    models: List[Dict[str, Any]] = Field(default_factory=list)
    
    def model_post_init(self, __context):
        """Post-init hook to load env vars."""
        if not self.api_key:
            self.api_key = os.environ.get(f"{self.__class__.__name__.upper()}_API_KEY")
        
        if not self.base_url:
            self.base_url = os.environ.get(f"{self.__class__.__name__.upper()}_BASE_URL")


class AgentConfig(BaseModel):
    """Agent configuration."""
    
    name: str = "osmanlica-agent"
    version: str = "0.1.0"
    
    models: Dict[str, ModelConfig] = Field(default_factory=dict)
    default_model: str = "deepseek-v4-flash"
    
    tools: Dict[str, Any] = Field(default_factory=dict)
    
    sessions: Dict[str, Any] = Field(default_factory=lambda: {
        "max_history": 50,
        "auto_save": True,
        "save_dir": "./data/sessions"
    })
    
    agent: Dict[str, Any] = Field(default_factory=lambda: {
        "params": {
            "temperature": 0.3,
            "max_tokens": 4000
        }
    })


class ConfigManager:
    """
    Manages configuration loading and validation.
    """
    
    DEFAULT_CONFIG_PATH = Path("~/.ottoman-agent/config.yaml").expanduser()
    
    def __init__(self, config_path: Optional[Path] = None):
        self.config_path = config_path or self.DEFAULT_CONFIG_PATH
        self._config: Optional[AgentConfig] = None
    
    def load(self) -> AgentConfig:
        """Load configuration from file."""
        if self._config is not None:
            return self._config
        
        if not self.config_path.exists():
            # Create default config
            self._create_default_config()
        
        with open(self.config_path, "r", encoding="utf-8") as f:
            data = yaml.safe_load(f)
        
        self._config = AgentConfig(**data)
        return self._config
    
    def save(self, config: AgentConfig) -> None:
        """Save configuration to file."""
        self.config_path.parent.mkdir(parents=True, exist_ok=True)
        
        with open(self.config_path, "w", encoding="utf-8") as f:
            yaml.dump(config.dict(), f, default_flow_style=False, allow_unicode=True)
        
        self._config = config
    
    def _create_default_config(self) -> None:
        """Create default configuration file."""
        default_config = AgentConfig()
        self.save(default_config)
    
    def get(self) -> AgentConfig:
        """Get current configuration."""
        if self._config is None:
            return self.load()
        return self._config


# Global config instance
_config_manager = ConfigManager()


def get_config() -> AgentConfig:
    """Get global configuration."""
    return _config_manager.get()


def load_config(path: Optional[Path] = None) -> AgentConfig:
    """Load configuration from path."""
    manager = ConfigManager(path)
    return manager.load()
