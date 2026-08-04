/**
 * Ottoman Agent - Simple Renderer Process
 */

// Backend URL (from settings or default)
let backendUrl = 'http://localhost:8001';

// Tab navigation
document.querySelectorAll('.nav-item').forEach(item => {
    item.addEventListener('click', () => {
        document.querySelectorAll('.nav-item').forEach(i => i.classList.remove('active'));
        item.classList.add('active');
        
        const tab = item.dataset.tab;
        document.querySelectorAll('.tab-content').forEach(content => {
            content.classList.remove('active');
        });
        document.getElementById(`tab-${tab}`).classList.add('active');
    });
});

// Backend status check
async function checkBackendStatus() {
    const statusIndicator = document.getElementById('backend-status');
    const dot = statusIndicator.querySelector('.status-dot');
    const text = statusIndicator.querySelector('.status-text');
    
    try {
        const response = await fetch(`${backendUrl}/api/health`);
        const data = await response.json();
        
        if (data.status === 'healthy') {
            dot.classList.add('running');
            text.textContent = 'Backend: Çalışıyor';
        } else {
            dot.classList.remove('running');
            text.textContent = 'Backend: Hata';
        }
    } catch (error) {
        dot.classList.remove('running');
        text.textContent = 'Backend: Bağlı Değil';
    }
}

// Test backend button
document.getElementById('btn-test-backend').addEventListener('click', checkBackendStatus);

// Direction selector
let currentDirection = 'ot-to-tr';
document.querySelectorAll('input[name="direction"]').forEach(radio => {
    radio.addEventListener('change', (e) => {
        currentDirection = e.target.value;
        updateDirectionUI();
    });
});

function updateDirectionUI() {
    const inputLabel = document.getElementById('input-label');
    const outputLabel = document.getElementById('output-label');
    const inputText = document.getElementById('input-text');
    const outputText = document.getElementById('output-text');
    
    if (currentDirection === 'ot-to-tr') {
        inputLabel.textContent = 'Osmanlıca Metin (Arap Harfi)';
        inputText.placeholder = 'عثمانلي توركجهسى...';
        outputLabel.textContent = 'Modern Türkçe Sonuç';
        outputText.placeholder = 'Sonuç burada görünecek...';
    } else {
        inputLabel.textContent = 'Modern Türkçe Metin';
        inputText.placeholder = 'Osmanlı Türkçesi...';
        outputLabel.textContent = 'Osmanlıca Sonuç (Arap Harfi)';
        outputText.placeholder = 'عثمانلي توركجهسى...';
    }
    
    document.querySelectorAll('.direction-option').forEach(opt => {
        opt.classList.remove('active');
    });
    document.querySelector(`input[name="direction"][value="${currentDirection}"]`).closest('.direction-option').classList.add('active');
}

// Swap button
const btnSwap = document.getElementById('btn-swap');
if (btnSwap) {
    btnSwap.addEventListener('click', () => {
        const inputText = document.getElementById('input-text');
        const outputText = document.getElementById('output-text');
        const temp = inputText.value;
        inputText.value = outputText.value;
        outputText.value = temp;
        
        // Toggle direction
        const radios = document.querySelectorAll('input[name="direction"]');
        radios.forEach(radio => {
            if (radio.value === 'ot-to-tr') {
                radio.checked = radio.checked === false;
            } else {
                radio.checked = !radio.checked;
            }
        });
        currentDirection = currentDirection === 'ot-to-tr' ? 'tr-to-ot' : 'ot-to-tr';
        updateDirectionUI();
    });
}

// Transliterate button
document.getElementById('btn-transliterate').addEventListener('click', async () => {
    const text = document.getElementById('input-text').value.trim();
    const mode = document.getElementById('mode-select').value;
    const outputText = document.getElementById('output-text');
    const resultInfo = document.getElementById('result-info');
    
    if (!text) {
        outputText.value = 'Lütfen metin girin';
        return;
    }
    
    outputText.value = 'Çevriliyor...';
    resultInfo.classList.add('hidden');
    
    try {
        const response = await fetch(`${backendUrl}/api/transliterate`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                text: text,
                mode: mode,
                direction: currentDirection
            })
        });
        
        const data = await response.json();
        
        if (data.success) {
            outputText.value = data.output;
            resultInfo.classList.remove('hidden');
            document.getElementById('result-confidence').textContent = `Güven: ${(data.confidence * 100).toFixed(1)}%`;
            document.getElementById('result-method').textContent = `Mod: ${data.method}`;
            document.getElementById('result-direction').textContent = `Yön: ${data.direction === 'ot-to-tr' ? 'Osmanlıca→Türkçe' : 'Türkçe→Osmanlıca'}`;
        } else {
            outputText.value = `Hata: ${data.detail || 'Bilinmeyen hata'}`;
        }
    } catch (error) {
        outputText.value = `Bağlantı hatası: ${error.message}`;
    }
});

// Clear button
document.getElementById('btn-clear').addEventListener('click', () => {
    document.getElementById('input-text').value = '';
    document.getElementById('output-text').value = '';
    document.getElementById('result-info').classList.add('hidden');
});

// Copy button
document.getElementById('btn-copy').addEventListener('click', () => {
    const outputText = document.getElementById('output-text');
    if (outputText.value) {
        navigator.clipboard.writeText(outputText.value);
        const btn = document.getElementById('btn-copy');
        const originalText = btn.textContent;
        btn.textContent = 'Kopyalandı!';
        setTimeout(() => {
            btn.textContent = originalText;
        }, 1500);
    }
});

// Chat functionality
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
        const response = await fetch(`${backendUrl}/api/chat`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                message: message,
                model: 'deepseek-v4-flash'
            })
        });
        
        const data = await response.json();
        
        if (data.success) {
            addChatMessage('assistant', data.output);
        } else {
            addChatMessage('assistant', `Hata: ${data.detail || 'Bilinmeyen hata'}`);
        }
    } catch (error) {
        addChatMessage('assistant', `Bağlantı hatası: ${error.message}`);
    }
}

btnSend.addEventListener('click', sendChat);
chatInput.addEventListener('keypress', (e) => {
    if (e.key === 'Enter') sendChat();
});

// Settings modal
const btnSettings = document.getElementById('btn-settings');
const settingsModal = document.getElementById('settings-modal');
const btnCloseSettings = document.getElementById('btn-close-settings');
const btnSaveSettings = document.getElementById('btn-save-settings');
const settingBackendUrl = document.getElementById('setting-backend-url');

btnSettings.addEventListener('click', () => {
    settingsModal.classList.remove('hidden');
});

btnCloseSettings.addEventListener('click', () => {
    settingsModal.classList.add('hidden');
});

btnSaveSettings.addEventListener('click', () => {
    backendUrl = settingBackendUrl.value;
    localStorage.setItem('ottoman-backend-url', backendUrl);
    settingsModal.classList.add('hidden');
    checkBackendStatus();
});

// Load settings on startup
const savedUrl = localStorage.getItem('ottoman-backend-url');
if (savedUrl) {
    backendUrl = savedUrl;
    settingBackendUrl.value = backendUrl;
}

// Initial check
checkBackendStatus();
