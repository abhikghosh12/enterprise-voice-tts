# 🌐 Web Browser Extension Integration

Convert any website text to speech with a browser extension.

## Chrome Extension

### manifest.json

```json
{
  "manifest_version": 3,
  "name": "Voice TTS Reader",
  "version": "1.0.0",
  "description": "Convert any text to speech using your local TTS engine",
  "permissions": [
    "activeTab",
    "contextMenus",
    "storage"
  ],
  "background": {
    "service_worker": "background.js"
  },
  "content_scripts": [{
    "matches": ["<all_urls>"],
    "js": ["content.js"],
    "css": ["styles.css"]
  }],
  "action": {
    "default_popup": "popup.html",
    "default_icon": {
      "16": "icons/icon16.png",
      "48": "icons/icon48.png",
      "128": "icons/icon128.png"
    }
  },
  "options_page": "options.html",
  "icons": {
    "16": "icons/icon16.png",
    "48": "icons/icon48.png",
    "128": "icons/icon128.png"
  }
}
```

### background.js

```javascript
// Create context menu for selected text
chrome.runtime.onInstalled.addListener(() => {
  chrome.contextMenus.create({
    id: 'speak-selection',
    title: 'Speak "%s"',
    contexts: ['selection']
  });
  
  chrome.contextMenus.create({
    id: 'speak-page',
    title: 'Speak entire page',
    contexts: ['page']
  });
});

// Handle context menu clicks
chrome.contextMenus.onClicked.addListener((info, tab) => {
  if (info.menuItemId === 'speak-selection') {
    speakText(info.selectionText, tab.id);
  } else if (info.menuItemId === 'speak-page') {
    chrome.tabs.sendMessage(tab.id, { action: 'getPageText' }, (response) => {
      if (response && response.text) {
        speakText(response.text, tab.id);
      }
    });
  }
});

// TTS API integration
async function speakText(text, tabId) {
  try {
    // Get settings
    const settings = await chrome.storage.sync.get({
      apiUrl: 'http://localhost:5000',
      apiKey: '',
      voiceId: 'en-US-lessac-medium',
      engine: 'piper'
    });
    
    // Call TTS API
    const response = await fetch(`${settings.apiUrl}/api/v1/lightning/get_speech`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        ...(settings.apiKey && { 'Authorization': `Bearer ${settings.apiKey}` })
      },
      body: JSON.stringify({
        text: text,
        voice_id: settings.voiceId,
        engine: settings.engine
      })
    });
    
    const data = await response.json();
    
    // Poll for completion
    const result = await pollJobCompletion(data.job_id, settings.apiUrl);
    
    // Play audio in content script
    chrome.tabs.sendMessage(tabId, {
      action: 'playAudio',
      audioUrl: result.audio_url
    });
    
  } catch (error) {
    console.error('TTS Error:', error);
    chrome.notifications.create({
      type: 'basic',
      iconUrl: 'icons/icon48.png',
      title: 'TTS Error',
      message: error.message
    });
  }
}

async function pollJobCompletion(jobId, apiUrl, timeout = 30000) {
  const startTime = Date.now();
  
  while (Date.now() - startTime < timeout) {
    const response = await fetch(`${apiUrl}/api/v1/jobs/${jobId}`);
    const data = await response.json();
    
    if (data.status === 'completed') {
      return data.result;
    } else if (data.status === 'failed') {
      throw new Error(data.error || 'Job failed');
    }
    
    await new Promise(resolve => setTimeout(resolve, 500));
  }
  
  throw new Error('Job timeout');
}

// Handle keyboard shortcuts
chrome.commands.onCommand.addListener((command) => {
  if (command === 'speak-selection') {
    chrome.tabs.query({ active: true, currentWindow: true }, (tabs) => {
      chrome.tabs.sendMessage(tabs[0].id, { action: 'speakSelection' });
    });
  }
});
```

### content.js

