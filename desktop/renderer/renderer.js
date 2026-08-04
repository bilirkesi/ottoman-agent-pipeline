/**
 * Ottoman Agent - Renderer Process
 */

// Tab navigation
document.querySelectorAll('.nav-item').forEach(item => {
  item.addEventListener('click', () => {
    // Update active tab
    document.querySelectorAll('.nav-item').forEach(i => i.classList.remove('active'));
    item.classList.add('active');
    
    // Show corresponding content
    const tab = item.dataset.tab;
    document.querySelectorAll('.tab-content').forEach(content => {
      content.classList.remove('active');
    });
    document.getElementById(`tab-${tab}`).classList.add('active');
    
    // Load data for tab
    if (tab === 'keys') loadKeys();
    if (tab === 'tools') loadTools();
    if (tab === 'workflows') loadWorkflows();
    if (tab === 'history') loadHistory();
  });
});

// Backend control
const btnStartBackend = document.getElementById('btn-start-backend');
const btnStopBackend = document.getElementById('btn-stop-backend');
const statusIndicator = document.getElementById('backend-status');

btnStartBackend.addEventListener('click', () => {
  window.ottomanAgent.startBackend();
  btnStartBackend.disabled = true;
  btnStopBackend.disabled = false;
});

btnStopBackend.addEventListener('click', () => {
  window.ottomanAgent.stopBackend();
  btnStartBackend.disabled = false;
  btnStopBackend.disabled = true;
});

window.ottomanAgent.onBackendStatus((status) => {
  const dot = statusIndicator.querySelector('.status-dot');
  const text = statusIndicator.querySelector('.status-text');
  
  if (status === 'running') {
    dot.classList.add('running');
    text.textContent = 'Backend: Running';
    btnStartBackend.disabled = true;
    btnStopBackend.disabled = false;
  } else {
    dot.classList.remove('running');
    text.textContent = 'Backend: Stopped';
    btnStartBackend.disabled = false;
    btnStopBackend.disabled = true;
  }
});

window.ottomanAgent.onBackendOutput((data) => {
  console.log('Backend output:', data);
});

window.ottomanAgent.onBackendError((data) => {
  console.error('Backend error:', data);
});

// Transliteration
const btnTransliterate = document.getElementById('btn-transliterate');
const ottomanInput = document.getElementById('ottoman-input');
const outputBox = document.getElementById('transliteration-output');
const metricsBox = document.getElementById('transliteration-metrics');

btnTransliterate.addEventListener('click', async () => {
  const text = ottomanInput.value.trim();
  if (!text) {
    outputBox.textContent = 'Please enter Ottoman Turkish text';
    return;
  }
  
  const mode = document.querySelector('input[name="mode"]:checked').value;
  
  outputBox.textContent = 'Transliterating...';
  metricsBox.textContent = '';
  
  try {
    const result = await window.ottomanAgent.transliterate(text, { mode });
    
    if (result.error) {
      outputBox.textContent = `Error: ${result.error}`;
    } else {
      outputBox.textContent = result.modern_turkish || result.output || JSON.stringify(result, null, 2);
      metricsBox.innerHTML = `
        <strong>Confidence:</strong> ${(result.confidence * 100).toFixed(1)}% | 
        <strong>Method:</strong> ${result.method || mode} | 
        <strong>Chunks:</strong> ${result.chunks || 1}
      `;
    }
  } catch (error) {
    outputBox.textContent = `Error: ${error.message}`;
  }
});

// Chat
const chatInput = document.getElementById('chat-input');
const chatMessages = document.getElementById('chat-messages');
const btnSend = document.getElementById('btn-send');

function addChatMessage(role, content) {
  const div = document.createElement('div');
  div.className = `chat-message ${role}`;
  div.textContent = content;
  chatMessages.appendChild(div);
  chatMessages.scrollTop = chatMessages.scrollHeight;
}

async function sendChat() {
  const message = chatInput.value.trim();
  if (!message) return;
  
  addChatMessage('user', message);
  chatInput.value = '';
  
  try {
    const result = await window.ottomanAgent.chat(message);
    
    if (result.error) {
      addChatMessage('assistant', `Error: ${result.error}`);
    } else {
      addChatMessage('assistant', result.output || result.message || JSON.stringify(result, null, 2));
    }
  } catch (error) {
    addChatMessage('assistant', `Error: ${error.message}`);
  }
}

btnSend.addEventListener('click', sendChat);
chatInput.addEventListener('keypress', (e) => {
  if (e.key === 'Enter') sendChat();
});

