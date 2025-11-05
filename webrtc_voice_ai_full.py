#!/usr/bin/env python3
"""
WebRTC Voice AI Contact Center - FULL AI VERSION
With Speech Recognition, Ollama AI, and Text-to-Speech
"""

from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.responses import HTMLResponse
from fastapi.middleware.cors import CORSMiddleware
import json
import uuid
from datetime import datetime
import logging
import io
import wave
import base64
import asyncio
import aiohttp

# Speech Recognition
try:
    import speech_recognition as sr
    SPEECH_RECOGNITION_AVAILABLE = True
except ImportError:
    SPEECH_RECOGNITION_AVAILABLE = False
    print("⚠️  speech_recognition not installed. Install with: pip install SpeechRecognition")

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(title="WebRTC Voice AI Contact Center - Full AI")

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

class AIVoiceCall:
    def __init__(self, call_id: str, websocket: WebSocket):
        self.call_id = call_id
        self.websocket = websocket
        self.start_time = datetime.now()
        self.conversation_history = []
        self.is_active = True
        
    async def process_audio(self, audio_hex: str):
        """Process audio: STT -> AI -> TTS"""
        try:
            # Step 1: Convert hex to audio bytes
            audio_bytes = bytes.fromhex(audio_hex)
            logger.info(f"🎤 Processing {len(audio_bytes)} bytes of audio")
            
            # Step 2: Speech-to-Text
            transcription = await self.speech_to_text(audio_bytes)
            
            if not transcription or transcription.strip() == "":
                logger.info("🔇 No speech detected in audio")
                return
            
            logger.info(f"📝 Transcription: {transcription}")
            
            await self.websocket.send_json({
                "type": "transcription",
                "text": transcription,
                "timestamp": datetime.now().isoformat()
            })
            
            # Step 3: Get AI Response
            ai_response = await self.get_ai_response(transcription)
            logger.info(f"🤖 AI Response: {ai_response}")
            
            await self.websocket.send_json({
                "type": "ai_response",
                "text": ai_response,
                "timestamp": datetime.now().isoformat()
            })
            
            # Step 4: Text-to-Speech
            audio_url = await self.text_to_speech(ai_response)
            
            if audio_url:
                logger.info(f"🔊 TTS Audio ready: {audio_url}")
                await self.websocket.send_json({
                    "type": "audio_response",
                    "audio_url": audio_url,
                    "timestamp": datetime.now().isoformat()
                })
            
        except Exception as e:
            logger.error(f"❌ Error processing audio: {e}", exc_info=True)
            await self.websocket.send_json({
                "type": "error",
                "message": f"Processing error: {str(e)}"
            })
    
    async def speech_to_text(self, audio_bytes: bytes) -> str:
        """Convert speech to text using speech_recognition"""
        try:
            if not SPEECH_RECOGNITION_AVAILABLE:
                return "Speech recognition not available"
            
            recognizer = sr.Recognizer()
            
            # Convert webm to wav format that speech_recognition can handle
            # For now, we'll use the audio directly
            audio_data = sr.AudioData(audio_bytes, 48000, 2)
            
            try:
                # Use Google's free speech recognition
                text = recognizer.recognize_google(audio_data)
                return text
            except sr.UnknownValueError:
                logger.info("Could not understand audio")
                return ""
            except sr.RequestError as e:
                logger.error(f"Speech recognition error: {e}")
                return ""
                
        except Exception as e:
            logger.error(f"STT error: {e}")
            return ""
    
    async def get_ai_response(self, user_message: str) -> str:
        """Get AI response from Ollama"""
        try:
            async with aiohttp.ClientSession() as session:
                # Add to conversation history
                self.conversation_history.append({
                    "role": "user",
                    "content": user_message
                })
                
                # Call Ollama API
                payload = {
                    "model": "llama3.2:1b",
                    "messages": self.conversation_history,
                    "stream": False
                }
                
                async with session.post(
                    "http://localhost:11434/api/chat",
                    json=payload,
                    timeout=aiohttp.ClientTimeout(total=30)
                ) as response:
                    if response.status == 200:
                        data = await response.json()
                        ai_message = data.get("message", {}).get("content", "I apologize, I couldn't generate a response.")
                        
                        # Add to history
                        self.conversation_history.append({
                            "role": "assistant",
                            "content": ai_message
                        })
                        
                        return ai_message
                    else:
                        logger.error(f"Ollama API error: {response.status}")
                        return "I'm having trouble connecting to my AI brain right now."
                        
        except asyncio.TimeoutError:
            logger.error("Ollama API timeout")
            return "Sorry, I'm taking too long to think. Please try again."
        except Exception as e:
            logger.error(f"AI response error: {e}")
            return f"I'm having technical difficulties: {str(e)}"
    
    async def text_to_speech(self, text: str) -> str:
        """Convert text to speech using the TTS server"""
        try:
            async with aiohttp.ClientSession() as session:
                # Call TTS API on port 8000
                payload = {
                    "text": text,
                    "engine": "gtts",
                    "voice_id": "gtts-en"
                }
                
                async with session.post(
                    "http://localhost:8000/api/v1/tts/generate",
                    json=payload,
                    timeout=aiohttp.ClientTimeout(total=30)
                ) as response:
                    if response.status == 200:
                        data = await response.json()
                        audio_url = data.get("audio_url")
                        if audio_url:
                            # Make sure URL is accessible
                            if not audio_url.startswith("http"):
                                audio_url = f"http://localhost:8000{audio_url}"
                            return audio_url
                    
                    logger.error(f"TTS API error: {response.status}")
                    return None
                    
        except Exception as e:
            logger.error(f"TTS error: {e}")
            return None

