"""
Web Search Tool - Web search and fetch capabilities
"""

import asyncio
import json
import logging
import re
from typing import Any, Dict, List, Optional
from urllib.parse import quote

import httpx

from .base import BaseTool

logger = logging.getLogger(__name__)


class WebSearchTool(BaseTool):
    """
    Tool for web search and content fetching.
    
    Supports:
    - Web search (DuckDuckGo, Bing)
    - URL content fetching
    - Content extraction
    """
    
    name = "web_search"
    description = """
    Web search and content fetching tool.
    Use this tool to:
    - Search the web for information
    - Fetch content from URLs
    - Extract text from web pages
    """
    
    def __init__(self, max_results: int = 10, timeout: int = 30, **kwargs):
        super().__init__(**kwargs)
        self.max_results = max_results
        self.timeout = timeout
        self._client: Optional[httpx.AsyncClient] = None
    
    async def initialize(self) -> None:
        """Initialize HTTP client."""
        self._client = httpx.AsyncClient(
            timeout=self.timeout,
            headers={
                "User-Agent": "OttomanAgent/1.0 (research@bilirkesi.ai)"
            }
        )
        await super().initialize()
    
    async def close(self) -> None:
        """Close HTTP client."""
        if self._client:
            await self._client.aclose()
            self._client = None
        await super().close()
    
    async def execute(self, action: str, query: str = "", url: str = "", **kwargs) -> Any:
        """
        Execute web search or fetch.
        
        Args:
            action: Operation type ("search" or "fetch")
            query: Search query
            url: URL to fetch
        """
        actions = {
            "search": self._search,
            "fetch": self._fetch,
            "extract": self._extract
        }
        
        if action not in actions:
            raise ValueError(f"Unknown action: {action}")
        
        return await actions[action](query, url, **kwargs)
    
    async def _search(self, query: str, url: str = "", **kwargs) -> List[Dict[str, Any]]:
        """
        Search the web using DuckDuckGo.
        
        Returns list of results with title, url, snippet.
        """
        if not query:
            raise ValueError("Query is required for search")
        
        encoded_query = quote(query)
        
        # DuckDuckGo HTML API
        search_url = f"https://html.duckduckgo.com/html/?q={encoded_query}"
        
        try:
            response = await self._client.get(search_url)
            response.raise_for_status()
            
            results = self._parse_duckduckgo_results(response.text, kwargs.get("max_results", self.max_results))
            
            logger.info(f"Found {len(results)} results for '{query}'")
            return results
            
        except Exception as e:
            logger.error(f"Search failed: {e}")
            return []
    
    async def _fetch(self, query: str, url: str = "", **kwargs) -> Dict[str, Any]:
        """
        Fetch content from a URL.
        
        Returns title, content, and metadata.
        """
        if not url:
            raise ValueError("URL is required for fetch")
        
        try:
            response = await self._client.get(url)
            response.raise_for_status()
            
            # Extract title
            title_match = re.search(r"<title[^>]*>([^<]+)</title>", response.text, re.IGNORECASE)
            title = title_match.group(1).strip() if title_match else "No title"
            
            # Extract text content
            content = self._extract_text(response.text)
            
            # Truncate if too long
            max_length = kwargs.get("max_length", 10000)
            if len(content) > max_length:
                content = content[:max_length] + "...[truncated]"
            
            return {
                "url": url,
                "title": title,
                "content": content,
                "length": len(content)
            }
            
        except Exception as e:
            logger.error(f"Fetch failed: {e}")
            return {
                "url": url,
                "error": str(e)
            }
    
    async def _extract(self, query: str, url: str = "", **kwargs) -> Dict[str, Any]:
        """
        Extract structured data from URL.
        
        Returns extracted entities and content.
        """
        fetch_result = await self._fetch(query, url, **kwargs)
        
        if "error" in fetch_result:
            return fetch_result
        
        # Simple extraction (can be enhanced with NLP)
        return {
            **fetch_result,
            "entities": self._extract_entities(fetch_result.get("content", "")),
            "keywords": self._extract_keywords(fetch_result.get("content", ""))
        }
    
    def _parse_duckduckgo_results(self, html: str, limit: int = 10) -> List[Dict[str, Any]]:
        """Parse DuckDuckGo HTML results."""
        results = []
        
        # Extract result blocks
        result_pattern = r'<a rel="nofollow" href="([^"]+)"[^>]*>.*?<h2[^>]*>([^<]+)</h2>.*?<span[^>]*class="aui[^"]*"[^>]*>([^<]+)</span>'
        
        for match in re.finditer(result_pattern, html, re.DOTALL):
            url = match.group(1)
            title = match.group(2).strip()
            snippet = match.group(3).strip()
            
            if url and title:
                results.append({
                    "title": title,
                    "url": url,
                    "snippet": snippet
                })
            
            if len(results) >= limit:
                break
        
        return results
    
    def _extract_text(self, html: str) -> str:
        """Extract text content from HTML."""
        # Remove scripts and styles
        text = re.sub(r'<script[^>]*>.*?</script>', '', html, flags=re.DOTALL)
        text = re.sub(r'<style[^>]*>.*?</style>', '', text, flags=re.DOTALL)
        
        # Remove HTML tags
        text = re.sub(r'<[^>]+>', ' ', text)
        
        # Decode HTML entities
        text = re.sub(r'&(\w+);', r' \1 ', text)
        text = re.sub(r'&#(\d+);', lambda m: chr(int(m.group(1))), text)
        
        # Normalize whitespace
        text = re.sub(r'\s+', ' ', text).strip()
        
        return text
    
    def _extract_entities(self, text: str) -> List[Dict[str, str]]:
        """Simple entity extraction (can be enhanced)."""
        # Person names (capitalized words)
        persons = re.findall(r'\b[A-Z][a-z]+(?:\s+[A-Z][a-z]+)+\b', text)
        
        # Locations (after common prefixes)
        locations = re.findall(r'\b(?:in|at|from)\s+([A-Z][a-z]+(?:\s+[A-Z][a-z]+)*)\b', text)
        
        return [
            {"type": "person", "value": p} for p in persons[:10]
        ] + [
            {"type": "location", "value": l} for l in locations[:10]
        ]
    
    def _extract_keywords(self, text: str, count: int = 10) -> List[str]:
        """Extract keywords from text."""
        # Simple frequency-based extraction
        words = re.findall(r'\b[a-zçğıöşü]{4,}\b', text.lower())
        
        # Count frequency
        freq = {}
        for word in words:
            freq[word] = freq.get(word, 0) + 1
        
        # Sort by frequency
        sorted_words = sorted(freq.items(), key=lambda x: x[1], reverse=True)
        
        return [word for word, count in sorted_words[:count]]
    
    def _get_input_schema(self) -> Dict[str, Any]:
        return {
            "action": {
                "type": "string",
                "enum": ["search", "fetch", "extract"],
                "description": "Operation to perform"
            },
            "query": {
                "type": "string",
                "description": "Search query"
            },
            "url": {
                "type": "string",
                "description": "URL to fetch"
            }
        }
    
    def _get_required_fields(self) -> List[str]:
        return ["action"]
