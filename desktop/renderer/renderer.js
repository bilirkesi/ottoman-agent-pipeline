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

// Transliteration - TWO-WAY
const btnTransliterate = document.getElementById('btn-transliterate');
const inputText = document.getElementById('input-text');
const outputText = document.getElementById('output-text');
const metricsBox = document.getElementById('transliteration-metrics');
const inputLabel = document.getElementById('input-label');
const outputLabel = document.getElementById('output-label');
const btnSwap = document.getElementById('btn-swap');
const btnClear = document.getElementById('btn-clear');
const btnCopy = document.getElementById('btn-copy');

let currentDirection = 'ot-to-tr';

// Direction selector
document.querySelectorAll('input[name="direction"]').forEach(radio => {
    radio.addEventListener('change', (e) => {
        currentDirection = e.target.value;
        updateDirectionUI();
    });
});

// Swap button - swap input and output
btnSwap.addEventListener('click', () => {
    // Swap input and output
    const temp = inputText.value;
    inputText.value = outputText.value;
    outputText.value = temp;
    
    // Swap direction
    currentDirection = currentDirection === 'ot-to-tr' ? 'tr-to-ot' : 'ot-to-tr';
    document.querySelector(`input[name="direction"][value="${currentDirection}"]`).checked = true;
    
    updateDirectionUI();
});

// Clear button
btnClear.addEventListener('click', () => {
    inputText.value = '';
    outputText.value = '';
    metricsBox.textContent = '';
});

// Copy button
btnCopy.addEventListener('click', () => {
    if (outputText.value) {
        navigator.clipboard.writeText(outputText.value);
        const originalText = btnCopy.textContent;
        btnCopy.textContent = 'Copied!';
        setTimeout(() => {
            btnCopy.textContent = originalText;
        }, 1500);
    }
});

function updateDirectionUI() {
    // Update labels
    if (currentDirection === 'ot-to-tr') {
        inputLabel.textContent = 'Ottoman Turkish Text (Arap Harfi)';
        inputText.placeholder = 'عثمانلي توركجهسى...';
        outputLabel.textContent = 'Modern Turkish Result';
        outputText.placeholder = 'Result will appear here...';
    } else {
        inputLabel.textContent = 'Modern Turkish Text';
        inputText.placeholder = 'Osmanlı Türkçesi...';
        outputLabel.textContent = 'Osmanlıca Result (Arap Harfi)';
        outputText.placeholder = 'عثمانلي توركجهسى...';
    }
    
    // Update active state
    document.querySelectorAll('.direction-option').forEach(opt => {
        opt.classList.remove('active');
    });
    document.querySelector(`input[name="direction"][value="${currentDirection}"]`).closest('.direction-option').classList.add('active');
}

btnTransliterate.addEventListener('click', async () => {
    const text = inputText.value.trim();
    if (!text) {
        outputText.textContent = 'Lütfen metin girin';
        return;
    }
    const mode = document.querySelector('input[name="mode"]:checked').value;
    outputText.textContent = 'İşleniyor...';
    metricsBox.textContent = '';
    
    try {
        const result = await window.ottomanAgent.transliterate(text, { 
            mode,
            direction: currentDirection
        });
        if (result.error) {
            outputText.textContent = `Hata: ${result.error}`;
        } else {
            // Determine output field based on direction
            const output = currentDirection === 'ot-to-tr' 
                ? (result.modern_turkish || result.output)
                : (result.osmanlica || result.output);
            outputText.textContent = output || JSON.stringify(result, null, 2);
            metricsBox.innerHTML = `Güven: ${(result.confidence * 100).toFixed(1)}% | Yöntem: ${result.method || mode} | Yön: ${currentDirection === 'ot-to-tr' ? 'Osmanlıca→Türkçe' : 'Türkçe→Osmanlıca'}`;
        }
    } catch (error) {
        outputText.textContent = `Hata: ${error.message}`;
    }
});

// Chat
const chatInput = document.getElementById('chat-input');
const chatMessages = document.getElementById('chat-messages');
const btnSend = document.getElementById('btn-send');