@app.websocket("/ws/call")
async def websocket_call_endpoint(websocket: WebSocket):
    """WebSocket endpoint for voice calls"""
    call_id = str(uuid.uuid4())
    
    try:
        await websocket.accept()
        call = AIVoiceCall(call_id, websocket)
        active_calls[call_id] = call
        
        logger.info(f"✅ Call connected: {call_id}")
        
        # Send connection confirmation
        await websocket.send_json({
            "type": "connected",
            "call_id": call_id,
            "message": "Connected to AI Voice Assistant!",
            "timestamp": datetime.now().isoformat()
        })
        
        # Send greeting
        greeting = "Hello! I'm your AI voice assistant. I can hear you, understand you, and respond with my voice. What would you like to talk about?"
        
        await websocket.send_json({
            "type": "greeting",
            "text": greeting,
            "timestamp": datetime.now().isoformat()
        })
        
        # Generate TTS for greeting
        greeting_audio = await call.text_to_speech(greeting)
        if greeting_audio:
            await websocket.send_json({
                "type": "audio_response",
                "audio_url": greeting_audio,
                "timestamp": datetime.now().isoformat()
            })
        
        # Handle incoming messages
        while True:
            try:
                data = await websocket.receive_json()
                
                if data["type"] == "audio_data":
                    # Process audio through full AI pipeline
                    audio_hex = data.get("audio", "")
                    if audio_hex:
                        await call.process_audio(audio_hex)
                    
                elif data["type"] == "end_call":
                    logger.info(f"📞 Call ended by user: {call_id}")
                    break
                    
                elif data["type"] == "ping":
                    await websocket.send_json({"type": "pong"})
                    
            except json.JSONDecodeError as e:
                logger.error(f"❌ JSON decode error: {e}")
                
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
    """Serve the full AI voice interface"""
    return HTMLResponse(content="""
<!DOCTYPE html>
<html>
<head>
    <title>AI Voice Assistant</title>
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
            max-width: 900px;
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
        .badge {
            display: inline-block;
            padding: 5px 15px;
            margin: 0 5px;
            border-radius: 20px;
            font-size: 12px;
            font-weight: bold;
        }
        .badge.stt { background: #e3f2fd; color: #1976d2; }
        .badge.ai { background: #f3e5f5; color: #7b1fa2; }
        .badge.tts { background: #e8f5e9; color: #388e3c; }
        
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
        
        .status {
            text-align: center;
            padding: 15px;
            margin: 20px 0;
            border-radius: 10px;
            font-weight: 500;
        }
        .status.ready { background: #e3f2fd; color: #1976d2; }
        .status.connected { background: #e8f5e9; color: #388e3c; }
        .status.processing { background: #fff3e0; color: #f57c00; }
        .status.error { background: #ffebee; color: #d32f2f; }
        
        .conversation {
            background: #f5f5f5;
            border-radius: 10px;
            padding: 20px;
            max-height: 500px;
            overflow-y: auto;
            margin: 20px 0;
        }
        .message {
            margin: 15px 0;
            padding: 15px;
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
        .message.system {
            background: #fff3e0;
            text-align: center;
            margin: 10px 50px;
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
        .debug .processing { color: #ffb74d; }
    </style>
</head>
<body>
    <div class="container">
        <h1>🎙️ AI Voice Assistant</h1>
        <p class="subtitle">
            <span class="badge stt">🎤 Speech Recognition</span>
            <span class="badge ai">🤖 AI Powered</span>
            <span class="badge tts">🔊 Voice Response</span>
        </p>
        
        <button id="callButton" class="call-button start" onclick="toggleCall()">
            📞 Start Talking
        </button>
        
        <div id="status" class="status ready">
            Ready to talk. Click "Start Talking" and allow microphone access.
        </div>
        
        <div class="conversation" id="conversation">
            <div class="message system">
                <strong>System</strong>
                Welcome! This AI assistant can:<br>
                • Listen to your voice<br>
                • Understand what you say<br>
                • Generate intelligent responses<br>
                • Speak back to you<br><br>
                Click "Start Talking" to begin!
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
        }

        function addMessage(sender, text, type = 'ai') {
            const conversation = document.getElementById('conversation');
            const messageDiv = document.createElement('div');
            messageDiv.className = `message ${type}`;
            messageDiv.innerHTML = `<strong>${sender}</strong>${text}`;
            conversation.appendChild(messageDiv);
            conversation.scrollTop = conversation.scrollHeight;
        }

        function updateCallButton() {
            const button = document.getElementById('callButton');
            if (isCallActive) {
                button.textContent = '📞 Stop Talking';
                button.className = 'call-button end';
            } else {
                button.textContent = '📞 Start Talking';
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
                log('🚀 Starting AI voice session...', 'info');
                updateStatus('Requesting microphone access...', 'ready');
                
                const stream = await navigator.mediaDevices.getUserMedia({ 
                    audio: {
                        echoCancellation: true,
                        noiseSuppression: true,
                        autoGainControl: true
                    } 
                });
                
                log('✅ Microphone access granted!', 'success');
                updateStatus('Connecting to AI assistant...', 'ready');
                
                websocket = new WebSocket('ws://localhost:8001/ws/call');
                
                websocket.onopen = function() {
                    log('✅ Connected to AI assistant!', 'success');
                    updateStatus('🎤 Listening... Start speaking!', 'connected');
                    isCallActive = true;
                    updateCallButton();
                    startRecording(stream);
                };
                
                websocket.onmessage = function(event) {
                    try {
                        const data = JSON.parse(event.data);
                        handleWebSocketMessage(data);
                    } catch (e) {
                        log(`❌ Error parsing message: ${e}`, 'error');
                    }
                };
                
                websocket.onerror = function(error) {
                    log(`❌ WebSocket error`, 'error');
                    updateStatus('Connection error occurred', 'error');
                };
                
                websocket.onclose = function() {
                    log(`🔌 Disconnected from AI assistant`, 'info');
                    updateStatus('Connection closed', 'ready');
                    isCallActive = false;
                    updateCallButton();
                    stopRecording();
                };
                
            } catch (error) {
                log(`❌ Error: ${error.message}`, 'error');
                updateStatus(`Error: ${error.message}`, 'error');
                
                if (error.name === 'NotAllowedError') {
                    alert('Microphone permission denied. Please allow microphone access.');
                }
            }
        }

        function startRecording(stream) {
            try {
                mediaRecorder = new MediaRecorder(stream, { mimeType: 'audio/webm' });
                
                mediaRecorder.ondataavailable = function(event) {
                    if (event.data.size > 0) {
                        audioChunks.push(event.data);
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
            if (recordingInterval) {
                clearInterval(recordingInterval);
                recordingInterval = null;
            }
            
            if (mediaRecorder && mediaRecorder.state !== 'inactive') {
                mediaRecorder.stop();
                mediaRecorder.stream.getTracks().forEach(track => track.stop());
            }
        }

        async function sendAudioToServer() {
            try {
                const audioBlob = new Blob(audioChunks, { type: 'audio/webm' });
                const arrayBuffer = await audioBlob.arrayBuffer();
                const audioBytes = new Uint8Array(arrayBuffer);
                const hexString = Array.from(audioBytes)
                    .map(b => b.toString(16).padStart(2, '0'))
                    .join('');
                
                log(`📤 Sending audio for processing...`, 'processing');
                updateStatus('🤖 Processing your voice...', 'processing');
                
                websocket.send(JSON.stringify({
                    type: 'audio_data',
                    audio: hexString
                }));
                
            } catch (error) {
                log(`❌ Error sending audio: ${error}`, 'error');
            }
        }

        function handleWebSocketMessage(data) {
            switch (data.type) {
                case 'connected':
                    log(`✅ Session ID: ${data.call_id}`, 'success');
                    break;
                    
                case 'greeting':
                    addMessage('AI Assistant', data.text, 'ai');
                    log('👋 AI sent greeting', 'success');
                    break;
                    
                case 'transcription':
                    addMessage('You said', `"${data.text}"`, 'user');
                    log(`📝 Transcribed: ${data.text}`, 'success');
                    updateStatus('🤖 AI is thinking...', 'processing');
                    break;
                    
                case 'ai_response':
                    addMessage('AI Assistant', data.text, 'ai');
                    log(`🤖 AI responded`, 'success');
                    updateStatus('🎤 Listening... Keep talking!', 'connected');
                    break;
                    
                case 'audio_response':
                    log(`🔊 Playing AI voice response`, 'success');
                    playAudio(data.audio_url);
                    break;
                    
                case 'error':
                    log(`❌ ${data.message}`, 'error');
                    updateStatus(`Error: ${data.message}`, 'error');
                    break;
            }
        }

        function playAudio(audioUrl) {
            try {
                const audio = new Audio(audioUrl);
                audio.play().catch(e => {
                    log(`⚠️ Audio playback issue: ${e.message}`, 'error');
                });
            } catch (e) {
                log(`❌ Error playing audio: ${e}`, 'error');
            }
        }

        function endCall() {
            log('📞 Ending session...', 'info');
            
            if (websocket && websocket.readyState === WebSocket.OPEN) {
                websocket.send(JSON.stringify({ type: 'end_call' }));
                websocket.close();
            }
            
            stopRecording();
            isCallActive = false;
            updateCallButton();
            updateStatus('Session ended', 'ready');
            log('✅ Session ended', 'success');
        }

        log('🌐 AI Voice Assistant ready', 'success');
    </script>
</body>
</html>
    """)

