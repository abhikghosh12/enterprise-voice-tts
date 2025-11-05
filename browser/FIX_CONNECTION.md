# Fix: Connection failed: connect ECONNREFUSED ::1:11434

## The Problem

The error `ECONNREFUSED ::1:11434` means the browser tried to connect to Ollama using **IPv6** (`::1`) but Ollama is only listening on **IPv4** (`127.0.0.1`).

## ✅ Quick Fix

### Option 1: Use the Updated Browser (Recommended)

The browser has been updated to use `127.0.0.1` by default instead of `localhost`.

**Just restart the browser:**

1. Close the browser
2. From **PowerShell** or **CMD** (not Git Bash):
   ```powershell
   cd C:\git\enterprise-voice-tts\browser
   npm start
   ```

The connection should now work! ✅

### Option 2: Manual Settings Update

If you already have the browser open:

1. Click **⚙️ Settings** (top-right)
2. Change endpoint from `http://localhost:11434` to:
   ```
   http://127.0.0.1:11434
   ```
3. Click **"Test Connection"** - should show success!
4. Click **"Save Settings"**
5. Status bar should now show **"🟢 Ollama"**

## Why This Happens

- `localhost` can resolve to either IPv4 (`127.0.0.1`) or IPv6 (`::1`)
- On your system, it's resolving to IPv6
- Ollama only listens on IPv4 by default
- Using `127.0.0.1` explicitly forces IPv4

## Verify Ollama is Running

From PowerShell:
```powershell
# Test IPv4 (should work)
curl http://127.0.0.1:11434/api/tags

# Test IPv6 (will fail if Ollama not configured for it)
curl http://[::1]:11434/api/tags
```

## Make Ollama Listen on IPv6 (Optional)

If you prefer using `localhost` or IPv6:

1. Stop Ollama
2. Set environment variable:
   ```powershell
   $env:OLLAMA_HOST="[::]:11434"
   ollama serve
   ```
3. Now Ollama listens on both IPv4 and IPv6

But the **easier solution** is just using `127.0.0.1` in the browser.

## Status After Fix

After applying the fix, you should see:

- ✅ Status bar: **"🟢 Ollama"** (green, not red/black)
- ✅ Settings → Test Connection: **"Connected! Found X model(s)"**
- ✅ Model dropdown: Shows your models (llama3.2:1b, etc.)
- ✅ Chat works: Can send messages and get responses

## Still Not Working?

### Check 1: Is Ollama Actually Running?

```powershell
curl http://127.0.0.1:11434/api/tags
```

Should return JSON with models. If not:
```powershell
ollama serve
```

### Check 2: Do You Have Models?

```powershell
ollama list
```

If empty:
```powershell
ollama pull llama3.2:1b
```

### Check 3: Browser Started from PowerShell?

**Don't use Git Bash!** Use PowerShell or CMD:
```powershell
cd C:\git\enterprise-voice-tts\browser
npm start
```

### Check 4: Check DevTools

If DevTools is open (F12), look for errors in Console tab.

## Permanent Fix Applied

The browser code has been updated:
- **File**: `main.js` line 6
- **Changed from**: `http://localhost:11434`
- **Changed to**: `http://127.0.0.1:11434`

This ensures all new browser instances use IPv4 by default.

## Additional Notes

### For Remote Ollama

If Ollama is on another machine, use its IP address:
```
http://192.168.1.100:11434
```

### For Custom Port

If Ollama runs on a different port:
```
http://127.0.0.1:8080
```

### For HTTPS

If using HTTPS (rare for local):
```
https://127.0.0.1:11434
```

---

**Fixed**: 2025-10-27
**Issue**: IPv6 vs IPv4 resolution
**Solution**: Use explicit IPv4 address (127.0.0.1)
