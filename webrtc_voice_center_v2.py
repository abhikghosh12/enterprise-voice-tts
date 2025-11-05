#!/usr/bin/env python3
"""
WebRTC Voice AI Contact Center - IMPROVED VERSION
Better error handling and debugging
"""

from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.responses import HTMLResponse
from fastapi.middleware.cors import CORSMiddleware
import json
import uuid
from datetime import datetime
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(title="WebRTC Voice AI Contact Center")

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Active calls storage
active_calls = {}

@app.websocket("/ws/call")
async def websocket_call_endpoint(websocket: WebSocket):
    """WebSocket endpoint for voice calls"""
    call_id = str(uuid.uuid4())
    
    try:
        await websocket.accept()
        active_calls[call_id] = websocket
        logger.info(f"✅ Call connected: {call_id}")
        
        # Send connection confirmation
        await websocket.send_json({
            "type": "connected",
            "call_id": call_id,
            "message": "WebSocket connected successfully!",
            "timestamp": datetime.now().isoformat()
        })
        
        # Send greeting
        await websocket.send_json({
            "type": "greeting",
            "text": "Hello! I'm your AI assistant. Start speaking and I'll respond!",
            "timestamp": datetime.now().isoformat()
        })
        
        # Handle incoming messages
        while True:
            try:
                data = await websocket.receive_json()
                logger.info(f"📩 Received message type: {data.get('type')}")
                
                if data["type"] == "audio_data":
                    # Audio received
                    audio_size = len(data.get("audio", ""))
                    logger.info(f"🎤 Audio received: {audio_size} bytes")
                    
                    # Echo back confirmation
                    await websocket.send_json({
                        "type": "audio_received",
                        "message": f"Received {audio_size} bytes of audio",
                        "timestamp": datetime.now().isoformat()
                    })
                    
                    # Send demo response
                    await websocket.send_json({
                        "type": "ai_response",
                        "text": "I heard you! This is a test response.",
                        "timestamp": datetime.now().isoformat()
                    })
                    
                elif data["type"] == "end_call":
                    logger.info(f"📞 Call ended by user: {call_id}")
                    break
                    
                elif data["type"] == "ping":
                    await websocket.send_json({"type": "pong"})
                    
            except json.JSONDecodeError as e:
                logger.error(f"❌ JSON decode error: {e}")
                await websocket.send_json({
                    "type": "error",
                    "message": "Invalid JSON format"
                })
                
    except WebSocketDisconnect:
        logger.info(f"🔌 WebSocket disconnected: {call_id}")
    except Exception as e:
        logger.error(f"❌ WebSocket error: {e}", exc_info=True)
    finally:
        # Clean up
        if call_id in active_calls:
            del active_calls[call_id]
        logger.info(f"🧹 Cleaned up call: {call_id}")

