# Agent Team - Implementation Guide

## Overview

The Ottoman Agent Pipeline includes a team of 5 specialized agents that work together to:
1. **CodeAgent** - Implement and refactor code
2. **TestAgent** - Write and run tests
3. **DeployAgent** - Manage CI/CD and releases
4. **ResearchAgent** - Conduct research and analysis
5. **DocsAgent** - Generate documentation

## Agent Implementation

### CodeAgent

```python
class CodeAgent:
    """
    Kod yazma, refactoring, linting agent'ı.
    
    Özellikler:
    - Kod implementasyonu
    - Refactoring
    - Code review
    - Linting
    """
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.tools = {
            "write_file": self._write_file,
            "edit_file": self._write_file,
            "lint_code": self._lint_code,
            "refactor": self._refactor
        }
    
    async def implement(self, name: str, path: str, content: str) -> Dict:
        """Kod implement et"""
        # 1. Write file
        await self._write_file(path, content)
        
        # 2. Lint code
        lint_result = await self._lint_code(path)
        
        # 3. Review and fix
        if lint_result["errors"]:
            await self._fix_issues(path, lint_result["errors"])
        
        return {
            "status": "success",
            "path": path,
            "lint_errors": len(lint_result["errors"]),
            "lint_warnings": len(lint_result["warnings"])
        }
    
    async def _lint_code(self, path: str) -> Dict:
        """Code linting"""
        # Use ruff, pylint, or mypy
        import subprocess
        result = subprocess.run(
            ["ruff", "check", path],
            capture_output=True,
            text=True
        )
        return {
            "errors": self._parse_output(result.stdout),
            "warnings": []
        }
```

### TestAgent

```python
class TestAgent:
    """
    Test yazma ve çalıştırma agent'ı.
    
    Özellikler:
    - Unit test yazma
    - Integration test
    - Coverage raporlama
    - Benchmark
    """
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.tools = {
            "write_test": self._write_test,
            "run_tests": self._run_tests,
            "benchmark": self._benchmark
        }
    
    async def test(self, path: str, test_path: str) -> Dict:
        """Test çalıştır"""
        # 1. Run tests
        result = await self._run_tests(test_path)
        
        # 2. Check coverage
        coverage = await self._get_coverage(path)
        
        # 3. Report
        return {
            "passed": result["passed"],
            "failed": result["failed"],
            "coverage": coverage["percent"],
            "status": "pass" if result["failed"] == 0 and coverage["percent"] >= 90 else "fail"
        }
    
    async def _run_tests(self, path: str) -> Dict:
        """Test çalıştır"""
        import pytest
        result = pytest.main([path, "-v", "--tb=short"])
        return {
            "passed": result.get("passed", 0),
            "failed": result.get("failed", 0)
        }
```

### DeployAgent

```python
class DeployAgent:
    """
    Deployment ve CI/CD agent'ı.
    
    Özellikler:
    - Package build
    - PyPI publish
    - GitHub release
    - Docker deploy
    """
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.tools = {
            "build_package": self._build_package,
            "publish_pypi": self._publish_pypi,
            "create_release": self._create_release
        }
    
    async def deploy(self, version: str) -> Dict:
        """Deploy et"""
        # 1. Build package
        await self._build_package(version)
        
        # 2. Publish to PyPI
        await self._publish_pypi(version)
        
        # 3. Create GitHub release
        await self._create_release(version)
        
        return {
            "status": "success",
            "version": version,
            "published_at": datetime.now().isoformat()
        }
```

### ResearchAgent

