const { contextBridge, ipcRenderer } = require('electron');

contextBridge.exposeInMainWorld('electronAPI', {
  // Ollama API
  ollamaChat: (messages, model) => ipcRenderer.invoke('ollama-chat', messages, model),
  ollamaChatStream: (messages, model) => ipcRenderer.invoke('ollama-chat-stream', messages, model),
  ollamaModels: () => ipcRenderer.invoke('ollama-models'),
  setOllamaEndpoint: (endpoint) => ipcRenderer.invoke('set-ollama-endpoint', endpoint),
  getOllamaEndpoint: () => ipcRenderer.invoke('get-ollama-endpoint'),
  onStreamChunk: (callback) => ipcRenderer.on('ollama-stream-chunk', (_event, chunk) => callback(chunk))
});
