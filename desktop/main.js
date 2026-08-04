/**
 * Electron Main Process - Ottoman Agent Desktop App
 */

const { app, BrowserWindow, ipcMain, dialog, Menu } = require('electron');
const path = require('path');
const { spawn } = require('child_process');
const isDev = process.env.NODE_ENV === 'development';

let mainWindow;
let pythonProcess = null;

// Create the main window
function createWindow() {
  mainWindow = new BrowserWindow({
    width: 1400,
    height: 900,
    minWidth: 1024,
    minHeight: 768,
    webPreferences: {
      nodeIntegration: false,
      contextIsolation: true,
      preload: path.join(__dirname, 'preload.js')
    },
    icon: path.join(__dirname, '../resources/icon.png'),
    title: 'Ottoman Agent',
    backgroundColor: '#1a1a2e',
    frame: true,
    darkTheme: true
  });

  // Load the app
  if (isDev) {
    mainWindow.loadURL('http://localhost:3000');
    mainWindow.webContents.openDevTools();
  } else {
    mainWindow.loadFile(path.join(__dirname, '../renderer/index.html'));
  }

  // Create menu
  createMenu();

  // Handle window close
  mainWindow.on('closed', () => {
    mainWindow = null;
  });

  // Handle Python process
  mainWindow.on('close', (event) => {
    if (pythonProcess) {
      pythonProcess.kill();
    }
  });
}

// Create application menu
function createMenu() {
  const template = [
    {
      label: 'File',
      submenu: [
        {
          label: 'New Translation',
          accelerator: 'CmdOrCtrl+N',
          click: () => mainWindow.webContents.send('menu-action', 'new-translation')
        },
        {
          label: 'Open File',
          accelerator: 'CmdOrCtrl+O',
          click: () => mainWindow.webContents.send('menu-action', 'open-file')
        },
        { type: 'separator' },
        {
          label: 'Exit',
          accelerator: 'CmdOrCtrl+Q',
          click: () => app.quit()
        }
      ]
    },
    {
      label: 'Edit',
      submenu: [
        { label: 'Undo', accelerator: 'CmdOrCtrl+Z', role: 'undo' },
        { label: 'Redo', accelerator: 'CmdOrCtrl+Y', role: 'redo' },
        { type: 'separator' },
        { label: 'Cut', accelerator: 'CmdOrCtrl+X', role: 'cut' },
        { label: 'Copy', accelerator: 'CmdOrCtrl+C', role: 'copy' },
        { label: 'Paste', accelerator: 'CmdOrCtrl+V', role: 'paste' },
        { label: 'Select All', accelerator: 'CmdOrCtrl+A', role: 'selectall' }
      ]
    },
    {
      label: 'View',
      submenu: [
        { label: 'Reload', accelerator: 'CmdOrCtrl+R', click: () => mainWindow.reload() },
        { label: 'Toggle Full Screen', accelerator: 'F11', click: () => mainWindow.setFullScreen(!mainWindow.isFullScreen()) },
        { label: 'Toggle Developer Tools', accelerator: 'F12', click: () => mainWindow.webContents.toggleDevTools() }
      ]
    },
    {
      label: 'Tools',
      submenu: [
        {
          label: 'Start Backend',
          accelerator: 'CmdOrCtrl+B',
          click: () => startBackend()
        },
        {
          label: 'Stop Backend',
          accelerator: 'CmdOrCtrl+Shift+B',
          click: () => stopBackend()
        },
        { type: 'separator' },
        {
          label: 'Open API Docs',
          click: () => {
            const { shell } = require('electron');
            shell.openExternal('http://localhost:8000/docs');
          }
        }
      ]
    },
    {
      label: 'Help',
      submenu: [
        {
          label: 'About',
          click: () => {
            dialog.showMessageBox({
              type: 'info',
              title: 'About Ottoman Agent',
              message: 'Ottoman Agent v1.0.0\nOttoman Turkish Transliteration System',
              buttons: ['OK']
            });
          }
        }
      ]
    }
  ];

  const menu = Menu.buildFromTemplate(template);
  Menu.setApplicationMenu(menu);
}

