"""
File System Tool - File operations for agent
"""

import asyncio
import json
import logging
import os
from pathlib import Path
from typing import Any, Dict, List, Optional

from .base import BaseTool

logger = logging.getLogger(__name__)


class FileSystemTool(BaseTool):
    """
    Tool for file system operations.
    
    Supports:
    - Read/write files
    - List directories
    - Search files
    - Copy/move files
    """
    
    name = "filesystem"
    description = """
    File system operations for reading, writing, and managing files.
    Use this tool to:
    - Read content from files
    - Write content to files
    - List directory contents
    - Search for files by pattern
    - Get file metadata
    """
    
    def __init__(self, root_dir: Path = Path("./data"), **kwargs):
        super().__init__(**kwargs)
        self.root_dir = Path(root_dir).resolve()
        self.root_dir.mkdir(parents=True, exist_ok=True)
        
        # Security: Prevent path traversal
        self._allowed_paths = [self.root_dir]
    
    async def execute(self, action: str, path: str = "", content: str = "", **kwargs) -> Any:
        """
        Execute file system operation.
        
        Args:
            action: Operation type (read, write, list, search, metadata)
            path: File/directory path
            content: Content to write (for write action)
            **kwargs: Additional parameters
        """
        # Sanitize path
        safe_path = self._sanitize_path(path)
        
        actions = {
            "read": self._read_file,
            "write": self._write_file,
            "list": self._list_directory,
            "search": self._search_files,
            "metadata": self._get_metadata
        }
        
        if action not in actions:
            raise ValueError(f"Unknown action: {action}")
        
        return await actions[action](safe_path, content, **kwargs)
    
    async def _read_file(self, path: Path, content: str = "", **kwargs) -> str:
        """Read file content."""
        if not path.exists():
            raise FileNotFoundError(f"File not found: {path}")
        
        if not path.is_file():
            raise ValueError(f"Not a file: {path}")
        
        # Read with encoding
        encoding = kwargs.get("encoding", "utf-8")
        max_chars = kwargs.get("max_chars")
        
        with open(path, "r", encoding=encoding) as f:
            text = f.read()
        
        if max_chars and len(text) > max_chars:
            text = text[:max_chars] + "\n... [truncated]"
        
        return text
    
    async def _write_file(self, path: Path, content: str = "", **kwargs) -> str:
        """Write content to file."""
        # Ensure path is within root
        try:
            path.relative_to(self.root_dir)
        except ValueError:
            raise ValueError(f"Path traversal detected: {path}")
        
        # Create parent directories
        path.parent.mkdir(parents=True, exist_ok=True)
        
        # Write with encoding
        encoding = kwargs.get("encoding", "utf-8")
        mode = kwargs.get("mode", "w")
        
        with open(path, mode, encoding=encoding) as f:
            f.write(content)
        
        return f"Written {len(content)} chars to {path}"
    
    async def _list_directory(self, path: Path, content: str = "", **kwargs) -> List[Dict[str, Any]]:
        """List directory contents."""
        if not path.exists():
            raise FileNotFoundError(f"Directory not found: {path}")
        
        if not path.is_dir():
            raise ValueError(f"Not a directory: {path}")
        
        recursive = kwargs.get("recursive", False)
        max_depth = kwargs.get("max_depth", 1)
        
        entries = []
        for item in path.iterdir():
            rel_path = item.relative_to(self.root_dir)
            stat = item.stat()
            
            entries.append({
                "path": str(rel_path),
                "name": item.name,
                "type": "directory" if item.is_dir() else "file",
                "size": stat.st_size if item.is_file() else None,
                "modified": stat.st_mtime
            })
            
            # Recurse if requested
            if recursive and item.is_dir() and max_depth > 1:
                sub_entries = await self._list_directory(
                    item, max_depth=max_depth - 1
                )
                entries.extend(sub_entries)
        
        return entries
    
    async def _search_files(self, path: Path, content: str = "", pattern: str = "*", **kwargs) -> List[str]:
        """Search files by pattern."""
        if not path.exists():
            raise FileNotFoundError(f"Directory not found: {path}")
        
        recursive = kwargs.get("recursive", True)
        
        if recursive:
            files = list(path.rglob(pattern))
        else:
            files = list(path.glob(pattern))
        
        return [str(f.relative_to(self.root_dir)) for f in files]
    
    async def _get_metadata(self, path: Path, content: str = "", **kwargs) -> Dict[str, Any]:
        """Get file/directory metadata."""
        if not path.exists():
            raise FileNotFoundError(f"Path not found: {path}")
        
        stat = path.stat()
        
        return {
            "path": str(path.relative_to(self.root_dir)),
            "name": path.name,
            "type": "directory" if path.is_dir() else "file",
            "size": stat.st_size if path.is_file() else None,
            "created": stat.st_ctime,
            "modified": stat.st_mtime,
            "accessed": stat.st_atime
        }
    
    def _sanitize_path(self, path_str: str) -> Path:
        """Sanitize and resolve path."""
        # Handle relative paths
        if not path_str.startswith("/"):
            path_str = str(self.root_dir / path_str)
        
        # Resolve and check
        path = Path(path_str).resolve()
        
        # Security check
        try:
            path.relative_to(self.root_dir)
        except ValueError:
            raise ValueError(f"Path traversal not allowed: {path}")
        
        return path
    
    def _get_input_schema(self) -> Dict[str, Any]:
        return {
            "action": {
                "type": "string",
                "enum": ["read", "write", "list", "search", "metadata"],
                "description": "Operation to perform"
            },
            "path": {
                "type": "string",
                "description": "File or directory path"
            },
            "content": {
                "type": "string",
                "description": "Content to write (for write action)"
            },
            "pattern": {
                "type": "string",
                "description": "Search pattern (for search action)"
            }
        }
    
    def _get_required_fields(self) -> List[str]:
        return ["action"]
