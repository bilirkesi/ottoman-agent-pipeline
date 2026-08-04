# Desktop App - Implementation Guide

## Overview

The Ottoman Agent Desktop app is built with Electron and provides:
- Transliteration interface
- Agent chat
- Workflow management
- Key management (BYOK)
- History tracking

## Project Structure

```
desktop/
├── main.js          # Electron main process
├── preload.js       # Preload script
├── renderer/
│   ├── index.html   # Main UI
│   ├── styles.css   # Styles
│   └── renderer.js  # Renderer process
└── resources/       # Icons and assets
```

## Running the App

```bash
# Install dependencies
npm install

# Development mode
npm start

# Build for production
npm run build:win
```

## Features

### 1. Transliteration Tab
- Input: Ottoman Turkish text (Arap harfi)
- Mode selection: Hybrid, Neural, NLP
- Output: Modern Turkish text
- Confidence scoring
- Chunk handling for long texts

### 2. Agent Chat Tab
- Chat interface
- Message history
- Model selection
- Streaming responses

### 3. Workflows Tab
- Workflow list
- Create new workflow
- Execute workflow
- Template selection

### 4. API Keys Tab
- Key list
- Create new key
- Rotate key
- Revoke key
- Audit logs

### 5. Tools Tab
- Tool list
- Execute tool
- Tool stats
- Tool history

### 6. History Tab
- Execution history
- Search and filter
- Export results

## Backend Communication

The desktop app communicates with the backend API at `http://localhost:8000`.

### API Endpoints Used

```javascript
// Health check
fetch('http://localhost:8000/health')

// Transliterate
fetch('http://localhost:8000/api/v1/transliterate', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({ text, mode })
})

// Chat
fetch('http://localhost:8000/api/v1/chat', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({ message })
})

// BYOK keys
fetch('http://localhost:8000/api/v1/byok/keys', {
  method: 'GET'
})

// MCP tools
fetch('http://localhost:8000/api/v1/mcp/tools', {
  method: 'GET'
})

// Workflows
fetch('http://localhost:8000/api/v1/workflows/', {
  method: 'GET'
})
```

## Building for Production

### Windows
```bash
npm run build:win
# Output: dist/Ottoman-Agent-0.1.0-setup.exe
```

### macOS
```bash
npm run build:mac
# Output: dist/Ottoman Agent 0.1.0.dmg
```

### Linux
```bash
npm run build:linux
# Output: dist/Ottoman-Agent-0.1.0.AppImage
```

## Troubleshooting

### Cache Issues
If you see cache errors, run with:
```bash
npx electron . --disable-gpu
```

### Port Already in Use
If port 8000 is already in use:
1. Kill the process: `taskkill /F /PID <pid>`
2. Or change the backend port in `backend/server.py`

### Dependencies Missing
```bash
npm install
pip install -e .
```

## References

- [Electron Documentation](https://www.electronjs.org/docs)
- [Electron Builder](https://www.electron.build/)
- [FastAPI Documentation](https://fastapi.tiangolo.com/)