// Keys management
async function loadKeys() {
  const container = document.getElementById('keys-list');
  container.innerHTML = 'Loading...';
  
  try {
    const result = await window.ottomanAgent.listKeys();
    
    if (result.error) {
      container.innerHTML = `Error: ${result.error}`;
      return;
    }
    
    if (result.keys.length === 0) {
      container.innerHTML = '<p>No API keys configured. Add one below.</p>';
      return;
    }
    
    container.innerHTML = '';
    result.keys.forEach(key => {
      const div = document.createElement('div');
      div.className = 'list-item';
      div.innerHTML = `
        <div class="list-item-info">
          <span class="list-item-title">${key.service}</span>
          <span class="list-item-meta">ID: ${key.key_id} | Status: ${key.status} | Created: ${new Date(key.created_at).toLocaleDateString()}</span>
        </div>
        <div class="list-item-actions">
          <button class="btn btn-secondary btn-sm" onclick="rotateKey('${key.key_id}')">Rotate</button>
          <button class="btn btn-secondary btn-sm" onclick="revokeKey('${key.key_id}')">Revoke</button>
        </div>
      `;
      container.appendChild(div);
    });
  } catch (error) {
    container.innerHTML = `Error: ${error.message}`;
  }
}

document.getElementById('btn-create-key').addEventListener('click', async () => {
  const service = document.getElementById('key-service').value.trim();
  const keyValue = document.getElementById('key-value').value.trim();
  const scope = document.getElementById('key-scope').value;
  
  if (!service || !keyValue) {
    alert('Please fill in all fields');
    return;
  }
  
  try {
    const result = await window.ottomanAgent.createKey({
      service,
      api_key: keyValue,
      scope
    });
    
    if (result.key_id) {
      alert(`Key created: ${result.key_id}`);
      document.getElementById('key-service').value = '';
      document.getElementById('key-value').value = '';
      loadKeys();
    } else {
      alert(`Error: ${result.detail || result.error}`);
    }
  } catch (error) {
    alert(`Error: ${error.message}`);
  }
});

async function rotateKey(keyId) {
  const newKey = prompt('Enter new API key:');
  if (!newKey) return;
  
  try {
    const response = await fetch(`http://localhost:8000/api/v1/byok/keys/${keyId}/rotate`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ new_api_key: newKey })
    });
    
    const result = await response.json();
    if (result.success) {
      alert('Key rotated successfully');
      loadKeys();
    } else {
      alert('Error rotating key');
    }
  } catch (error) {
    alert(`Error: ${error.message}`);
  }
}

async function revokeKey(keyId) {
  if (!confirm('Are you sure you want to revoke this key?')) return;
  
  try {
    const response = await fetch(`http://localhost:8000/api/v1/byok/keys/${keyId}/revoke`, {
      method: 'POST'
    });
    
    const result = await response.json();
    if (result.success) {
      alert('Key revoked');
      loadKeys();
    } else {
      alert('Error revoking key');
    }
  } catch (error) {
    alert(`Error: ${error.message}`);
  }
}

// Tools
async function loadTools() {
  const container = document.getElementById('tools-list');
  container.innerHTML = 'Loading...';
  
  try {
    const response = await fetch('http://localhost:8000/api/v1/mcp/tools');
    const tools = await response.json();
    
    if (!Array.isArray(tools)) {
      container.innerHTML = '<p>No tools available</p>';
      return;
    }
    
    container.innerHTML = '';
    tools.forEach(tool => {
      const div = document.createElement('div');
      div.className = 'list-item';
      div.innerHTML = `
        <div class="list-item-info">
          <span class="list-item-title">${tool.name}</span>
          <span class="list-item-meta">${tool.description}</span>
        </div>
        <div class="list-item-actions">
          <button class="btn btn-primary btn-sm" onclick="executeTool('${tool.tool_id}')">Execute</button>
        </div>
      `;
      container.appendChild(div);
    });
  } catch (error) {
    container.innerHTML = `<p>Error loading tools: ${error.message}</p>`;
  }
}

async function executeTool(toolId) {
  const params = prompt('Enter parameters (JSON):', '{}');
  if (!params) return;
  
  try {
    const result = await window.ottomanAgent.executeTool(toolId, JSON.parse(params));
    alert(JSON.stringify(result, null, 2));
  } catch (error) {
    alert(`Error: ${error.message}`);
  }
}