@app.get("/api/stats")
async def get_call_stats():
    """Get current call statistics"""
    return {
        "active_calls": len(active_calls),
        "status": "operational",
        "features": {
            "speech_recognition": SPEECH_RECOGNITION_AVAILABLE,
            "ai_enabled": True,
            "tts_enabled": True
        }
    }

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "service": "webrtc-voice-ai-full",
        "speech_recognition": SPEECH_RECOGNITION_AVAILABLE
    }

if __name__ == "__main__":
    import uvicorn
    
    print("\n" + "="*70)
    print("🎙️  AI VOICE ASSISTANT - FULL VERSION")
    print("="*70)
    print("\n✨ Features:")
    print("  🎤 Speech Recognition (Google)")
    print("  🤖 AI Responses (Ollama)")
    print("  🔊 Voice Synthesis (TTS)")
    print(f"\n📊 Status:")
    print(f"  Speech Recognition: {'✅ Available' if SPEECH_RECOGNITION_AVAILABLE else '❌ Not Available'}")
    print(f"  AI Backend: ✅ Ollama (port 11434)")
    print(f"  TTS Backend: ✅ TTS Server (port 8000)")
    print("\n📡 Server: http://localhost:8001")
    print("🌐 Interface: http://localhost:8001")
    print("\n" + "="*70 + "\n")
    
    if not SPEECH_RECOGNITION_AVAILABLE:
        print("⚠️  WARNING: Install speech recognition:")
        print("   pip install SpeechRecognition\n")
    
    uvicorn.run(app, host="0.0.0.0", port=8001, log_level="info")