```javascript
// Audio player
let currentAudio = null;
let audioPlayer = null;

// Initialize audio player
function initAudioPlayer() {
  if (!audioPlayer) {
    audioPlayer = new Audio();
    audioPlayer.onended = () => {
      removeHighlight();
    };
  }
  return audioPlayer;
}

// Listen for messages from background script
chrome.runtime.onMessage.addListener((request, sender, sendResponse) => {
  if (request.action === 'getPageText') {
    // Extract readable text from page
    const text = extractPageText();
    sendResponse({ text: text });
  }
  
  else if (request.action === 'playAudio') {
    playAudio(request.audioUrl);
  }
  
  else if (request.action === 'speakSelection') {
    const selectedText = window.getSelection().toString();
    if (selectedText) {
      // Send to background script
      chrome.runtime.sendMessage({
        action: 'speak',
        text: selectedText
      });
    }
  }
  
  return true;
});

function extractPageText() {
  // Get main content (try article tag first, then body)
  const article = document.querySelector('article') || document.querySelector('main') || document.body;
  
  // Remove scripts, styles, etc.
  const clone = article.cloneNode(true);
  clone.querySelectorAll('script, style, nav, footer, header, aside').forEach(el => el.remove());
  
  // Get text content
  return clone.innerText.trim();
}

function playAudio(audioUrl) {
  const player = initAudioPlayer();
  
  // Stop current audio if playing
  if (!player.paused) {
    player.pause();
    player.currentTime = 0;
  }
  
  // Play new audio
  player.src = audioUrl;
  player.play().catch(error => {
    console.error('Audio play error:', error);
  });
  
  // Highlight current text (optional)
  highlightText();
}

function highlightText() {
  const selection = window.getSelection();
  if (!selection.rangeCount) return;
  
  const range = selection.getRangeAt(0);
  const span = document.createElement('span');
  span.className = 'tts-highlight';
  span.style.backgroundColor = 'yellow';
  span.style.transition = 'background-color 0.3s';
  
  try {
    range.surroundContents(span);
  } catch (e) {
    // Ignore errors for complex selections
  }
}

function removeHighlight() {
  document.querySelectorAll('.tts-highlight').forEach(el => {
    const parent = el.parentNode;
    parent.replaceChild(document.createTextNode(el.textContent), el);
    parent.normalize();
  });
}

// Add floating control panel
function createControlPanel() {
  const panel = document.createElement('div');
  panel.id = 'tts-control-panel';
  panel.innerHTML = `
    <div class="tts-controls">
      <button id="tts-play-pause">⏸️</button>
      <button id="tts-stop">⏹️</button>
      <input type="range" id="tts-speed" min="0.5" max="2" step="0.1" value="1">
      <span id="tts-time">0:00 / 0:00</span>
    </div>
  `;
  
  document.body.appendChild(panel);
  
  // Event listeners
  document.getElementById('tts-play-pause').addEventListener('click', () => {
    if (audioPlayer.paused) {
      audioPlayer.play();
    } else {
      audioPlayer.pause();
    }
  });
  
  document.getElementById('tts-stop').addEventListener('click', () => {
    audioPlayer.pause();
    audioPlayer.currentTime = 0;
    removeHighlight();
  });
  
  document.getElementById('tts-speed').addEventListener('input', (e) => {
    audioPlayer.playbackRate = e.target.value;
  });
}
```

### popup.html

```html
<!DOCTYPE html>
<html>
<head>
  <meta charset="UTF-8">
  <style>
    body {
      width: 300px;
      padding: 15px;
      font-family: Arial, sans-serif;
    }
    
    h2 {
      margin-top: 0;
      color: #333;
    }
    
    .voice-select, .engine-select {
      width: 100%;
      padding: 8px;
      margin: 10px 0;
      border: 1px solid #ddd;
      border-radius: 4px;
    }
    
    button {
      width: 100%;
      padding: 10px;
      margin: 5px 0;
      background: #4CAF50;
      color: white;
      border: none;
      border-radius: 4px;
      cursor: pointer;
      font-size: 14px;
    }
    
    button:hover {
      background: #45a049;
    }
    
    .status {
      margin-top: 10px;
      padding: 10px;
      background: #f0f0f0;
      border-radius: 4px;
      font-size: 12px;
    }
  </style>
</head>
<body>
  <h2>🎙️ Voice TTS Reader</h2>
  
  <select class="voice-select" id="voiceSelect">
    <option value="en-US-lessac-medium">US Male (Fast)</option>
    <option value="en-US-libritts-high">US Female (Fast)</option>
    <option value="en-GB-alan-medium">UK Male (Fast)</option>
    <option value="en-US-GuyNeural">US Male (Quality)</option>
  </select>
  
  <select class="engine-select" id="engineSelect">
    <option value="piper">Piper (Fastest)</option>
    <option value="edge">Edge TTS (Quality)</option>
    <option value="coqui">Coqui (Best)</option>
  </select>
  
  <button id="speakSelection">🔊 Speak Selection</button>
  <button id="speakPage">📄 Speak Entire Page</button>
  <button id="stopSpeaking">⏹️ Stop</button>
  <button id="openOptions">⚙️ Settings</button>
  
  <div class="status" id="status">Ready</div>
  
  <script src="popup.js"></script>
</body>
</html>
```

