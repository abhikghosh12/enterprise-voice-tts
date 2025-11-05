# Troubleshooting Guide - Ollama Connection Issues

## Problem: "⚫ Ollama (Not connected)" in browser

### Quick Fix (Most Common)

1. **Make sure Ollama is running**:
   ```bash
   ollama serve
   ```
   Leave this terminal open!

2. **Restart the browser**:
   - Close the Enterprise Voice Browser
   - Run `npm start` again or double-click `start-browser.bat`

3. **Check Settings**:
   - Click the ⚙️ **Settings** button in top-right
   - Verify endpoint is: `http://localhost:11434`
   - Click **"Test Connection"**
   - If successful, click **"Save Settings"**

### Detailed Troubleshooting

#### Step 1: Verify Ollama is Running

**Test from command line**:
```bash
curl http://localhost:11434/api/tags
```

**Expected output**: JSON with list of models

**If this fails**:
- Ollama is not running
- Run: `ollama serve`
- On Windows, you may need to start it as a service

#### Step 2: Check for Models

```bash
ollama list
```

**If no models found**:
```bash
ollama pull llama3.2:1b
# Or
ollama pull llama3.2
ollama pull mistral
```

#### Step 3: Test Ollama API Directly

```bash
curl -X POST http://localhost:11434/api/generate \
  -d '{"model": "llama3.2:1b", "prompt": "Say hi", "stream": false}'
```

**If this works**, Ollama is fine. The issue is with the browser connection.

#### Step 4: Check Browser Console

1. Start the browser with DevTools:
   - Edit `main.js` line 25
   - Uncomment: `mainWindow.webContents.openDevTools();`
   - Restart browser

2. Look for errors in Console tab:
   - Red errors about "Failed to fetch"
   - CORS errors
   - Network errors
   - Connection refused

#### Step 5: Check Firewall

Windows Firewall may block Electron:

1. Open **Windows Defender Firewall**
2. Click **Allow an app through firewall**
3. Find **Electron** or **Node.js**
4. Check both **Private** and **Public** boxes
5. Click **OK**

#### Step 6: Try Different Endpoint

If localhost doesn't work, try:

1. Open Settings (⚙️)
2. Try these alternatives:
   - `http://127.0.0.1:11434`
   - `http://[::1]:11434` (IPv6)
3. Test each one
4. Save the one that works

### Common Issues

#### Issue 1: "Connection Refused"

**Cause**: Ollama not running or wrong port

**Solution**:
```bash
# Check if Ollama is on port 11434
netstat -ano | findstr :11434

# If nothing found, Ollama isn't running
ollama serve

# If it's on a different port, use that in Settings
```

#### Issue 2: "No models found"

**Cause**: Ollama running but no models pulled

**Solution**:
```bash
ollama pull llama3.2:1b
```

Then refresh browser or click Settings → Test Connection

#### Issue 3: "ECONNREFUSED" in DevTools

**Cause**: Network/firewall blocking localhost

**Solution**:
1. Check Windows Firewall (Step 5 above)
2. Try `127.0.0.1` instead of `localhost`
3. Disable VPN if running
4. Check antivirus isn't blocking

#### Issue 4: Sandbox blocking requests

**Symptoms**: Works with `sandbox: false` but not `sandbox: true`

**Solution**: This shouldn't happen because the **main process** makes API calls, not the renderer. If it does:

1. Check DevTools Network tab
2. Verify requests are going through IPC (electronAPI)
3. Make sure you're using the updated code (v2.0)

#### Issue 5: Ollama on different port

**Cause**: Ollama running on non-default port

**Check**:
```bash
# Windows
netstat -ano | findstr ollama

# Or check Ollama environment
echo %OLLAMA_HOST%
```

**Solution**:
1. Open Settings
2. Enter correct endpoint, e.g., `http://localhost:8080`
3. Test and Save

#### Issue 6: Remote Ollama not accessible

**Cause**: Ollama only listening on localhost

**Solution** (on Ollama server):
```bash
# Set Ollama to listen on all interfaces
set OLLAMA_HOST=0.0.0.0:11434
ollama serve

# Or use specific IP
set OLLAMA_HOST=192.168.1.100:11434
ollama serve
```

Then in browser Settings:
```
http://192.168.1.100:11434
```

### Diagnostic Script

Run the diagnostic script:
```bash
cd C:\git\enterprise-voice-tts\browser
diagnose.bat
```

This checks:
- ✅ Ollama service running
- ✅ Models available
- ✅ API working
- ✅ Endpoint configuration

### Manual Testing

#### Test 1: Check Ollama Tags
```bash
curl http://localhost:11434/api/tags
```

#### Test 2: Test Chat API
```bash
curl -X POST http://localhost:11434/api/chat \
  -H "Content-Type: application/json" \
  -d '{
    "model": "llama3.2:1b",
    "messages": [{"role": "user", "content": "Hi"}],
    "stream": false
  }'
```

#### Test 3: Check Browser IPC

In DevTools Console:
```javascript
// Test if electronAPI is available
console.log(window.electronAPI);

// Test getting endpoint
window.electronAPI.getOllamaEndpoint().then(console.log);

// Test getting models
window.electronAPI.ollamaModels().then(console.log);
```

### Still Not Working?

#### Enable Debug Logging

1. Edit `main.js`
2. Add logging to IPC handlers:

```javascript
// Around line 147
ipcMain.handle('ollama-models', async () => {
  console.log('Fetching models from:', ollamaEndpoint);
  try {
    const response = await axios.get(`${ollamaEndpoint}/api/tags`, {
      timeout: 5000
    });
    console.log('Models response:', response.data);
    return {
      success: true,
      models: response.data.models || []
    };
  } catch (error) {
    console.error('Failed to fetch models:', error.message);
    console.error('Error details:', error.response?.data);
    return {
      success: false,
      error: error.response?.data?.error || error.message,
      models: []
    };
  }
});
```

3. Restart browser
4. Check terminal for logs

#### Check Network

In DevTools (F12) → Network tab:
- Should see NO network requests to Ollama (IPC handles it)
- If you see CORS errors, something is wrong with IPC

#### Verify Code Version

Make sure you have v2.0:

```bash
cd C:\git\enterprise-voice-tts\browser
git log --oneline -1
# Or check CHANGELOG.md
```

### Getting Help

If still stuck:

1. **Gather info**:
   - Output of `diagnose.bat`
   - DevTools Console errors
   - Terminal logs from `npm start`
   - Ollama version: `ollama --version`
   - Node version: `node --version`

2. **Check these files are updated**:
   - `main.js` - Has `sanitizeInput` function
   - `preload.js` - Has `setOllamaEndpoint`
   - `renderer.js` - Has settings functions
   - `index.html` - Has settings modal

3. **Try clean install**:
   ```bash
   cd C:\git\enterprise-voice-tts\browser
   rmdir /s /q node_modules
   npm install
   npm start
   ```

### Success Checklist

When working properly, you should see:

- ✅ "🟢 Ollama" in status bar (bottom-right)
- ✅ Models in dropdown (AI sidebar)
- ✅ Settings → Test Connection = Success
- ✅ Can send messages and get responses
- ✅ Streaming text appears smoothly

---

**Last Updated**: 2025-10-27
**Version**: 2.0
