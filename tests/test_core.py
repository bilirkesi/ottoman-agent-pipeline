import pytest
from ottoman_agent_pipeline import __version__
from ottoman_agent_pipeline.core.orchestrator import AgentOrchestrator
from ottoman_agent_pipeline.core.session import AgentSession


def test_package_imports():
    """Smoke test: the whole package (core, models, byok, mcp, workflow, codegraph, nlp_graph, api) must import."""
    assert __version__ == "0.1.0"


@pytest.mark.asyncio
async def test_orchestrator_init():
    """Test orchestrator initialization."""
    orch = AgentOrchestrator()
    assert orch.session_id is not None
    assert orch.session is not None
    assert orch.config is not None


@pytest.mark.asyncio
async def test_session():
    """Test session management."""
    session = AgentSession(session_id="test-session")

    # Add messages
    session.add_message("user", "Hello")
    session.add_message("assistant", "Hi there!")

    assert len(session.messages) == 2
    assert session.get_history() == [
        {"role": "user", "content": "Hello"},
        {"role": "assistant", "content": "Hi there!"}
    ]


def test_get_status():
    """Test status retrieval."""
    orch = AgentOrchestrator()
    status = orch.get_status()

    assert "session_id" in status
    assert "tools" in status
    assert "models" in status
    assert status["tools"] == []
    assert status["models"] == []


def test_config_schema():
    """Test that config schema matches orchestrator access patterns."""
    from ottoman_agent_pipeline.core.config import AgentConfig

    config = AgentConfig()

    # models.default is a string, providers is a dict
    assert isinstance(config.models.default, str)
    assert isinstance(config.models.providers, dict)

    # tools.<name>.enabled pattern
    assert config.tools.filesystem.enabled is True
    assert config.tools.translation.enabled is True

    # agent.params and sessions.max_history
    assert config.agent.params.temperature == 0.3
    assert config.sessions.max_history == 50