@app.get("/")
async def get_call_interface():
    """Serve the improved WebRTC call interface"""
    return HTMLResponse(content="""
<!DOCTYPE html>
<html>
<head>
    <title>Voice AI Contact Center</title>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body { 
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
            padding: 20px;
        }
        .container {
            max-width: 800px;
            margin: 0 auto;
            background: white;
            border-radius: 20px;
            padding: 40px;
            box-shadow: 0 20px 60px rgba(0,0,0,0.3);
        }
        h1 { 
            text-align: center;
            color: #333;
            margin-bottom: 10px;
        }
        .subtitle {
            text-align: center;
            color: #666;
            margin-bottom: 30px;
        }
        .call-button {
            display: block;
            width: 200px;
            margin: 20px auto;
            padding: 20px;
            font-size: 18px;
            font-weight: bold;
            border: none;
            border-radius: 50px;
            cursor: pointer;
            transition: all 0.3s;
            box-shadow: 0 4px 15px rgba(0,0,0,0.2);
        }
        .call-button.start {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
        }
        .call-button.start:hover {
            transform: translateY(-2px);
            box-shadow: 0 6px 20px rgba(0,0,0,0.3);
        }
        .call-button.end {
            background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%);
            color: white;
        }
        .call-button:disabled {
            opacity: 0.5;
            cursor: not-allowed;
        }
        .status {
            text-align: center;
            padding: 15px;
            margin: 20px 0;
            border-radius: 10px;
            font-weight: 500;
        }
        .status.ready { background: #e3f2fd; color: #1976d2; }
        .status.connected { background: #e8f5e9; color: #388e3c; }
        .status.error { background: #ffebee; color: #d32f2f; }
        .conversation {
            background: #f5f5f5;
            border-radius: 10px;
            padding: 20px;
            max-height: 400px;
            overflow-y: auto;
            margin: 20px 0;
        }
        .message {
            margin: 10px 0;
            padding: 12px;
            border-radius: 10px;
            animation: slideIn 0.3s;
        }
        @keyframes slideIn {
            from { opacity: 0; transform: translateY(10px); }
            to { opacity: 1; transform: translateY(0); }
        }
        .message.user {
            background: #e3f2fd;
            margin-left: 50px;
        }
        .message.ai {
            background: #f3e5f5;
            margin-right: 50px;
        }
        .message strong {
            display: block;
            margin-bottom: 5px;
            font-size: 12px;
            opacity: 0.7;
        }
        .debug {
            margin-top: 20px;
            padding: 15px;
            background: #263238;
            color: #aed581;
            border-radius: 10px;
            font-family: 'Courier New', monospace;
            font-size: 12px;
            max-height: 200px;
            overflow-y: auto;
        }
        .debug div {
            margin: 5px 0;
            padding: 3px;
        }
        .debug .info { color: #81d4fa; }
        .debug .error { color: #ef5350; }
        .debug .success { color: #aed581; }
    </style>
</head>
<body>
    <div class="container">
        <h1>🎙️ Voice AI Contact Center</h1>
        <p class="subtitle">Free • No Twilio • Browser-Based</p>
        
        <button id="callButton" class="call-button start" onclick="toggleCall()">
            📞 Start Call
        </button>
        
        <div id="status" class="status ready">
            Ready to connect. Click "Start Call" to begin.
        </div>
        
        <div class="conversation" id="conversation">
            <div class="message ai">
                <strong>AI Assistant</strong>
                Welcome! Click "Start Call" and allow microphone access to begin.
            </div>
        </div>
        
        <details>
            <summary style="cursor: pointer; padding: 10px; background: #f5f5f5; border-radius: 5px;">
                🔧 Debug Console
            </summary>
            <div class="debug" id="debug"></div>
        </details>
    </div>

    <script>
        let websocket = null;
        let mediaRecorder = null;
        let isCallActive = false;
        let audioChunks = [];
        let recordingInterval = null;

        function log(message, type = 'info') {
            const debug = document.getElementById('debug');
            const time = new Date().toLocaleTimeString();
            const div = document.createElement('div');
            div.className = type;
            div.textContent = `[${time}] ${message}`;
            debug.appendChild(div);
            debug.scrollTop = debug.scrollHeight;
            console.log(message);
        }

        function updateStatus(message, type = 'ready') {
            const status = document.getElementById('status');
            status.textContent = message;
            status.className = `status ${type}`;
            log(message, type === 'error' ? 'error' : 'info');
        }

        function addMessage(sender, text) {
            const conversation = document.getElementById('conversation');
            const messageDiv = document.createElement('div');
            messageDiv.className = `message ${sender === 'You' ? 'user' : 'ai'}`;
            messageDiv.innerHTML = `<strong>${sender}</strong>${text}`;
            conversation.appendChild(messageDiv);
            conversation.scrollTop = conversation.scrollHeight;
        }

        function updateCallButton() {
            const button = document.getElementById('callButton');
            if (isCallActive) {
                button.textContent = '📞 End Call';
                button.className = 'call-button end';
            } else {
                button.textContent = '📞 Start Call';
                button.className = 'call-button start';
            }
        }

        async function toggleCall() {
            if (isCallActive) {
                endCall();
            } else {
                await startCall();
            }
        }

        async function startCall() {
            try {
                log('🚀 Starting call...', 'info');
                updateStatus('Requesting microphone access...', 'ready');
                
                // Get microphone access FIRST
                log('🎤 Requesting microphone permission...', 'info');
                const stream = await navigator.mediaDevices.getUserMedia({ 
                    audio: {
                        echoCancellation: true,
                        noiseSuppression: true,
                        autoGainControl: true
                    } 
                });
                
                log('✅ Microphone access granted!', 'success');
                updateStatus('Microphone ready, connecting to server...', 'ready');
                
                // Now connect WebSocket
                log('🔌 Connecting WebSocket...', 'info');
                websocket = new WebSocket('ws://localhost:8001/ws/call');
                
                websocket.onopen = function() {
                    log('✅ WebSocket connected!', 'success');
                    updateStatus('Connected to AI Assistant', 'connected');
                    isCallActive = true;
                    updateCallButton();
                    
                    // Start recording
                    startRecording(stream);
                };
                
                websocket.onmessage = function(event) {
                    try {
                        const data = JSON.parse(event.data);
                        log(`📨 Received: ${data.type}`, 'info');
                        handleWebSocketMessage(data);
                    } catch (e) {
                        log(`❌ Error parsing message: ${e}`, 'error');
                    }
                };
                
                websocket.onerror = function(error) {
                    log(`❌ WebSocket error: ${error}`, 'error');
                    updateStatus('Connection error occurred', 'error');
                };
                
                websocket.onclose = function(event) {
                    log(`🔌 WebSocket closed: ${event.code} ${event.reason}`, 'info');
                    updateStatus('Connection closed', 'ready');
                    isCallActive = false;
                    updateCallButton();
                    stopRecording();
                };
                
            } catch (error) {
                log(`❌ Error starting call: ${error.message}`, 'error');
                updateStatus(`Error: ${error.message}`, 'error');
                
                if (error.name === 'NotAllowedError') {
                    alert('Microphone permission denied. Please allow microphone access and try again.');
                } else if (error.name === 'NotFoundError') {
                    alert('No microphone found. Please connect a microphone and try again.');
                }
            }
        }

        function startRecording(stream) {
            try {
                log('🎙️ Starting audio recording...', 'info');
                
                mediaRecorder = new MediaRecorder(stream, {
                    mimeType: 'audio/webm'
                });
                
                mediaRecorder.ondataavailable = function(event) {
                    if (event.data.size > 0) {
                        audioChunks.push(event.data);
                        log(`📼 Audio chunk: ${event.data.size} bytes`, 'info');
                    }
                };
                
                mediaRecorder.onstop = function() {
                    if (audioChunks.length > 0 && websocket && websocket.readyState === WebSocket.OPEN) {
                        sendAudioToServer();
                    }
                    audioChunks = [];
                };
                
                mediaRecorder.start();
                log('✅ Recording started', 'success');
                
                // Record in 3-second chunks
                recordingInterval = setInterval(() => {
                    if (mediaRecorder && mediaRecorder.state === 'recording') {
                        mediaRecorder.stop();
                        mediaRecorder.start();
                    }
                }, 3000);
                
            } catch (error) {
                log(`❌ Recording error: ${error}`, 'error');
            }
        }

        function stopRecording() {
            log('⏹️ Stopping recording...', 'info');
            
            if (recordingInterval) {
                clearInterval(recordingInterval);
                recordingInterval = null;
            }
            
            if (mediaRecorder && mediaRecorder.state !== 'inactive') {
                mediaRecorder.stop();
                mediaRecorder.stream.getTracks().forEach(track => track.stop());
            }
            
            log('✅ Recording stopped', 'success');
        }

        async function sendAudioToServer() {
            try {
                const audioBlob = new Blob(audioChunks, { type: 'audio/webm' });
                const arrayBuffer = await audioBlob.arrayBuffer();
                const audioBytes = new Uint8Array(arrayBuffer);
                const hexString = Array.from(audioBytes)
                    .map(b => b.toString(16).padStart(2, '0'))
                    .join('');
                
                log(`📤 Sending audio: ${hexString.length} chars`, 'info');
                
                websocket.send(JSON.stringify({
                    type: 'audio_data',
                    audio: hexString
                }));
                
                addMessage('You', '🎤 [Audio sent]');
                
            } catch (error) {
                log(`❌ Error sending audio: ${error}`, 'error');
            }
        }

        function handleWebSocketMessage(data) {
            switch (data.type) {
                case 'connected':
                    log(`✅ Call ID: ${data.call_id}`, 'success');
                    addMessage('System', `Connected! Call ID: ${data.call_id.substring(0, 8)}...`);
                    break;
                    
                case 'greeting':
                    addMessage('AI Assistant', data.text);
                    break;
                    
                case 'ai_response':
                    addMessage('AI Assistant', data.text);
                    break;
                    
                case 'audio_received':
                    log(data.message, 'success');
                    break;
                    
                case 'error':
                    log(`❌ ${data.message}`, 'error');
                    updateStatus(`Error: ${data.message}`, 'error');
                    break;
            }
        }

        function endCall() {
            log('📞 Ending call...', 'info');
            
            if (websocket && websocket.readyState === WebSocket.OPEN) {
                websocket.send(JSON.stringify({ type: 'end_call' }));
                websocket.close();
            }
            
            stopRecording();
            
            isCallActive = false;
            updateCallButton();
            updateStatus('Call ended', 'ready');
            log('✅ Call ended', 'success');
        }

        // Initialize
        log('🌐 Page loaded and ready', 'success');
    </script>
</body>
</html>
    """)

@app.get("/api/stats")
async def get_call_stats():
    """Get current call statistics"""
    return {
        "active_calls": len(active_calls),
        "status": "operational"
    }

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy", "service": "webrtc-voice-ai"}

if __name__ == "__main__":
    import uvicorn
    print("\n" + "="*70)
    print("🎙️  WEBRTC VOICE AI CONTACT CENTER - IMPROVED VERSION")
    print("="*70)
    print("\n📡 Server: http://localhost:8001")
    print("🌐 Interface: http://localhost:8001")
    print("📊 Stats: http://localhost:8001/api/stats")
    print("💚 Health: http://localhost:8001/health")
    print("\n✅ Features:")
    print("  • Better error handling")
    print("  • Debug console")
    print("  • Improved UI")
    print("  • Real-time logging")
    print("\n" + "="*70 + "\n")
    
    uvicorn.run(app, host="0.0.0.0", port=8001, log_level="info")
