"""
Twilio Integration for Voice AI
Handles incoming/outgoing calls with real-time audio streaming
"""

from fastapi import FastAPI, WebSocket, Request
from fastapi.responses import Response
from twilio.twiml.voice_response import VoiceResponse, Connect, Stream
from twilio.rest import Client
import asyncio
import base64
import json
import logging
from typing import Optional
import os

logger = logging.getLogger(__name__)

app = FastAPI(title="Voice AI Twilio Server")


class TwilioConfig:
    """Twilio configuration"""
    def __init__(self):
        self.account_sid = os.getenv("TWILIO_ACCOUNT_SID")
        self.auth_token = os.getenv("TWILIO_AUTH_TOKEN")
        self.phone_number = os.getenv("TWILIO_PHONE_NUMBER")
        self.webhook_url = os.getenv("WEBHOOK_BASE_URL")
        
        if not all([self.account_sid, self.auth_token, self.phone_number]):
            raise ValueError("Missing Twilio configuration")
        
        self.client = Client(self.account_sid, self.auth_token)


config = TwilioConfig()


@app.post("/voice/incoming")
async def handle_incoming_call(request: Request):
    """
    Handle incoming phone call
    Returns TwiML to start streaming audio
    """
    form_data = await request.form()
    
    call_sid = form_data.get("CallSid")
    from_number = form_data.get("From")
    to_number = form_data.get("To")
    
    logger.info(f"Incoming call: {call_sid} from {from_number}")
    
    # Create TwiML response
    response = VoiceResponse()
    
    # Greeting
    response.say(
        "Hello! Welcome to our AI assistant. Please wait while I connect you.",
        voice='Polly.Joanna'
    )
    
    # Start audio streaming
    connect = Connect()
    stream = Stream(url=f'wss://{config.webhook_url}/voice/stream')
    stream.parameter(name='CallSid', value=call_sid)
    stream.parameter(name='From', value=from_number)
    connect.append(stream)
    response.append(connect)
    
    return Response(content=str(response), media_type="application/xml")


@app.websocket("/voice/stream")
async def handle_audio_stream(websocket: WebSocket):
    """
    Handle real-time audio streaming from Twilio
    """
    await websocket.accept()
    
    call_sid = None
    from_number = None
    stream_sid = None
    
    logger.info("WebSocket connection established")
    
    try:
        # Import services
        from stt_service import STTService, TranscriptionConfig
        from vad_service import VADService, StreamingVAD
        from conversation_manager import ConversationManager, ConversationContext
        import httpx
        
        # Initialize services
        stt = STTService(TranscriptionConfig(model_size="base"))
        vad = VADService()
        streaming_vad = StreamingVAD(vad)
        
        # Initialize conversation manager
        conversation_manager = ConversationManager(
            api_key=os.getenv("CLAUDE_API_KEY"),
            provider="anthropic"
        )
        
        # Create conversation context
        context = None
        
        # Buffer for audio chunks
        audio_buffer = bytearray()
        
        async for message in websocket.iter_text():
            data = json.loads(message)
            event = data.get('event')
            
            if event == 'start':
                # Stream started
                call_sid = data.get('start', {}).get('callSid')
                stream_sid = data.get('start', {}).get('streamSid')
                from_number = data.get('start', {}).get('customParameters', {}).get('From')
                
                logger.info(f"Stream started: {stream_sid} for call {call_sid}")
                
                # Create conversation context
                context = ConversationContext(
                    conversation_id=call_sid,
                    customer_id=from_number
                )
                
            elif event == 'media':
                # Received audio chunk from caller
                payload = data['media']['payload']
                
                # Decode audio (mulaw base64)
                audio_chunk = base64.b64decode(payload)
                audio_buffer.extend(audio_chunk)
                
                # Check VAD every 100ms worth of audio
                if len(audio_buffer) >= 1600:  # 100ms at 8kHz
                    chunk = bytes(audio_buffer[:1600])
                    audio_buffer = audio_buffer[1600:]
                    
                    # Process with VAD
                    vad_result = streaming_vad.process_chunk(chunk, chunk_duration_ms=100)
                    
                    if vad_result['speech_ended']:
                        # Speech segment ended, transcribe it
                        logger.info("Speech ended, transcribing...")
                        
                        # Transcribe accumulated audio
                        if len(audio_buffer) > 0:
                            transcription = await stt.transcribe_audio(bytes(audio_buffer))
                            user_text = transcription.text
                            
                            logger.info(f"User said: {user_text}")
                            
                            if user_text.strip():
                                # Generate AI response
                                ai_response, functions = await conversation_manager.generate_response(
                                    context,
                                    user_text
                                )
                                
                                logger.info(f"AI response: {ai_response}")
                                
                                # Convert response to speech using TTS API
                                tts_url = os.getenv("TTS_API_URL", "http://localhost:5000")
                                
                                async with httpx.AsyncClient() as client:
                                    tts_response = await client.post(
                                        f"{tts_url}/api/v1/lightning/get_speech",
                                        json={
                                            "text": ai_response,
                                            "voice_id": "en-US-lessac-medium",
                                            "engine": "piper",
                                            "sample_rate": 8000,  # Twilio uses 8kHz
                                            "output_format": "wav"
                                        }
                                    )
                                    
                                    tts_data = tts_response.json()
                                    job_id = tts_data['job_id']
                                    
                                    # Poll for completion
                                    audio_url = await poll_tts_completion(client, tts_url, job_id)
                                    
                                    if audio_url:
                                        # Download audio
                                        audio_response = await client.get(audio_url)
                                        audio_data = audio_response.content
                                        
                                        # Send audio to caller
                                        await send_audio_to_caller(websocket, audio_data, stream_sid)
                            
                            # Clear buffer
                            audio_buffer.clear()
            
            elif event == 'stop':
                # Stream stopped
                logger.info(f"Stream stopped: {stream_sid}")
                break
    
    except Exception as e:
        logger.error(f"WebSocket error: {e}", exc_info=True)
    
    finally:
        await websocket.close()
        logger.info("WebSocket connection closed")


