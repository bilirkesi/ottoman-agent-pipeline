import tempfile
from pathlib import Path

import pytest

from ottoman_agent_pipeline.tools.filesystem import FileSystemTool


@pytest.mark.asyncio
async def test_filesystem_tool():
    """Test file system tool."""
    with tempfile.TemporaryDirectory() as tmpdir:
        tool = FileSystemTool(root_dir=Path(tmpdir))

        # Test write
        result = await tool.execute(
            "write", path="test_output.txt", content="New content"
        )
        assert "Written" in result

        # Test read
        content = await tool.execute("read", path="test_output.txt")
        assert "New content" in content

        # Test list
        entries = await tool.execute("list", path=".")
        assert isinstance(entries, list)
        assert len(entries) == 1
        assert entries[0]["name"] == "test_output.txt"


def test_tool_schema():
    """Test tool schema generation."""
    tool = FileSystemTool()
    schema = tool.get_schema()

    assert schema["name"] == "filesystem"
    assert "description" in schema
    assert "input_schema" in schema
