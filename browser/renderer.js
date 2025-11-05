// DOM Elements
const webview = document.getElementById('webview');
const urlBar = document.getElementById('urlBar');
const backBtn = document.getElementById('backBtn');
const forwardBtn = document.getElementById('forwardBtn');
const refreshBtn = document.getElementById('refreshBtn');
const homeBtn = document.getElementById('homeBtn');
const goBtn = document.getElementById('goBtn');
const aiToggleBtn = document.getElementById('aiToggleBtn');
const aiSidebar = document.getElementById('aiSidebar');
const closeSidebarBtn = document.getElementById('closeSidebarBtn');
const chatContainer = document.getElementById('chatContainer');
const chatInput = document.getElementById('chatInput');
const sendBtn = document.getElementById('sendBtn');
const voiceInputBtn = document.getElementById('voiceInputBtn');
const toggleSpeechBtn = document.getElementById('toggleSpeechBtn');
const chatVoiceBtn = document.getElementById('chatVoiceBtn');
const voiceModal = document.getElementById('voiceModal');
const stopVoiceBtn = document.getElementById('stopVoiceBtn');
const voiceText = document.getElementById('voiceText');
const statusText = document.getElementById('statusText');
const ollamaStatus = document.getElementById('ollamaStatus');
const voiceStatus = document.getElementById('voiceStatus');
const modelSelector = document.getElementById('modelSelector');
const settingsBtn = document.getElementById('settingsBtn');
const settingsModal = document.getElementById('settingsModal');
const closeSettingsBtn = document.getElementById('closeSettingsBtn');
const ollamaEndpointInput = document.getElementById('ollamaEndpointInput');
const saveSettingsBtn = document.getElementById('saveSettingsBtn');
const testConnectionBtn = document.getElementById('testConnectionBtn');
const clearHistoryBtn = document.getElementById('clearHistoryBtn');
const settingsStatus = document.getElementById('settingsStatus');

// State
let speechEnabled = true;
let recognition = null;
let synthesis = window.speechSynthesis;
let currentModel = 'llama3.2';
let conversationHistory = [];
let isCheckingConnection = false; // Race condition prevention

// Initialize
document.addEventListener('DOMContentLoaded', () => {
    initializeWebview();
    initializeSpeechRecognition();
    initializeEventListeners();
    loadOllamaModels();
    checkOllamaConnection();
    loadSettings();
});

// Webview Management
function initializeWebview() {
    webview.addEventListener('did-start-loading', () => {
        statusText.textContent = 'Loading...';
    });

    webview.addEventListener('did-stop-loading', () => {
        statusText.textContent = 'Ready';
        urlBar.value = webview.getURL();
    });

    webview.addEventListener('page-title-updated', (e) => {
        document.title = e.title + ' - Enterprise Voice Browser';
    });

    webview.addEventListener('new-window', (e) => {
        webview.loadURL(e.url);
    });
}

// Event Listeners
function initializeEventListeners() {
    // Navigation
    backBtn.addEventListener('click', () => webview.goBack());
    forwardBtn.addEventListener('click', () => webview.goForward());
    refreshBtn.addEventListener('click', () => webview.reload());
    homeBtn.addEventListener('click', () => navigateToURL('https://www.google.com'));
    
    goBtn.addEventListener('click', () => navigateToURL(urlBar.value));
    urlBar.addEventListener('keypress', (e) => {
        if (e.key === 'Enter') navigateToURL(urlBar.value);
    });

    // AI Sidebar
    aiToggleBtn.addEventListener('click', toggleAISidebar);
    closeSidebarBtn.addEventListener('click', toggleAISidebar);

    // Chat
    sendBtn.addEventListener('click', sendMessage);
    chatInput.addEventListener('keypress', (e) => {
        if (e.key === 'Enter' && !e.shiftKey) {
            e.preventDefault();
            sendMessage();
        }
    });

    // Voice
    voiceInputBtn.addEventListener('click', startVoiceInput);
    chatVoiceBtn.addEventListener('click', startVoiceInput);
    stopVoiceBtn.addEventListener('click', stopVoiceInput);
    toggleSpeechBtn.addEventListener('click', toggleSpeech);

    // Model selector
    modelSelector.addEventListener('change', (e) => {
        currentModel = e.target.value;
        addMessage('System', `Switched to model: ${currentModel}`, 'ai');
    });

    // Quick actions
    document.querySelectorAll('.quick-btn').forEach(btn => {
        btn.addEventListener('click', () => handleQuickAction(btn.dataset.action));
    });

    // Stream chunk listener
    window.electronAPI.onStreamChunk((chunk) => {
        appendToLastMessage(chunk);
    });

    // Settings
    settingsBtn.addEventListener('click', openSettings);
    closeSettingsBtn.addEventListener('click', closeSettings);
    saveSettingsBtn.addEventListener('click', saveSettings);
    testConnectionBtn.addEventListener('click', testConnection);
    clearHistoryBtn.addEventListener('click', clearChatHistory);
}

