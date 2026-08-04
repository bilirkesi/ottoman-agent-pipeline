"""
Configuration management

AgentConfig şeması, AgentOrchestrator'ın kullandığı erişim desenleriyle
birebir eşleşecek şekilde modellenmiştir:

- config.models.default           -> varsayılan model adı
- config.models.providers[<ad>]   -> provider ayarları (api_key, base_url, models)
- config.tools.<ad>.enabled       -> tool aç/kapa
- config.agent.params             -> model çağrı parametreleri
- config.sessions.max_history     -> oturum geçmişi sınırı
"""

import os
import yaml
from pathlib import Path
from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field


class ModelConfig(BaseModel):
    """Model provider configuration."""

    name: str = ""
    api_key: Optional[str] = None
    base_url: Optional[str] = None
    models: List[Dict[str, Any]] = Field(default_factory=list)

    def model_post_init(self, __context):
        """Post-init hook to load env vars (ör. DEEPSEEK_API_KEY)."""
        if not self.api_key and self.name:
            self.api_key = os.environ.get(f"{self.name.upper()}_API_KEY")
        if not self.base_url and self.name:
            self.base_url = os.environ.get(f"{self.name.upper()}_BASE_URL")


class ModelsConfig(BaseModel):
    """Model sağlayıcı haritası."""

    default: str = "deepseek-v4-flash"
    providers: Dict[str, ModelConfig] = Field(default_factory=dict)


class FileSystemToolConfig(BaseModel):
    enabled: bool = True
    root_dir: str = "./data"


class WebSearchToolConfig(BaseModel):
    enabled: bool = True
    max_results: int = 5


class TranslationToolConfig(BaseModel):
    enabled: bool = True
    pipeline: str = "hybrid"


class NERToolConfig(BaseModel):
    enabled: bool = True
    model: str = "bert-base-turkish"


class ToolsConfig(BaseModel):
    """Tool yapılandırması."""

    filesystem: FileSystemToolConfig = Field(default_factory=FileSystemToolConfig)
    web_search: WebSearchToolConfig = Field(default_factory=WebSearchToolConfig)
    translation: TranslationToolConfig = Field(default_factory=TranslationToolConfig)
    ner: NERToolConfig = Field(default_factory=NERToolConfig)


class AgentParams(BaseModel):
    """Model çağrı parametreleri (chat'e **params olarak iletilir)."""

    temperature: float = 0.3
    max_tokens: int = 4000


class AgentSection(BaseModel):
    """Agent kimlik ve davranış ayarları."""

    name: str = "osmanlica-agent"
    version: str = "0.1.0"
    team: Dict[str, Any] = Field(default_factory=dict)
    params: AgentParams = Field(default_factory=AgentParams)


class SessionsConfig(BaseModel):
    """Oturum yönetimi ayarları."""

    max_history: int = 50
    auto_save: bool = True
    save_dir: str = "./data/sessions"


class AgentConfig(BaseModel):
    """Agent configuration."""

    name: str = "osmanlica-agent"
    version: str = "0.1.0"

    agent: AgentSection = Field(default_factory=AgentSection)
    models: ModelsConfig = Field(default_factory=ModelsConfig)
    tools: ToolsConfig = Field(default_factory=ToolsConfig)
    sessions: SessionsConfig = Field(default_factory=SessionsConfig)


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
            data = yaml.safe_load(f) or {}

        self._config = AgentConfig(**data)
        return self._config

    def save(self, config: AgentConfig) -> None:
        """Save configuration to file."""
        self.config_path.parent.mkdir(parents=True, exist_ok=True)

        with open(self.config_path, "w", encoding="utf-8") as f:
            yaml.dump(config.model_dump(), f, default_flow_style=False, allow_unicode=True)

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