function addChatMessage(role, content) {
    const div = document.createElement('div');
    div.className = `chat-message ${role}`;
    
    // Handle JSON content
    try {
        const json = JSON.parse(content);
        if (json.output) {
            div.textContent = json.output;
        } else {
            div.textContent = content;
        }
    } catch {
        div.textContent = content;
    }
    
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
            addChatMessage('assistant', `Hata: ${result.error}`);
        } else {
            addChatMessage('assistant', result.output || 'Yanıt alındı');
        }
    } catch (error) {
        addChatMessage('assistant', `Hata: ${error.message}`);
    }
}

btnSend.addEventListener('click', sendChat);
chatInput.addEventListener('keypress', (e) => {
    if (e.key === 'Enter') sendChat();
});

// Keys management
async function loadKeys() {
    const container = document.getElementById('keys-list');
    container.innerHTML = 'Yükleniyor...';
    
    try {
        const result = await window.ottomanAgent.listKeys();
        if (result.error) {
            container.innerHTML = `Hata: ${result.error}`;
            return;
        }
        
        if (result.keys.length === 0) {
            container.innerHTML = '<p>API key bulunamadı. Aşağıdan ekleyin.</p>';
            return;
        }
        
        container.innerHTML = '';
        result.keys.forEach(key => {
            const div = document.createElement('div');
            div.className = 'list-item';
            div.innerHTML = `
                <div class="key-info">
                    <strong>${key.service}</strong>
                    <span>ID: ${key.key_id}</span>
                    <span class="key-status ${key.status}">Durum: ${key.status}</span>
                    <span>Oluşturuldu: ${new Date(key.created_at).toLocaleDateString()}</span>
                </div>
                <div class="key-actions">
                    <button onclick="rotateKey('${key.key_id}')">Rotate</button>
                    <button onclick="revokeKey('${key.key_id}')">Revoke</button>
                </div>
            `;
            container.appendChild(div);
        });
    } catch (error) {
        container.innerHTML = `Hata: ${error.message}`;
    }
}

document.getElementById('btn-create-key').addEventListener('click', async () => {
    const service = document.getElementById('key-service').value.trim();
    const keyValue = document.getElementById('key-value').value.trim();
    const scope = document.getElementById('key-scope').value;
    
    if (!service || !keyValue) {
        alert('Lütfen tüm alanları doldurun');
        return;
    }
    
    try {
        const result = await window.ottomanAgent.createKey({ service, api_key: keyValue, scope });
        if (result.key_id) {
            alert(`Key oluşturuldu: ${result.key_id}`);
            document.getElementById('key-service').value = '';
            document.getElementById('key-value').value = '';
            loadKeys();
        } else {
            alert(`Hata: ${result.detail || result.error}`);
        }
    } catch (error) {
        alert(`Hata: ${error.message}`);
    }
});

async function rotateKey(keyId) {
    const newKey = prompt('Yeni API key girin:');
    if (!newKey) return;
    
    try {
        const response = await fetch(`http://localhost:8000/api/v1/byok/keys/${keyId}/rotate`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ new_api_key: newKey })
        });
        const result = await response.json();
        if (result.success) {
            alert('Key başarıyla rotate edildi');
            loadKeys();
        } else {
            alert('Rotate hatası');
        }
    } catch (error) {
        alert(`Hata: ${error.message}`);
    }
}

async function revokeKey(keyId) {
    if (!confirm('Bu key\'i iptal etmek istediğinizden emin misiniz?')) return;
    
    try {
        const response = await fetch(`http://localhost:8000/api/v1/byok/keys/${keyId}/revoke`, {
            method: 'POST'
        });
        const result = await response.json();
        if (result.success) {
            alert('Key iptal edildi');
            loadKeys();
        } else {
            alert('İptal hatası');
        }
    } catch (error) {
        alert(`Hata: ${error.message}`);
    }
}

