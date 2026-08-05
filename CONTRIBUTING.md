# Contributing to Ottoman Agent Pipeline

Thank you for your interest in contributing! This document provides guidelines for contributing.

## 🚀 Quick Start

```bash
# Clone repository
git clone https://github.com/bilirkesi/ottoman-agent-pipeline.git
cd ottoman-agent-pipeline

# Install dependencies
pip install -e ".[dev]"
npm install --prefix desktop
npm install --prefix mobile

# Run tests
pytest tests/ -v

# Start backend
python backend/server.py

# Start desktop app
cd desktop && npm start
```

## 📋 Code Style

### Python
- Use **Black** for formatting
- Use **Ruff** for linting
- Use **basedpyright** for type checking
- Follow **PEP 8** guidelines

```bash
# Format code
black src/ tests/

# Lint code
ruff check src/ tests/

# Type check
basedpyright src/
```

### JavaScript/TypeScript
- Use **ESLint** for linting
- Use **Prettier** for formatting
- Follow **Airbnb** style guide

```bash
# Format code
npm run prettier:write --prefix desktop

# Lint code
npm run lint --prefix desktop
```

## 🧪 Testing

### Run All Tests
```bash
pytest tests/ -v
```

### Run Specific Test
```bash
pytest tests/test_core.py -v
pytest tests/test_tools.py -v
```

### Run with Coverage
```bash
pytest tests/ --cov=ottoman_agent_pipeline --cov-report=html
```

## 📝 Commit Guidelines

Follow **Conventional Commits**:
```
feat: Add new feature
fix: Fix bug
docs: Update documentation
style: Format code
refactor: Refactor code
test: Add tests
chore: Update dependencies
```

### Examples
```bash
git commit -m "feat: Add transliteration streaming support"
git commit -m "fix: Resolve CORS issue in API server"
git commit -m "docs: Update README with new API endpoints"
```

## 🔄 Pull Request Process

1. Fork the repository
2. Create a feature branch (`git checkout -b feat/amazing-feature`)
3. Make your changes
4. Run tests (`pytest tests/ -v`)
5. Commit your changes (`git commit -m 'feat: Add amazing feature'`)
6. Push to the branch (`git push origin feat/amazing-feature`)
7. Open a Pull Request

## 📚 Documentation

### Update README
- Add new features
- Update usage examples
- Keep it up-to-date

### API Documentation
- Update OpenAPI spec
- Add new endpoints to docs
- Include examples

### Agent Team Guide
- Document new agents
- Add usage examples
- Include error handling

## 🔐 Security

- Never commit API keys or secrets
- Use environment variables for sensitive data
- Follow OWASP guidelines
- Report vulnerabilities responsibly

## 🐛 Bug Reports

When filing a bug report, please include:
- OS and Python version
- Steps to reproduce
- Expected vs actual behavior
- Error messages/logs
- Minimal code example

## 💡 Feature Requests

When requesting a feature, please include:
- Problem description
- Proposed solution
- Use cases
- Alternatives considered

## 📊 Project Structure

```
ottoman-agent-pipeline/
├── src/ottoman_agent_pipeline/
│   ├── __init__.py
│   ├── agents/           # Agent team
│   ├── core/             # Core components
│   ├── tools/            # MCP tools
│   ├── models/           # Model providers
│   ├── byok/             # Key management
│   ├── mcp/              # Tool registry
│   ├── workflow/         # Workflow engine
│   ├── codegraph.py      # Code intelligence
│   ├── nlp_graph.py      # NLP graph
│   ├── cli.py            # CLI interface
│   └── api/              # REST API
├── desktop/              # Electron app
├── mobile/               # React Native app
├── docs/                 # Documentation
├── okf/                  # OKF documentation
├── tests/                # Tests
└── config/               # Configuration
```

## 🎯 Goals

1. **Research** → Benchmark models
2. **Implementation** → Write clean code
3. **Testing** → Ensure quality
4. **Documentation** → Help users
5. **Community** → Build ecosystem

## 📞 Contact

- GitHub Issues: https://github.com/bilirkesi/ottoman-agent-pipeline/issues
- Email: selahattin.taspinar@bdh.com.tr
- Website: https://github.com/bilirkesi

---

Thank you for contributing! 🎉
