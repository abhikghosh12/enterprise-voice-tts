// Setup Checker - Helps users install Ollama
const { shell } = require('electron');
const axios = require('axios');

class SetupChecker {
  constructor() {
    this.ollamaInstalled = false;
    this.ollamaRunning = false;
    this.modelsAvailable = false;
  }

  // Check if Ollama is installed and running
  async checkOllama() {
    try {
      const response = await axios.get('http://127.0.0.1:11434/api/tags', {
        timeout: 3000
      });

      this.ollamaRunning = true;
      this.ollamaInstalled = true;
      this.modelsAvailable = response.data.models && response.data.models.length > 0;

      return {
        installed: true,
        running: true,
        models: response.data.models || []
      };
    } catch (error) {
      // Ollama not running or not installed
      return {
        installed: false,
        running: false,
        models: []
      };
    }
  }

  // Open Ollama download page
  openOllamaDownload() {
    shell.openExternal('https://ollama.com/download');
  }

  // Open Ollama documentation
  openOllamaGuide() {
    shell.openExternal('https://github.com/ollama/ollama#quickstart');
  }

  // Generate setup instructions
  getSetupInstructions() {
    return {
      title: 'Ollama Setup Required',
      message: `Enterprise Voice Browser requires Ollama to be installed.

Ollama is an AI engine that runs language models locally on your computer.

Steps to install:
1. Download Ollama from ollama.com
2. Install Ollama
3. Open PowerShell and run: ollama serve
4. Download a model: ollama pull llama3.2:1b
5. Restart this browser

Would you like to download Ollama now?`,
      buttons: ['Download Ollama', 'Show Guide', 'Cancel']
    };
  }
}

module.exports = SetupChecker;