// Navigation
function navigateToURL(url) {
    if (!url) return;
    
    // Add protocol if missing
    if (!url.startsWith('http://') && !url.startsWith('https://') && !url.startsWith('file://')) {
        // Check if it looks like a domain
        if (url.includes('.') && !url.includes(' ')) {
            url = 'https://' + url;
        } else {
            // Treat as search query
            url = 'https://www.google.com/search?q=' + encodeURIComponent(url);
        }
    }
    
    webview.loadURL(url);
    urlBar.value = url;
}

// AI Sidebar
function toggleAISidebar() {
    aiSidebar.classList.toggle('hidden');
    aiToggleBtn.classList.toggle('active');
}

// Chat Functions
async function sendMessage() {
    const message = chatInput.value.trim();
    if (!message) return;

    chatInput.value = '';
    sendBtn.disabled = true;

    addMessage('You', message, 'user');
    conversationHistory.push({ role: 'user', content: message });

    // Show thinking indicator
    const thinkingMsg = addMessage('AI', 'Thinking...', 'thinking');

    try {
        // Use streaming for better UX with full conversation history
        thinkingMsg.remove();
        const aiMsg = addMessage('AI', '', 'ai');

        const result = await window.electronAPI.ollamaChatStream(conversationHistory, currentModel);

        if (!result.success) {
            aiMsg.textContent = 'Error: ' + result.error;
            aiMsg.classList.add('error');
            aiMsg.classList.remove('ai');
        } else {
            conversationHistory.push({ role: 'assistant', content: result.message });

            // Text-to-speech for AI response
            if (speechEnabled) {
                speak(result.message);
            }
        }
    } catch (error) {
        const errorMsg = thinkingMsg.querySelector ? thinkingMsg : addMessage('AI', '', 'error');
        errorMsg.textContent = 'Error: ' + (error.message || 'Unknown error');
        errorMsg.classList.remove('thinking');
        errorMsg.classList.add('error');
        console.error('Chat error:', error);
    } finally {
        sendBtn.disabled = false;
        chatInput.focus();
    }
}

function addMessage(sender, text, type) {
    const messageDiv = document.createElement('div');
    messageDiv.className = `message ${type}`;
    messageDiv.textContent = text;
    
    // Remove welcome message if it exists
    const welcome = chatContainer.querySelector('.welcome-message');
    if (welcome) welcome.remove();
    
    chatContainer.appendChild(messageDiv);
    chatContainer.scrollTop = chatContainer.scrollHeight;
    
    return messageDiv;
}

// Improved streaming with batching to reduce reflows
let streamBuffer = '';
let streamTimer = null;

function appendToLastMessage(chunk) {
    streamBuffer += chunk;

    // Clear existing timer
    if (streamTimer) {
        clearTimeout(streamTimer);
    }

    // Batch updates every 50ms for better performance
    streamTimer = setTimeout(() => {
        const messages = chatContainer.querySelectorAll('.message.ai');
        if (messages.length > 0) {
            const lastMessage = messages[messages.length - 1];
            lastMessage.textContent += streamBuffer;
            streamBuffer = '';
            chatContainer.scrollTop = chatContainer.scrollHeight;
        }
    }, 50);
}

