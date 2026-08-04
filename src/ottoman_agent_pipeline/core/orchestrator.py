"""
Agent Orchestrator - Core pipeline orchestration
"""

import asyncio
import json
import logging
from datetime import datetime
from pathlib import Path
from typing import Any, AsyncGenerator, Dict, List, Optional, Union

from pydantic import BaseModel, Field

from .config import AgentConfig
from .session import AgentSession
from .tools.base import BaseTool
from .models.base import BaseModel as ModelProvider
from .prompts.system import SystemPromptBuilder

logger = logging.getLogger(__name__)


class AgentResponse(BaseModel):
    """Response from the agent pipeline."""
    
    success: bool = True
    output: str = ""
    tool_calls: List[Dict[str, Any]] = Field(default_factory=list)
    model_used: str = ""
    tokens_used: int = 0
    latency_ms: float = 0.0
    error: Optional[str] = None
    metadata: Dict[str, Any] = Field(default_factory=dict)
    
    def to_dict(self) -> Dict[str, Any]:
        return self.model_dump()
    
    def to_json(self) -> str:
        return json.dumps(self.to_dict(), ensure_ascii=False, indent=2)


class AgentOrchestrator:
    """
    Main orchestrator for the Ottoman Turkish transliteration agent pipeline.
    
    Handles:
    - Session management
    - Tool execution
    - Model selection and fallback
    - Pipeline state tracking
    - Error handling and recovery
    """
    
    def __init__(
        self,
        config: Optional[AgentConfig] = None,
        session_id: Optional[str] = None
    ):
        self.config = config or AgentConfig()
        self.session_id = session_id or datetime.now().strftime("%Y%m%d_%H%M%S")
        self.session = AgentSession(session_id=self.session_id)
        self.tools: Dict[str, BaseTool] = {}
        self.models: Dict[str, ModelProvider] = {}
        self._prompt_builder = SystemPromptBuilder()
        
        logger.info(f"Agent orchestrator initialized: {self.session_id}")
    
    async def initialize(self) -> None:
        """Initialize tools and models."""
        logger.info("Initializing agent pipeline...")
        
        # Initialize tools
        await self._initialize_tools()
        
        # Initialize models
        await self._initialize_models()
        
        logger.info(f"Agent initialized with {len(self.tools)} tools and {len(self.models)} models")
    
    async def _initialize_tools(self) -> None:
        """Initialize all configured tools."""
        from .tools.filesystem import FileSystemTool
        from .tools.web import WebSearchTool
        from .tools.translation import TranslationTool
        from .tools.ner import NERTool
        
        tool_configs = self.config.tools
        
        # File system tool
        if tool_configs.filesystem.enabled:
            self.tools["filesystem"] = FileSystemTool(
                root_dir=Path(tool_configs.filesystem.root_dir)
            )
        
        # Web search tool
        if tool_configs.web_search.enabled:
            self.tools["web_search"] = WebSearchTool(
                max_results=tool_configs.web_search.max_results
            )
        
        # Translation tool
        if tool_configs.translation.enabled:
            self.tools["translation"] = TranslationTool(
                pipeline=tool_configs.translation.pipeline
            )
        
        # NER tool
        if tool_configs.ner.enabled:
            self.tools["ner"] = NERTool(
                model=tool_configs.ner.model
            )
        
        logger.info(f"Initialized {len(self.tools)} tools")
    
    async def _initialize_models(self) -> None:
        """Initialize all configured model providers."""
        from .models.deepseek import DeepSeekModel
        from .models.gateway import GatewayModel
        from .models.reasonix import ReasonixModel
        
        model_configs = self.config.models
        
        # DeepSeek models
        if "deepseek" in model_configs.providers:
            deepseek_config = model_configs.providers["deepseek"]
            self.models["deepseek"] = DeepSeekModel(
                api_key=deepseek_config.api_key,
                base_url=deepseek_config.base_url,
                models=deepseek_config.models
            )
        
        # Gateway models
        if "gateway" in model_configs.providers:
            gateway_config = model_configs.providers["gateway"]
            self.models["gateway"] = GatewayModel(
                url=gateway_config.url,
                api_key=gateway_config.api_key
            )
        
        # Reasonix models (optional)
        if "reasonix" in model_configs.providers:
            reasonix_config = model_configs.providers["reasonix"]
            self.models["reasonix"] = ReasonixModel(
                api_key=reasonix_config.api_key,
                base_url=reasonix_config.base_url
            )
        
        logger.info(f"Initialized {len(self.models)} model providers")
    
    async def chat(
        self,
        message: str,
        model: Optional[str] = None,
        stream: bool = False,
        **kwargs
    ) -> Union[AgentResponse, AsyncGenerator[Dict[str, Any], None]]:
        """
        Process a chat message through the agent pipeline.
        
        Args:
            message: User input message
            model: Model to use (optional, uses default if not specified)
            stream: Whether to stream the response
            **kwargs: Additional parameters
            
        Returns:
            AgentResponse or async generator for streaming
        """
        start_time = datetime.now()
        
        try:
            # Get active model
            active_model = model or self.config.models.default
            model_provider = self._get_model(active_model)
            
            # Build messages
            messages = self._build_messages(message)
            
            # Add system prompt
            system_prompt = self._prompt_builder.build(
                tools=list(self.tools.keys()),
                models=list(self.models.keys())
            )
            messages.insert(0, {"role": "system", "content": system_prompt})
            
            # Execute pipeline
            if stream:
                return self._stream_response(model_provider, messages, **kwargs)
            else:
                return await self._process_message(
                    model_provider=model_provider,
                    messages=messages,
                    start_time=start_time
                )
                
        except Exception as e:
            logger.error(f"Agent error: {e}", exc_info=True)
            return AgentResponse(
                success=False,
                error=str(e),
                model_used=model or self.config.models.default,
                latency_ms=(datetime.now() - start_time).total_seconds() * 1000
            )
    
    async def _process_message(
        self,
        model_provider: ModelProvider,
        messages: List[Dict[str, str]],
        start_time: datetime
    ) -> AgentResponse:
        """Process a single message through the model."""
        try:
            # Call model
            response = await model_provider.chat(messages, **self.config.agent.params)
            
            # Extract content
            output = response.get("content", "")
            tool_calls = response.get("tool_calls", [])
            tokens = response.get("usage", {}).get("total_tokens", 0)
            
            # Execute tool calls if any
            if tool_calls:
                output = await self._execute_tool_calls(tool_calls, output)
            
            # Save to session
            self.session.add_message("user", messages[-1]["content"])
            self.session.add_message("assistant", output)
            
            # Build response
            latency_ms = (datetime.now() - start_time).total_seconds() * 1000
            
            return AgentResponse(
                success=True,
                output=output,
                tool_calls=tool_calls,
                model_used=model_provider.name,
                tokens_used=tokens,
                latency_ms=latency_ms
            )
            
        except Exception as e:
            logger.error(f"Model error: {e}", exc_info=True)
            
            # Try fallback model
            fallback_model = self._get_fallback_model(model_provider.name)
            if fallback_model:
                logger.info(f"Attempting fallback to {fallback_model.name}")
                return await self._process_message(fallback_model, messages, start_time)
            
            raise
    
    async def _stream_response(
        self,
        model_provider: ModelProvider,
        messages: List[Dict[str, str]],
        **kwargs
    ) -> AsyncGenerator[Dict[str, Any], None]:
        """Stream response from model."""
        async for chunk in model_provider.chat_stream(messages, **kwargs):
            yield chunk
    
    async def _execute_tool_calls(
        self,
        tool_calls: List[Dict[str, Any]],
        current_output: str
    ) -> str:
        """Execute tool calls and update output."""
        for tool_call in tool_calls:
            tool_name = tool_call.get("name")
            tool_input = tool_call.get("input", {})
            
            if tool_name in self.tools:
                try:
                    result = await self.tools[tool_name].execute(**tool_input)
                    current_output += f"\n\n[Tool: {tool_name}]\n{result}"
                except Exception as e:
                    logger.error(f"Tool {tool_name} error: {e}")
                    current_output += f"\n\n[Tool: {tool_name} failed: {e}]"
        
        return current_output
    
    def _build_messages(self, message: str) -> List[Dict[str, str]]:
        """Build message list with history."""
        messages = []
        
        # Add history (last N messages)
        history = self.session.get_history(
            limit=self.config.sessions.max_history
        )
        messages.extend(history)
        
        # Add current message
        messages.append({"role": "user", "content": message})
        
        return messages
    
    def _get_model(self, model_name: str) -> ModelProvider:
        """Get model provider by name."""
        # Try direct match
        if model_name in self.models:
            return self.models[model_name]
        
        # Try prefix match (e.g., "deepseek/deepseek-v4-flash" -> "deepseek")
        for key, model in self.models.items():
            if model_name.startswith(key + "/"):
                return model
        
        # Return default
        default_model = self.config.models.default
        if default_model in self.models:
            return self.models[default_model]
        
        # Return first available
        if self.models:
            return next(iter(self.models.values()))
        
        raise ValueError(f"No models available. Checked: {model_name}")
    
    def _get_fallback_model(self, current_model_name: str) -> Optional[ModelProvider]:
        """Get fallback model if current fails."""
        models = list(self.models.values())
        
        for i, model in enumerate(models):
            if model.name != current_model_name:
                return model
        
        return None
    
    async def translate(
        self,
        text: str,
        mode: str = "hybrid",
        model: Optional[str] = None
    ) -> AgentResponse:
        """
        Direct transliteration endpoint.
        
        Args:
            text: Ottoman Turkish text
            mode: Transliteration mode (hybrid/neural/nlp)
            model: Model to use
        """
        return await self.chat(
            message=f"Transliterate this Ottoman Turkish text to Modern Turkish: {text}",
            model=model,
            mode=mode
        )
    
    async def analyze(
        self,
        text: str,
        entities: bool = True,
        pos: bool = True
    ) -> AgentResponse:
        """
        Analyze text with NER and POS tagging.
        
        Args:
            text: Input text
            entities: Whether to extract named entities
            pos: Whether to add POS tags
        """
        prompt = f"Analyze this Ottoman Turkish text:"
        if entities:
            prompt += "\n- Extract named entities (persons, locations, organizations)"
        if pos:
            prompt += "\n- Add part-of-speech tags"
        prompt += f"\n\n{text}"
        
        return await self.chat(message=prompt)
    
    def get_session(self) -> AgentSession:
        """Get current session."""
        return self.session
    
    def get_status(self) -> Dict[str, Any]:
        """Get agent status."""
        return {
            "session_id": self.session_id,
            "tools": list(self.tools.keys()),
            "models": list(self.models.keys()),
            "session_messages": len(self.session.messages),
            "config": self.config.dict()
        }
    
    def reset_session(self) -> None:
        """Reset current session."""
        self.session = AgentSession(session_id=self.session_id)
        logger.info("Session reset")
    
    async def close(self) -> None:
        """Cleanup resources."""
        for tool in self.tools.values():
            if hasattr(tool, "close"):
                await tool.close()
        
        for model in self.models.values():
            if hasattr(model, "close"):
                await model.close()
        
        logger.info("Agent closed")
