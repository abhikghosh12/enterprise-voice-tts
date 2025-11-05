#!/usr/bin/env python3
"""
WebRTC Voice AI - FIXED VERSION
Uses correct endpoints and proper audio handling
"""

from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.responses import HTMLResponse
from fastapi.middleware.cors import CORSMiddleware
import json
import uuid
from datetime import datetime
import logging
import asyncio
import aiohttp
import os
import tempfile

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(title="WebRTC Voice AI - Fixed")

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
            
            # Step 2: Save audio to temporary file and upload to STT endpoint
            transcription = await self.speech_to_text_via_api(audio_bytes)
            
            if not transcription or transcription.strip() == "":
                logger.info("🔇 No speech detected in audio")
                return
            
            logger.info(f"📝 Transcription: {transcription}")
            
            await self.websocket.send_json({
                "type": "transcription",
                "text": transcription,
                "timestamp": datetime.now().isoformat()
            })
            
            # Step 3: Get AI Response from Ollama
            ai_response = await self.get_ai_response(transcription)
            logger.info(f"🤖 AI Response: {ai_response}")
            
            await self.websocket.send_json({
                "type": "ai_response",
                "text": ai_response,
                "timestamp": datetime.now().isoformat()
            })
            
            # Step 4: Text-to-Speech using the chat endpoint
            audio_url = await self.text_to_speech_via_chat(ai_response)
            
            if audio_url:
                logger.info(f"🔊 TTS Audio ready: {audio_url}")
                await self.websocket.send_json({
                    "type": "audio_response",
                    "audio_url": f"http://localhost:8000{audio_url}",
                    "timestamp": datetime.now().isoformat()
                })
            
        except Exception as e:
            logger.error(f"❌ Error processing audio: {e}", exc_info=True)
            await self.websocket.send_json({
                "type": "error",
                "message": f"Processing error: {str(e)}"
            })
    
    async def speech_to_text_via_api(self, audio_bytes: bytes) -> str:
        """Convert speech to text by uploading to TTS server's STT endpoint"""
        try:
            # Create temporary file
            with tempfile.NamedTemporaryFile(suffix='.webm', delete=False) as temp_file:
                temp_file.write(audio_bytes)
                temp_path = temp_file.name
            
            try:
                async with aiohttp.ClientSession() as session:
                    # Upload file to STT endpoint
                    data = aiohttp.FormData()
                    data.add_field('file',
                                   open(temp_path, 'rb'),
                                   filename='audio.webm',
                                   content_type='audio/webm')
                    
                    async with session.post(
                        "http://localhost:8000/api/speech-to-text",
                        data=data,
                        timeout=aiohttp.ClientTimeout(total=30)
                    ) as response:
                        if response.status == 200:
                            result = await response.json()
                            if result.get('success'):
                                return result.get('text', '')
                            else:
                                logger.error(f"STT error: {result.get('error')}")
                                return ""
                        else:
                            logger.error(f"STT API error: {response.status}")
                            return ""
            finally:
                # Clean up temp file
                if os.path.exists(temp_path):
                    os.remove(temp_path)
                    
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
                
                # Call Ollama API directly
                payload = {
                    "model": "llama3.2:1b",
                    "messages": self.conversation_history,
                    "stream": False,
                    "options": {
                        "temperature": 0.7,
                        "num_predict": 50  # Short responses for voice
                    }
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
                        return "I'm having trouble connecting right now."
                        
        except asyncio.TimeoutError:
            logger.error("Ollama API timeout")
            return "Sorry, I'm taking too long to think."
        except Exception as e:
            logger.error(f"AI response error: {e}")
            return f"I'm having technical difficulties."
    
    async def text_to_speech_via_chat(self, text: str) -> str:
        """Convert text to speech using the /api/ollama/chat endpoint"""
        try:
            async with aiohttp.ClientSession() as session:
                # Use the chat endpoint which includes TTS
                payload = {
                    "message": text,
                    "model": "llama3.2:1b",
                    "engine": "gtts",
                    "voice_id": "gtts-en",
                    "history": []  # Empty history for TTS only
                }
                
                async with session.post(
                    "http://localhost:8000/api/ollama/chat",
                    json=payload,
                    timeout=aiohttp.ClientTimeout(total=30)
                ) as response:
                    if response.status == 200:
                        data = await response.json()
                        if data.get('success'):
                            return data.get('audio_url')
                    
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
        greeting = "Hello! I'm your AI voice assistant. Start speaking and I'll respond!"
        
        await websocket.send_json({
            "type": "greeting",
            "text": greeting,
            "timestamp": datetime.now().isoformat()
        })
        
        # Generate TTS for greeting
        greeting_audio = await call.text_to_speech_via_chat(greeting)
        if greeting_audio:
            await websocket.send_json({
                "type": "audio_response",
                "audio_url": f"http://localhost:8000{greeting_audio}",
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
    """Serve the interface - reusing from v2"""
    return HTMLResponse(content=open('webrtc_voice_center_v2.py').read().split('"""')[4])

@app.get("/api/stats")
async def get_call_stats():
    return {"active_calls": len(active_calls), "status": "operational"}

@app.get("/health")
async def health_check():
    return {"status": "healthy", "service": "webrtc-voice-ai-fixed"}

if __name__ == "__main__":
    import uvicorn
    
    print("\n" + "="*70)
    print("🎙️  AI VOICE ASSISTANT - FIXED VERSION")
    print("="*70)
    print("\n✨ Features:")
    print("  🎤 Speech Recognition (via TTS Server API)")
    print("  🤖 AI Responses (Ollama llama3.2:1b)")  
    print("  🔊 Voice Synthesis (Google TTS)")
    print("\n📋 Requirements:")
    print("  ✅ TTS Server running on port 8000")
    print("  ✅ Ollama running on port 11434")
    print("  ✅ Install: pip install aiohttp pydub")
    print("\n📡 Server: http://localhost:8001")
    print("\n" + "="*70 + "\n")
    
    uvicorn.run(app, host="0.0.0.0", port=8001, log_level="info")
