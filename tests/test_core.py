import pytest
from ottoman_agent_pipeline.core.orchestrator import AgentOrchestrator
from ottoman_agent_pipeline.core.session import AgentSession


@pytest.mark.asyncio
async def test_orchestrator_init():
    """Test orchestrator initialization."""
    orch = AgentOrchestrator()
    assert orch.session_id is not None
    assert orch.session is not None


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
        {"role": "assistant", "content": "Transliterate this: Hello"}
    ]


def test_get_status():
    """Test status retrieval."""
    orch = AgentOrchestrator()
    status = orch.get_status()
    
    assert "session_id" in status
    assert "tools" in status
    assert "models" in status