// Workflows
async function loadWorkflows() {
  const container = document.getElementById('workflows-list');
  container.innerHTML = 'Loading...';
  
  try {
    const response = await fetch('http://localhost:8000/api/v1/workflows/');
    const workflows = await response.json();
    
    if (!Array.isArray(workflows)) {
      container.innerHTML = '<p>No workflows found</p>';
      return;
    }
    
    container.innerHTML = '';
    workflows.forEach(wf => {
      const div = document.createElement('div');
      div.className = 'list-item';
      div.innerHTML = `
        <div class="list-item-info">
          <span class="list-item-title">${wf.name}</span>
          <span class="list-item-meta">v${wf.version} | ${wf.node_count} nodes | ${wf.status}</span>
        </div>
        <div class="list-item-actions">
          <button class="btn btn-primary btn-sm" onclick="runWorkflow('${wf.workflow_id}')">Run</button>
        </div>
      `;
      container.appendChild(div);
    });
  } catch (error) {
    container.innerHTML = `<p>Error loading workflows: ${error.message}</p>`;
  }
}

async function runWorkflow(workflowId) {
  const input = prompt('Enter input (JSON):', '{}');
  if (!input) return;
  
  try {
    const result = await window.ottomanAgent.executeWorkflow(workflowId, JSON.parse(input));
    alert(JSON.stringify(result, null, 2));
  } catch (error) {
    alert(`Error: ${error.message}`);
  }
}

document.getElementById('btn-new-workflow').addEventListener('click', async () => {
  const name = prompt('Enter workflow name:');
  if (!name) return;
  
  try {
    const response = await fetch('http://localhost:8000/api/v1/workflows/', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ name })
    });
    
    const result = await response.json();
    if (result.workflow_id) {
      alert(`Workflow created: ${result.workflow_id}`);
      loadWorkflows();
    }
  } catch (error) {
    alert(`Error: ${error.message}`);
  }
});

// History
async function loadHistory() {
  const container = document.getElementById('history-list');
  container.innerHTML = 'Loading...';
  
  try {
    const response = await fetch('http://localhost:8000/api/v1/mcp/tools/history?limit=50');
    const data = await response.json();
    
    container.innerHTML = '';
    
    if (!data.calls || data.calls.length === 0) {
      container.innerHTML = '<p>No history yet</p>';
      return;
    }
    
    data.calls.forEach(call => {
      const div = document.createElement('div');
      div.className = 'list-item';
      div.innerHTML = `
        <div class="list-item-info">
          <span class="list-item-title">${call.tool_name}</span>
          <span class="list-item-meta">${new Date(call.started_at).toLocaleString()} | ${call.duration_ms.toFixed(0)}ms | ${call.error ? '❌' : '✅'}</span>
        </div>
      `;
      container.appendChild(div);
    });
  } catch (error) {
    container.innerHTML = `<p>Error loading history: ${error.message}</p>`;
  }
}

// Settings
const btnSettings = document.getElementById('btn-settings');
const settingsModal = document.getElementById('settings-modal');
const btnCloseSettings = document.getElementById('btn-close-settings');
const btnSaveSettings = document.getElementById('btn-save-settings');

btnSettings.addEventListener('click', () => {
  settingsModal.classList.remove('hidden');
});

btnCloseSettings.addEventListener('click', () => {
  settingsModal.classList.add('hidden');
});

btnSaveSettings.addEventListener('click', () => {
  const backendUrl = document.getElementById('setting-backend-url').value;
  const defaultModel = document.getElementById('setting-default-model').value;
  
  localStorage.setItem('ottoman-agent-settings', JSON.stringify({ backendUrl, defaultModel }));
  settingsModal.classList.add('hidden');
  alert('Settings saved');
});

// Load settings on startup
const savedSettings = localStorage.getItem('ottoman-agent-settings');
if (savedSettings) {
  const settings = JSON.parse(savedSettings);
  document.getElementById('setting-backend-url').value = settings.backendUrl || 'http://localhost:8000';
  document.getElementById('setting-default-model').value = settings.defaultModel || 'deepseek-v4-flash';
}

// Menu actions
window.ottomanAgent.onMenuAction((action) => {
  if (action === 'new-translation') {
    document.querySelector('[data-tab="transliterate"]').click();
  } else if (action === 'open-file') {
    window.ottomanAgent.openFile().then(paths => {
      if (paths && paths.length > 0) {
        // Read and populate input
        require('fs').readFile(paths[0], 'utf8', (err, data) => {
          if (err) {
            alert('Error reading file');
            return;
          }
          ottomanInput.value = data;
        });
      }
    });
  }
});

// Initial load
loadKeys();