### popup.js

```javascript
// Load saved settings
chrome.storage.sync.get(['voiceId', 'engine'], (items) => {
  if (items.voiceId) {
    document.getElementById('voiceSelect').value = items.voiceId;
  }
  if (items.engine) {
    document.getElementById('engineSelect').value = items.engine;
  }
});

// Save settings on change
document.getElementById('voiceSelect').addEventListener('change', (e) => {
  chrome.storage.sync.set({ voiceId: e.target.value });
});

document.getElementById('engineSelect').addEventListener('change', (e) => {
  chrome.storage.sync.set({ engine: e.target.value });
});

// Speak selection button
document.getElementById('speakSelection').addEventListener('click', async () => {
  updateStatus('Getting selected text...');
  
  const [tab] = await chrome.tabs.query({ active: true, currentWindow: true });
  
  chrome.tabs.sendMessage(tab.id, { action: 'speakSelection' });
  
  updateStatus('Generating speech...');
});

// Speak page button
document.getElementById('speakPage').addEventListener('click', async () => {
  updateStatus('Extracting page text...');
  
  const [tab] = await chrome.tabs.query({ active: true, currentWindow: true });
  
  chrome.tabs.sendMessage(tab.id, { action: 'getPageText' }, (response) => {
    if (response && response.text) {
      // Send to background for processing
      chrome.runtime.sendMessage({
        action: 'speak',
        text: response.text
      });
      
      updateStatus('Generating speech...');
    }
  });
});

// Stop button
document.getElementById('stopSpeaking').addEventListener('click', async () => {
  const [tab] = await chrome.tabs.query({ active: true, currentWindow: true });
  
  chrome.tabs.sendMessage(tab.id, { action: 'stopAudio' });
  
  updateStatus('Stopped');
});

// Settings button
document.getElementById('openOptions').addEventListener('click', () => {
  chrome.runtime.openOptionsPage();
});

function updateStatus(message) {
  document.getElementById('status').textContent = message;
}
```

### options.html

```html
<!DOCTYPE html>
<html>
<head>
  <meta charset="UTF-8">
  <style>
    body {
      font-family: Arial, sans-serif;
      max-width: 600px;
      margin: 20px auto;
      padding: 20px;
    }
    
    h1 {
      color: #333;
    }
    
    .setting {
      margin: 20px 0;
    }
    
    label {
      display: block;
      margin-bottom: 5px;
      font-weight: bold;
    }
    
    input[type="text"], input[type="password"] {
      width: 100%;
      padding: 8px;
      border: 1px solid #ddd;
      border-radius: 4px;
    }
    
    button {
      padding: 10px 20px;
      background: #4CAF50;
      color: white;
      border: none;
      border-radius: 4px;
      cursor: pointer;
      margin-top: 10px;
    }
    
    button:hover {
      background: #45a049;
    }
    
    .success {
      color: green;
      margin-top: 10px;
    }
    
    .error {
      color: red;
      margin-top: 10px;
    }
  </style>
</head>
<body>
  <h1>⚙️ Voice TTS Reader Settings</h1>
  
  <div class="setting">
    <label for="apiUrl">TTS API URL:</label>
    <input type="text" id="apiUrl" placeholder="http://localhost:5000">
    <small>Default: http://localhost:5000</small>
  </div>
  
  <div class="setting">
    <label for="apiKey">API Key (optional):</label>
    <input type="password" id="apiKey" placeholder="Leave empty if not required">
  </div>
  
  <div class="setting">
    <label for="defaultVoice">Default Voice:</label>
    <select id="defaultVoice">
      <option value="en-US-lessac-medium">US Male (Fast)</option>
      <option value="en-US-libritts-high">US Female (Fast)</option>
      <option value="en-GB-alan-medium">UK Male (Fast)</option>
      <option value="en-US-GuyNeural">US Male (Quality)</option>
    </select>
  </div>
  
  <div class="setting">
    <label for="defaultEngine">Default Engine:</label>
    <select id="defaultEngine">
      <option value="piper">Piper (Fastest)</option>
      <option value="edge">Edge TTS (Quality)</option>
      <option value="coqui">Coqui (Best)</option>
    </select>
  </div>
  
  <button id="saveBtn">💾 Save Settings</button>
  <button id="testBtn">🧪 Test Connection</button>
  
  <div id="message"></div>
  
  <script src="options.js"></script>
</body>
</html>
```