// Start Python backend
function startBackend() {
  if (pythonProcess) {
    mainWindow.webContents.send('backend-status', 'running');
    return;
  }

  const pythonPath = isDev 
    ? 'python' 
    : path.join(process.resourcesPath, 'python', 'bin', 'python');
  
  const scriptPath = path.join(__dirname, '../backend/server.py');

  pythonProcess = spawn(pythonPath, [scriptPath], {
    stdio: ['pipe', 'pipe', 'pipe'],
    windowsHide: true
  });

  pythonProcess.stdout.on('data', (data) => {
    mainWindow.webContents.send('backend-output', data.toString());
  });

  pythonProcess.stderr.on('data', (data) => {
    mainWindow.webContents.send('backend-error', data.toString());
  });

  pythonProcess.on('close', (code) => {
    pythonProcess = null;
    mainWindow.webContents.send('backend-status', 'stopped');
  });

  mainWindow.webContents.send('backend-status', 'starting');
}

// Stop Python backend
function stopBackend() {
  if (pythonProcess) {
    pythonProcess.kill();
    pythonProcess = null;
    mainWindow.webContents.send('backend-status', 'stopped');
  }
}

// IPC Handlers
function setupIPC() {
  // File operations
  ipcMain.handle('open-file', async () => {
    const result = await dialog.showOpenDialog(mainWindow, {
      properties: ['openFile'],
      filters: [
        { name: 'Text Files', extensions: ['txt', 'md', 'json'] },
        { name: 'All Files', extensions: ['*'] }
      ]
    });
    return result.filePaths;
  });

  ipcMain.handle('save-file', async (event, filename, content) => {
    const result = await dialog.showSaveDialog(mainWindow, {
      defaultPath: filename
    });
    if (!result.canceled) {
      require('fs').writeFileSync(result.filePath, content);
      return result.filePath;
    }
    return null;
  });

  // Backend control
  ipcMain.on('backend-start', () => startBackend());
  ipcMain.on('backend-stop', () => stopBackend());

  // Translation
  ipcMain.handle('transliterate', async (event, text, options) => {
    try {
      const response = await fetch('http://localhost:8000/api/v1/transliterate', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ text, ...options })
      });
      return await response.json();
    } catch (error) {
      return { error: error.message };
    }
  });

  // Agent chat
  ipcMain.handle('agent-chat', async (event, message, options) => {
    try {
      const response = await fetch('http://localhost:8000/api/v1/chat', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ message, ...options })
      });
      return await response.json();
    } catch (error) {
      return { error: error.message };
    }
  });

  // Workflow execution
  ipcMain.handle('execute-workflow', async (event, workflowId, input) => {
    try {
      const response = await fetch(`http://localhost:8000/api/v1/workflows/${workflowId}/execute`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(input)
      });
      return await response.json();
    } catch (error) {
      return { error: error.message };
    }
  });

  // Key management
  ipcMain.handle('byok-create-key', async (event, keyData) => {
    try {
      const response = await fetch('http://localhost:8000/api/v1/byok/keys', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(keyData)
      });
      return await response.json();
    } catch (error) {
      return { error: error.message };
    }
  });

  ipcMain.handle('byok-list-keys', async (event, filters) => {
    try {
      const url = new URL('http://localhost:8000/api/v1/byok/keys');
      if (filters?.service) url.searchParams.set('service', filters.service);
      if (filters?.scope) url.searchParams.set('scope', filters.scope);
      if (filters?.status) url.searchParams.set('status', filters.status);
      
      const response = await fetch(url.toString());
      return await response.json();
    } catch (error) {
      return { error: error.message };
    }
  });

  // MCP Tools
  ipcMain.handle('mcp-execute', async (event, toolId, params) => {
    try {
      const response = await fetch(`http://localhost:8000/api/v1/mcp/tools/${toolId}/execute`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(params)
      });
      return await response.json();
    } catch (error) {
      return { error: error.message };
    }
  });

  // System info
  ipcMain.handle('get-system-info', () => {
    return {
      platform: process.platform,
      arch: process.arch,
      nodeVersion: process.version,
      electronVersion: process.versions.electron,
      memoryUsage: process.memoryUsage()
    };
  });
}

// App lifecycle
app.whenReady().then(() => {
  createWindow();
  setupIPC();

  app.on('activate', () => {
    if (mainWindow === null) {
      createWindow();
    }
  });
});

app.on('window-all-closed', () => {
  if (process.platform !== 'darwin') {
    app.quit();
  }
});

app.on('quit', () => {
  if (pythonProcess) {
    pythonProcess.kill();
  }
});