// Quick Actions
async function handleQuickAction(action) {
    try {
        const pageContent = await getPageContent();
        
        switch (action) {
            case 'summarize':
                chatInput.value = `Please summarize this webpage: ${pageContent.substring(0, 2000)}`;
                sendMessage();
                break;
            case 'explain':
                const selection = await getPageSelection();
                if (selection) {
                    chatInput.value = `Please explain: "${selection}"`;
                    sendMessage();
                } else {
                    addMessage('System', 'Please select some text on the page first.', 'error');
                }
                break;
            case 'translate':
                chatInput.value = 'Please translate this page to English';
                sendMessage();
                break;
        }
    } catch (error) {
        addMessage('System', 'Error: ' + error.message, 'error');
    }
}

async function getPageContent() {
    try {
        return await webview.executeJavaScript('document.body.innerText');
    } catch (error) {
        return '';
    }
}

async function getPageSelection() {
    try {
        return await webview.executeJavaScript('window.getSelection().toString()');
    } catch (error) {
        return '';
    }
}

// Speech Recognition
function initializeSpeechRecognition() {
    if ('webkitSpeechRecognition' in window) {
        recognition = new webkitSpeechRecognition();
        recognition.continuous = false;
        recognition.interimResults = true;
        recognition.lang = 'en-US';

        recognition.onresult = (event) => {
            const transcript = Array.from(event.results)
                .map(result => result[0].transcript)
                .join('');
            
            voiceText.textContent = transcript;
            
            if (event.results[0].isFinal) {
                chatInput.value = transcript;
                stopVoiceInput();
                sendMessage();
            }
        };

        recognition.onerror = (event) => {
            console.error('Speech recognition error:', event.error);
            voiceText.textContent = 'Error: ' + event.error;
            setTimeout(stopVoiceInput, 2000);
        };

        recognition.onend = () => {
            voiceInputBtn.classList.remove('active');
            chatVoiceBtn.classList.remove('recording');
        };

        voiceStatus.textContent = '🟢 Voice';
        voiceStatus.classList.add('connected');
    } else {
        voiceStatus.textContent = '⚫ Voice (Not supported)';
        voiceInputBtn.disabled = true;
        chatVoiceBtn.disabled = true;
    }
}

function startVoiceInput() {
    if (!recognition) return;
    
    voiceModal.classList.remove('hidden');
    voiceText.textContent = 'Listening...';
    voiceInputBtn.classList.add('active');
    chatVoiceBtn.classList.add('recording');
    
    try {
        recognition.start();
    } catch (error) {
        console.error('Failed to start recognition:', error);
    }
}

function stopVoiceInput() {
    if (recognition) {
        recognition.stop();
    }
    voiceModal.classList.add('hidden');
    voiceInputBtn.classList.remove('active');
    chatVoiceBtn.classList.remove('recording');
}

function toggleSpeech() {
    speechEnabled = !speechEnabled;
    toggleSpeechBtn.textContent = speechEnabled ? '🔊' : '🔇';
    toggleSpeechBtn.style.background = speechEnabled ? '#3d3d3d' : '#c42b1c';
    
    if (!speechEnabled) {
        synthesis.cancel();
    }
}

function speak(text) {
    if (!speechEnabled || !synthesis) return;
    
    synthesis.cancel();
    
    const utterance = new SpeechSynthesisUtterance(text);
    utterance.rate = 1.0;
    utterance.pitch = 1.0;
    utterance.volume = 1.0;
    
    // Try to use a natural voice
    const voices = synthesis.getVoices();
    const preferredVoice = voices.find(voice => 
        voice.lang.startsWith('en') && voice.localService
    );
    if (preferredVoice) {
        utterance.voice = preferredVoice;
    }
    
    synthesis.speak(utterance);
}