### options.js

```javascript
// Load saved settings
document.addEventListener('DOMContentLoaded', () => {
  chrome.storage.sync.get({
    apiUrl: 'http://localhost:5000',
    apiKey: '',
    voiceId: 'en-US-lessac-medium',
    engine: 'piper'
  }, (items) => {
    document.getElementById('apiUrl').value = items.apiUrl;
    document.getElementById('apiKey').value = items.apiKey;
    document.getElementById('defaultVoice').value = items.voiceId;
    document.getElementById('defaultEngine').value = items.engine;
  });
});

// Save settings
document.getElementById('saveBtn').addEventListener('click', () => {
  const settings = {
    apiUrl: document.getElementById('apiUrl').value,
    apiKey: document.getElementById('apiKey').value,
    voiceId: document.getElementById('defaultVoice').value,
    engine: document.getElementById('defaultEngine').value
  };
  
  chrome.storage.sync.set(settings, () => {
    showMessage('Settings saved successfully!', 'success');
  });
});

// Test connection
document.getElementById('testBtn').addEventListener('click', async () => {
  const apiUrl = document.getElementById('apiUrl').value;
  const apiKey = document.getElementById('apiKey').value;
  
  try {
    showMessage('Testing connection...', '');
    
    const response = await fetch(`${apiUrl}/api/v1/health`, {
      headers: {
        ...(apiKey && { 'Authorization': `Bearer ${apiKey}` })
      }
    });
    
    if (response.ok) {
      const data = await response.json();
      showMessage(`✅ Connection successful! Status: ${data.status}`, 'success');
    } else {
      showMessage(`❌ Connection failed: ${response.statusText}`, 'error');
    }
  } catch (error) {
    showMessage(`❌ Error: ${error.message}`, 'error');
  }
});

function showMessage(text, type) {
  const messageDiv = document.getElementById('message');
  messageDiv.textContent = text;
  messageDiv.className = type;
}
```

## Package & Deploy

```bash
# 1. Create extension package
zip -r voice-tts-extension.zip manifest.json background.js content.js popup.html popup.js options.html options.js styles.css icons/

# 2. Load in Chrome
# - Go to chrome://extensions/
# - Enable "Developer mode"
# - Click "Load unpacked"
# - Select extension folder

# 3. Test
# - Right-click on any webpage
# - Select text and choose "Speak"
```

## Firefox Extension (WebExtension)

The same code works for Firefox! Just change manifest_version to 2:

```json
{
  "manifest_version": 2,
  "name": "Voice TTS Reader",
  ...
}
```

## Usage Examples

1. **Read Articles**: Select text → Right-click → "Speak"
2. **Read Entire Page**: Right-click → "Speak entire page"
3. **Keyboard Shortcut**: Press `Ctrl+Shift+S` to speak selection
4. **Control Playback**: Use floating control panel

---

**Performance**: 0.3-0.8s latency with Piper engine!

**Privacy**: All processing happens locally on your TTS server.
