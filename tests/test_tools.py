import pytest
from ottoman_agent_pipeline.tools.filesystem import FileSystemTool
from pathlib import Path
import tempfile
import os


@pytest.mark.asyncio
async def test_filesystem_tool():
    """Test file system tool."""
    tool = FileSystemTool()
    
    # Create temp file
    with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.txt') as f:
        f.write("Test content")
        temp_path = f.name
    
    try:
        # Test read
        content = await tool.execute("read", path=temp_path)
        assert "Test content" in content
        
        # Test write
        result = await tool.execute("write", path="test_output.txt", content="New content")
        assert "Written" in result
        
        # Test list
        entries = await tool.execute("list", path=".")
        assert isinstance(entries, list)
        
    finally:
        # Cleanup
        if os.path.exists(temp_path):
            os.unlink(temp_path)


def test_tool_schema():
    """Test tool schema generation."""
    tool = FileSystemTool()
    schema = tool.get_schema()
    
    assert schema["name"] == "filesystem"
    assert "description" in schema
    assert "input_schema" in schema