```python
class ResearchAgent:
    """
    Araştırma ve analiz agent'ı.
    
    Özellikler:
    - Web search
    - Paper reading
    - Benchmark analysis
    - Model comparison
    """
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.tools = {
            "web_search": self._web_search,
            "read_paper": self._read_paper,
            "analyze_benchmark": self._analyze_benchmark
        }
    
    async def research(self, topic: str) -> Dict:
        """Araştırma yap"""
        # 1. Web search
        search_results = await self._web_search(topic)
        
        # 2. Read relevant papers
        papers = await self._read_paper(search_results)
        
        # 3. Analyze benchmarks
        analysis = await self._analyze_benchmark(papers)
        
        return {
            "topic": topic,
            "results": search_results,
            "papers": papers,
            "analysis": analysis
        }
```

### DocsAgent

```python
class DocsAgent:
    """
    Dokümantasyon agent'ı.
    
    Özellikler:
    - README yazma
    - API docs
    - Tutorial generation
    """
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.tools = {
            "write_readme": self._write_readme,
            "api_docs": self._api_docs,
            "generate_tutorial": self._generate_tutorial
        }
    
    async def document(self, project_path: str) -> Dict:
        """Dokümantasyon oluştur"""
        # 1. Generate README
        await self._write_readme(project_path)
        
        # 2. Generate API docs
        await self._api_docs(project_path)
        
        # 3. Generate tutorial
        await self._generate_tutorial(project_path)
        
        return {
            "status": "success",
            "docs_generated": ["README.md", "API.md", "TUTORIAL.md"]
        }
```

## Integration with Orchestrator

```python
class AgentTeam:
    """Agent takımı koordinatorü"""
    
    def __init__(self):
        self.agents = {
            "code": CodeAgent({...}),
            "test": TestAgent({...}),
            "deploy": DeployAgent({...}),
            "research": ResearchAgent({...}),
            "docs": DocsAgent({...})
        }
        self.bus = AgentBus()
    
    async def implement(self, name: str, path: str) -> Dict:
        """Kod implement et"""
        # CodeAgent implements
        code_result = await self.agents["code"].implement(name, path)
        
        # TestAgent tests
        test_result = await self.agents["test"].test(path)
        
        # DocsAgent documents
        docs_result = await self.agents["docs"].document(path)
        
        return {
            "code": code_result,
            "tests": test_result,
            "docs": docs_result
        }
```

## Usage Examples

### Example 1: Implement New Feature
```python
from ottoman_agent_pipeline.agents import AgentTeam

team = AgentTeam()

result = await team.implement(
    name="new_transliteration_method",
    path="src/ottoman_transliterator/pipeline.py"
)

print(f"Status: {result['status']}")
print(f"Tests passed: {result['tests']['passed']}")
print(f"Coverage: {result['tests']['coverage']}%")
```

### Example 2: Deploy New Version
```python
result = await team.deploy(version="0.2.0")

print(f"Version: {result['version']}")
print(f"Published: {result['published_at']}")
```

### Example 3: Research Topic
```python
result = await team.research(topic="Ottoman Turkish NLP 2026")

print(f"Search results: {len(result['results'])}")
print(f"Papers found: {len(result['papers'])}")
```

## Error Handling

```python
class AgentError(Exception):
    """Agent error base class"""
    pass

class CodeError(AgentError):
    """Code agent error"""
    pass

class TestError(AgentError):
    """Test agent error"""
    pass

class DeployError(AgentError):
    """Deploy agent error"""
    pass
```

## Testing

```python
import pytest
from ottoman_agent_pipeline.agents import AgentTeam

@pytest.mark.asyncio
async def test_agent_team():
    team = AgentTeam()
    
    # Test implement
    result = await team.implement("test", "test.py")
    assert result["status"] == "success"
    assert result["tests"]["passed"] > 0

@pytest.mark.asyncio
async def test_deploy():
    team = AgentTeam()
    result = await team.deploy("0.1.0")
    assert result["status"] == "success"
```

## References

- [Agent Patterns](https://microsoft.github.io/autogen/stable/reference/python/autogen.agentchat.contrib.agent_builder.html)
- [LangChain Agents](https://python.langchain.com/docs/modules/agents/)
- [AutoGPT](https://github.com/Significant-Gravitas/AutoGPT)