// Ollama Integration
async function loadOllamaModels() {
    try {
        const result = await window.electronAPI.ollamaModels();
        
        if (result.success && result.models.length > 0) {
            modelSelector.innerHTML = '';
            result.models.forEach(model => {
                const option = document.createElement('option');
                option.value = model.name;
                option.textContent = `${model.name} (${formatSize(model.size)})`;
                modelSelector.appendChild(option);
            });
            
            // Set current model to first available
            currentModel = result.models[0].name;
            ollamaStatus.textContent = '🟢 Ollama';
            ollamaStatus.classList.add('connected');
        } else {
            throw new Error('No models found');
        }
    } catch (error) {
        console.error('Failed to load models:', error);
        modelSelector.innerHTML = '<option value="">Ollama not connected</option>';
        ollamaStatus.textContent = '⚫ Ollama (Not connected)';
        ollamaStatus.classList.remove('connected');
    }
}

async function checkOllamaConnection() {
    // Prevent race conditions
    if (isCheckingConnection) return;

    isCheckingConnection = true;
    try {
        const result = await window.electronAPI.ollamaModels();
        if (result.success) {
            if (!ollamaStatus.classList.contains('connected')) {
                ollamaStatus.textContent = '🟢 Ollama';
                ollamaStatus.classList.add('connected');
                loadOllamaModels();
            }
        } else {
            ollamaStatus.textContent = '⚫ Ollama';
            ollamaStatus.classList.remove('connected');
        }
    } catch (error) {
        ollamaStatus.textContent = '⚫ Ollama';
        ollamaStatus.classList.remove('connected');
    } finally {
        isCheckingConnection = false;
    }
}

// Check connection every 10 seconds
setInterval(checkOllamaConnection, 10000);

function formatSize(bytes) {
    const gb = bytes / (1024 * 1024 * 1024);
    if (gb >= 1) {
        return gb.toFixed(1) + ' GB';
    }
    const mb = bytes / (1024 * 1024);
    return mb.toFixed(0) + ' MB';
}

// Settings Functions
async function loadSettings() {
    try {
        const result = await window.electronAPI.getOllamaEndpoint();
        if (result.success) {
            ollamaEndpointInput.value = result.endpoint;
        }
    } catch (error) {
        console.error('Failed to load settings:', error);
    }
}

function openSettings() {
    settingsModal.classList.remove('hidden');
    settingsStatus.textContent = '';
    settingsStatus.className = 'settings-status';
}

function closeSettings() {
    settingsModal.classList.add('hidden');
}

async function saveSettings() {
    const endpoint = ollamaEndpointInput.value.trim();

    if (!endpoint) {
        showSettingsStatus('Please enter an endpoint', 'error');
        return;
    }

    try {
        const result = await window.electronAPI.setOllamaEndpoint(endpoint);

        if (result.success) {
            showSettingsStatus('Settings saved successfully!', 'success');
            // Reload models with new endpoint
            setTimeout(() => {
                loadOllamaModels();
                checkOllamaConnection();
            }, 500);
        } else {
            showSettingsStatus('Error: ' + result.error, 'error');
        }
    } catch (error) {
        showSettingsStatus('Error: ' + error.message, 'error');
    }
}

async function testConnection() {
    showSettingsStatus('Testing connection...', 'info');
    testConnectionBtn.disabled = true;

    try {
        const result = await window.electronAPI.ollamaModels();

        if (result.success && result.models.length > 0) {
            showSettingsStatus(`Connected! Found ${result.models.length} model(s)`, 'success');
        } else if (result.success && result.models.length === 0) {
            showSettingsStatus('Connected, but no models found. Run: ollama pull llama3.2', 'error');
        } else {
            showSettingsStatus('Connection failed: ' + result.error, 'error');
        }
    } catch (error) {
        showSettingsStatus('Connection failed: ' + error.message, 'error');
    } finally {
        testConnectionBtn.disabled = false;
    }
}

function clearChatHistory() {
    if (confirm('Are you sure you want to clear the chat history?')) {
        conversationHistory = [];
        chatContainer.innerHTML = `
            <div class="welcome-message">
                <h4>Chat history cleared!</h4>
                <p>Start a new conversation</p>
            </div>
        `;
        showSettingsStatus('Chat history cleared', 'success');
    }
}

function showSettingsStatus(message, type) {
    settingsStatus.textContent = message;
    settingsStatus.className = `settings-status ${type}`;
}
