/**
 * Electron Preload Script
 * Exposes secure API to renderer
 */

const { contextBridge, ipcRenderer } = require('electron');

contextBridge.exposeInMainWorld('ottomanAgent', {
  // File operations
  openFile: () => ipcRenderer.invoke('open-file'),
  saveFile: (filename, content) => ipcRenderer.invoke('save-file', filename, content),
  
  // Backend control
  startBackend: () => ipcRenderer.send('backend-start'),
  stopBackend: () => ipcRenderer.send('backend-stop'),
  onBackendStatus: (callback) => ipcRenderer.on('backend-status', (_, status) => callback(status)),
  onBackendOutput: (callback) => ipcRenderer.on('backend-output', (_, data) => callback(data)),
  onBackendError: (callback) => ipcRenderer.on('backend-error', (_, data) => callback(data)),
  
  // Translation
  transliterate: (text, options) => ipcRenderer.invoke('transliterate', text, options),
  
  // Agent
  chat: (message, options) => ipcRenderer.invoke('agent-chat', message, options),
  
  // Workflow
  executeWorkflow: (workflowId, input) => ipcRenderer.invoke('execute-workflow', workflowId, input),
  
  // BYOK
  createKey: (keyData) => ipcRenderer.invoke('byok-create-key', keyData),
  listKeys: (filters) => ipcRenderer.invoke('byok-list-keys', filters),
  
  // MCP
  executeTool: (toolId, params) => ipcRenderer.invoke('mcp-execute', toolId, params),
  
  // System
  getSystemInfo: () => ipcRenderer.invoke('get-system-info'),
  
  // Menu actions
  onMenuAction: (callback) => ipcRenderer.on('menu-action', (_, action) => callback(action))
});