// Tools
async function loadTools() {
    const container = document.getElementById('tools-list');
    container.innerHTML = 'Yükleniyor...';
    
    try {
        const response = await fetch('http://localhost:8000/api/v1/mcp/tools');
        const tools = await response.json();
        
        if (!Array.isArray(tools)) {
            container.innerHTML = '<p>Tool bulunamadı</p>';
            return;
        }
        
        container.innerHTML = '';
        tools.forEach(tool => {
            const div = document.createElement('div');
            div.className = 'list-item';
            div.innerHTML = `
                <div class="tool-info">
                    <strong>${tool.name}</strong>
                    <span>${tool.description}</span>
                </div>
                <button onclick="executeTool('${tool.tool_id}')">Execute</button>
            `;
            container.appendChild(div);
        });
    } catch (error) {
        container.innerHTML = `Tool yüklenirken hata: ${error.message}`;
    }
}

async function executeTool(toolId) {
    const params = prompt('Parametreleri girin (JSON):', '{}');
    if (!params) return;
    
    try {
        const result = await window.ottomanAgent.executeTool(toolId, JSON.parse(params));
        alert(JSON.stringify(result, null, 2));
    } catch (error) {
        alert(`Hata: ${error.message}`);
    }
}

// Workflows
async function loadWorkflows() {
    const container = document.getElementById('workflows-list');
    container.innerHTML = 'Yükleniyor...';
    
    try {
        const response = await fetch('http://localhost:8000/api/v1/workflows/');
        const workflows = await response.json();
        
        if (!Array.isArray(workflows)) {
            container.innerHTML = '<p>Workflow bulunamadı</p>';
            return;
        }
        
        container.innerHTML = '';
        workflows.forEach(wf => {
            const div = document.createElement('div');
            div.className = 'list-item';
            div.innerHTML = `
                <div class="workflow-info">
                    <strong>${wf.name}</strong>
                    <span>v${wf.version}</span>
                    <span>${wf.node_count} düğüm</span>
                    <span class="workflow-status ${wf.status}">${wf.status}</span>
                </div>
                <button onclick="runWorkflow('${wf.workflow_id}')">Run</button>
            `;
            container.appendChild(div);
        });
    } catch (error) {
        container.innerHTML = `Workflow yüklenirken hata: ${error.message}`;
    }
}

async function runWorkflow(workflowId) {
    const input = prompt('Giriş verisini girin (JSON):', '{}');
    if (!input) return;
    
    try {
        const result = await window.ottomanAgent.executeWorkflow(workflowId, JSON.parse(input));
        alert(JSON.stringify(result, null, 2));
    } catch (error) {
        alert(`Hata: ${error.message}`);
    }
}

document.getElementById('btn-new-workflow').addEventListener('click', async () => {
    const name = prompt('Workflow adı girin:');
    if (!name) return;
    
    try {
        const response = await fetch('http://localhost:8000/api/v1/workflows/', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ name })
        });
        const result = await response.json();
        if (result.workflow_id) {
            alert(`Workflow oluşturuldu: ${result.workflow_id}`);
            loadWorkflows();
        }
    } catch (error) {
        alert(`Hata: ${error.message}`);
    }
});

// History
async function loadHistory() {
    const container = document.getElementById('history-list');
    container.innerHTML = 'Yükleniyor...';
    
    try {
        const response = await fetch('http://localhost:8000/api/v1/mcp/tools/history?limit=50');
        const data = await response.json();
        
        container.innerHTML = '';
        
        if (!data.calls || data.calls.length === 0) {
            container.innerHTML = '<p>Henüz geçiş yok</p>';
            return;
        }
        
        data.calls.forEach(call => {
            const div = document.createElement('div');
            div.className = 'list-item';
            div.innerHTML = `
                <div class="history-info">
                    <strong>${call.tool_name}</strong>
                    <span>${new Date(call.started_at).toLocaleString()}</span>
                    <span>${call.duration_ms.toFixed(0)}ms</span>
                    <span class="history-status">${call.error ? '❌' : '✅'}</span>
                </div>
            `;
            container.appendChild(div);
        });
    } catch (error) {
        container.innerHTML = `Geçmiş yüklenirken hata: ${error.message}`;
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
    alert('Ayarlar kaydedildi');
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
                require('fs').readFile(paths[0], 'utf8', (err, data) => {
                    if (err) {
                        alert('Dosya okunurken hata');
                        return;
                    }
                    inputText.value = data;
                });
            }
        });
    }
});

// Initial load
loadKeys();