async def poll_tts_completion(client, tts_url: str, job_id: str, timeout: int = 30) -> Optional[str]:
    """Poll TTS API for job completion"""
    import time
    start_time = time.time()
    
    while time.time() - start_time < timeout:
        try:
            response = await client.get(f"{tts_url}/api/v1/jobs/{job_id}")
            data = response.json()
            
            if data['status'] == 'completed':
                return data['result']['audio_url']
            elif data['status'] == 'failed':
                logger.error(f"TTS job failed: {data.get('error')}")
                return None
            
            await asyncio.sleep(0.5)
            
        except Exception as e:
            logger.error(f"Error polling TTS: {e}")
            return None
    
    logger.error(f"TTS job timeout: {job_id}")
    return None


async def send_audio_to_caller(websocket: WebSocket, audio_data: bytes, stream_sid: str):
    """Send audio back to caller via WebSocket"""
    try:
        # Convert audio to mulaw and base64
        # Note: In production, you'd convert PCM to mulaw properly
        audio_base64 = base64.b64encode(audio_data).decode('utf-8')
        
        # Send in chunks (Twilio expects 20ms chunks)
        chunk_size = 320  # 20ms at 8kHz mulaw
        
        for i in range(0, len(audio_base64), chunk_size):
            chunk = audio_base64[i:i + chunk_size]
            
            message = {
                "event": "media",
                "streamSid": stream_sid,
                "media": {
                    "payload": chunk
                }
            }
            
            await websocket.send_text(json.dumps(message))
            await asyncio.sleep(0.02)  # 20ms delay
            
    except Exception as e:
        logger.error(f"Error sending audio: {e}")


@app.post("/voice/outbound")
async def make_outbound_call(request: Request):
    """
    Make an outbound call
    
    Body:
    {
        "to": "+1234567890",
        "message": "Hello, this is a test call"
    }
    """
    data = await request.json()
    to_number = data.get("to")
    message = data.get("message", "Hello, this is an automated call.")
    
    try:
        call = config.client.calls.create(
            to=to_number,
            from_=config.phone_number,
            twiml=f'<Response><Say voice="Polly.Joanna">{message}</Say></Response>'
        )
        
        logger.info(f"Outbound call created: {call.sid}")
        
        return {
            "success": True,
            "call_sid": call.sid,
            "to": to_number
        }
        
    except Exception as e:
        logger.error(f"Outbound call error: {e}")
        return {
            "success": False,
            "error": str(e)
        }


@app.get("/voice/status/{call_sid}")
async def get_call_status(call_sid: str):
    """Get status of a call"""
    try:
        call = config.client.calls(call_sid).fetch()
        
        return {
            "call_sid": call.sid,
            "status": call.status,
            "duration": call.duration,
            "from": call.from_,
            "to": call.to
        }
        
    except Exception as e:
        logger.error(f"Error fetching call status: {e}")
        return {"error": str(e)}


@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy", "service": "twilio-voice-ai"}


if __name__ == "__main__":
    import uvicorn
    
    # Load environment variables
    from dotenv import load_dotenv
    load_dotenv()
    
    # Configure logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    # Run server
    port = int(os.getenv("PORT", 8080))
    
    print(f"""
    ╔══════════════════════════════════════════════════════════╗
    ║       Voice AI Twilio Server                             ║
    ║                                                          ║
    ║  Incoming calls: POST /voice/incoming                    ║
    ║  Audio streaming: WS /voice/stream                       ║
    ║  Outbound calls: POST /voice/outbound                    ║
    ║  Call status: GET /voice/status/:call_sid                ║
    ║                                                          ║
    ║  Configure Twilio webhook:                               ║
    ║  https://your-domain.com/voice/incoming                  ║
    ╚══════════════════════════════════════════════════════════╝
    """)
    
    uvicorn.run(
        app,
        host="0.0.0.0",
        port=port,
        log_level="info"
    )
