const { app, BrowserWindow, ipcMain, session, shell, dialog } = require('electron');
const path = require('path');
const axios = require('axios');

let mainWindow;
let ollamaEndpoint = 'http://127.0.0.1:11434'; // Configurable endpoint (using IPv4 for compatibility)

// Check if this is first run
async function checkOllamaOnStartup() {
  try {
    const response = await axios.get(`${ollamaEndpoint}/api/tags`, {
      timeout: 3000
    });
    return { connected: true, models: response.data.models || [] };
  } catch (error) {
    return { connected: false, models: [] };
  }
}

function createWindow() {
  mainWindow = new BrowserWindow({
    width: 1400,
    height: 900,
    webPreferences: {
      preload: path.join(__dirname, 'preload.js'),
      contextIsolation: true,
      nodeIntegration: false,
      webviewTag: true,
      sandbox: true
    },
    icon: path.join(__dirname, 'icon.png')
  });

  mainWindow.loadFile('index.html');

  // Open DevTools in development (temporarily enabled for debugging)
  mainWindow.webContents.openDevTools();

  mainWindow.on('closed', function () {
    mainWindow = null;
  });

  // Check Ollama connection after window loads
  mainWindow.webContents.on('did-finish-load', async () => {
    const status = await checkOllamaOnStartup();

    if (!status.connected) {
      // Show setup dialog
      const result = await dialog.showMessageBox(mainWindow, {
        type: 'warning',
        title: 'Ollama Required',
        message: 'Ollama AI Engine Not Detected',
        detail: 'Enterprise Voice Browser requires Ollama to be installed and running.\n\n' +
                'Ollama is a free AI engine that runs language models on your computer.\n\n' +
                'Would you like to:\n' +
                '1. Download Ollama now?\n' +
                '2. View setup instructions?',
        buttons: ['Download Ollama', 'View Setup Guide', 'Continue Anyway'],
        defaultId: 0,
        cancelId: 2
      });

      if (result.response === 0) {
        // Open Ollama download page
        shell.openExternal('https://ollama.com/download');
      } else if (result.response === 1) {
        // Open setup guide
        shell.openExternal('https://github.com/ollama/ollama#quickstart');
      }
    } else if (status.models.length === 0) {
      // Ollama connected but no models
      dialog.showMessageBox(mainWindow, {
        type: 'info',
        title: 'No AI Models Found',
        message: 'Ollama is running but no models are installed',
        detail: 'To use AI features, you need to download at least one model.\n\n' +
                'Open PowerShell and run:\n' +
                'ollama pull llama3.2:1b\n\n' +
                'This downloads a fast, 1.3GB AI model.\n\n' +
                'After downloading, restart the browser.',
        buttons: ['OK']
      });
    }
  });
}

app.whenReady().then(() => {
  createWindow();

  app.on('activate', function () {
    if (BrowserWindow.getAllWindows().length === 0) createWindow();
  });
});

app.on('window-all-closed', function () {
  if (process.platform !== 'darwin') app.quit();
});

// Validate and sanitize input
function sanitizeInput(input) {
  if (!input || typeof input !== 'string') return '';
  // Remove potential control characters and limit length
  return input.replace(/[\x00-\x1F\x7F]/g, '').substring(0, 10000);
}

// Handle Ollama API requests with conversation history
ipcMain.handle('ollama-chat', async (event, messages, model = 'llama3.2') => {
  try {
    // Validate messages array
    if (!Array.isArray(messages) || messages.length === 0) {
      throw new Error('Invalid messages format');
    }

    // Sanitize all messages
    const sanitizedMessages = messages.map(msg => ({
      role: msg.role === 'assistant' ? 'assistant' : 'user',
      content: sanitizeInput(msg.content)
    }));

    const response = await axios.post(`${ollamaEndpoint}/api/chat`, {
      model: sanitizeInput(model),
      messages: sanitizedMessages,
      stream: false
    }, {
      timeout: 30000 // 30 second timeout
    });

    return {
      success: true,
      message: response.data.message.content
    };
  } catch (error) {
    console.error('Ollama error:', error);
    return {
      success: false,
      error: error.response?.data?.error || error.message
    };
  }
});

// Handle streaming Ollama requests with conversation history
ipcMain.handle('ollama-chat-stream', async (event, messages, model = 'llama3.2') => {
  try {
    // Validate messages array
    if (!Array.isArray(messages) || messages.length === 0) {
      throw new Error('Invalid messages format');
    }

    // Sanitize all messages
    const sanitizedMessages = messages.map(msg => ({
      role: msg.role === 'assistant' ? 'assistant' : 'user',
      content: sanitizeInput(msg.content)
    }));

    const response = await axios.post(`${ollamaEndpoint}/api/chat`, {
      model: sanitizeInput(model),
      messages: sanitizedMessages,
      stream: true
    }, {
      responseType: 'stream',
      timeout: 60000 // 60 second timeout for streaming
    });

    return new Promise((resolve, reject) => {
      let fullResponse = '';

      response.data.on('data', (chunk) => {
        const lines = chunk.toString().split('\n').filter(line => line.trim());

        for (const line of lines) {
          try {
            const json = JSON.parse(line);
            if (json.message && json.message.content) {
              const sanitizedContent = sanitizeInput(json.message.content);
              fullResponse += sanitizedContent;
              mainWindow?.webContents.send('ollama-stream-chunk', sanitizedContent);
            }
          } catch (e) {
            console.error('Parse error:', e);
          }
        }
      });

      response.data.on('end', () => {
        resolve({ success: true, message: fullResponse });
      });

      response.data.on('error', (error) => {
        reject({ success: false, error: error.message });
      });
    });
  } catch (error) {
    console.error('Ollama stream error:', error);
    return {
      success: false,
      error: error.response?.data?.error || error.message
    };
  }
});

// Get available Ollama models
ipcMain.handle('ollama-models', async () => {
  try {
    const response = await axios.get(`${ollamaEndpoint}/api/tags`, {
      timeout: 5000
    });
    return {
      success: true,
      models: response.data.models || []
    };
  } catch (error) {
    console.error('Failed to fetch models:', error);
    return {
      success: false,
      error: error.response?.data?.error || error.message,
      models: []
    };
  }
});

// Set Ollama endpoint
ipcMain.handle('set-ollama-endpoint', async (_event, endpoint) => {
  try {
    // Validate endpoint format
    const url = new URL(endpoint);
    if (url.protocol !== 'http:' && url.protocol !== 'https:') {
      throw new Error('Invalid protocol. Use http:// or https://');
    }
    ollamaEndpoint = endpoint.replace(/\/$/, ''); // Remove trailing slash
    return { success: true, endpoint: ollamaEndpoint };
  } catch (error) {
    return { success: false, error: error.message };
  }
});

// Get current Ollama endpoint
ipcMain.handle('get-ollama-endpoint', async () => {
  return { success: true, endpoint: ollamaEndpoint };
});
