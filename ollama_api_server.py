"""
Ollama Voice API Backend
Handles requests from the web UI
"""
from fastapi import FastAPI, HTTPException
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Dict, Optional
from fastapi import UploadFile, File, Form
import asyncio
import sys
import os
from pathlib import Path
import time

# Add engines to path
sys.path.insert(0, os.path.dirname(__file__))

try:
    from tts_engines.engine_manager import get_engine_manager
except ImportError:
    # Fallback to simple TTS for Python 3.13
    print("Warning: Using simple TTS fallback for Python 3.13")
    from simple_tts import get_simple_tts
    get_engine_manager = get_simple_tts

app = FastAPI(title="Ollama Voice API")

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Static files
app.mount("/output", StaticFiles(directory="output"), name="output")
app.mount("/voice_samples", StaticFiles(directory="voice_samples"), name="voice_samples")

# Global state
tts_manager = None
ollama_host = "http://localhost:11434"


class ChatRequest(BaseModel):
    message: str
    model: str = "llama3.2:1b"  # Much faster 1B model
    engine: str = "gtts"   # Use working engine by default
    voice_id: str = "gtts-en"
    history: List[Dict] = []


class ChatResponse(BaseModel):
    success: bool
    response: str
    audio_url: str
    duration: float
    history: List[Dict]
    error: Optional[str] = None


@app.on_event("startup")
async def startup():
    """Initialize TTS engines and pre-warm Ollama model"""
    global tts_manager
    tts_manager = get_engine_manager()
    
    # Initialize engines
    await tts_manager.initialize_engines()
    
    # Pre-warm the default model to keep it loaded
    try:
        import requests
        print("Pre-warming llama3.2:1b model...")
        requests.post(
            f"{ollama_host}/api/generate",
            json={
                "model": "llama3.2:1b",
                "prompt": "Hi",
                "stream": False,
                "options": {"num_predict": 1}
            },
            timeout=30
        )
        print("Model pre-warmed and ready")
    except Exception as e:
        print(f"Warning: Model pre-warm failed: {e}")


@app.get("/")
async def root():
    """Serve the UI"""
    return FileResponse("public/voice-ui.html")


@app.get("/api/v1/health")
async def health_check():
    """Health check endpoint"""
    try:
        # Check Ollama
        import requests
        response = requests.get(f"{ollama_host}/api/tags", timeout=2)
        ollama_status = response.status_code == 200
    except:
        ollama_status = False
    
    return {
        "status": "healthy" if ollama_status else "degraded",
        "ollama": "connected" if ollama_status else "disconnected",
        "tts": "ready" if tts_manager else "initializing"
    }


@app.post("/api/ollama/chat", response_model=ChatResponse)
async def chat(request: ChatRequest):
    """
    Handle chat request:
    1. Send message to Ollama
    2. Convert response to speech
    3. Return audio URL
    """
    try:
        import requests
        
        # Prepare conversation history
        history = request.history.copy()
        history.append({
            "role": "user",
            "content": request.message
        })
        
        print(f"\n💬 User: {request.message}")
        print(f"🤖 Model: {request.model}")
        print(f"⏳ Sending to Ollama... (this may take a few minutes)")
        
        # Call Ollama with optimized settings for speed
        start_time = time.time()
        ollama_response = requests.post(
            f"{ollama_host}/api/chat",
            json={
                "model": request.model,
                "messages": history,
                "stream": False,
                "options": {
                    "temperature": 0.3,     # Lower for faster, more focused responses
                    "top_p": 0.8,
                    "num_predict": 30,     # Even shorter responses
                    "num_ctx": 512,       # Minimal context for speed
                    "num_thread": -1,     # Use all available CPU threads
                    "repeat_penalty": 1.1,
                    "seed": -1
                }
            },
            timeout=60  # Increased to 60 seconds for 1b model
        )
        
        if ollama_response.status_code != 200:
            raise HTTPException(
                status_code=500,
                detail=f"Ollama error: {ollama_response.status_code}"
            )
        
        result = ollama_response.json()
        assistant_message = result['message']['content']
        
        ollama_time = time.time() - start_time
        print(f"✅ Ollama response in {ollama_time:.1f}s")
        print(f"🗣️  Response: {assistant_message[:100]}...")
        
        # Check if response is too long for TTS
        if len(assistant_message) > 1000:
            print(f"⚠️  Long response ({len(assistant_message)} chars) - TTS may take longer")
        
        # Add to history
        history.append({
            "role": "assistant",
            "content": assistant_message
        })
        
        # Convert to speech
        # Smart engine and voice selection
        available_engines = list(tts_manager.engines.keys())
        voice_id = request.voice_id
        
        # Determine engine based on voice ID
        if voice_id.startswith("gtts-"):
            selected_engine = "gtts"
        elif voice_id == "system":
            selected_engine = "system"
        elif voice_id.endswith("Neural"):
            selected_engine = "edge"
        else:
            # Fallback to requested engine or first available
            selected_engine = request.engine if request.engine in available_engines else available_engines[0]
            # Adjust voice for fallback engine
            if selected_engine == "gtts":
                voice_id = "gtts-en"
            elif selected_engine == "system":
                voice_id = "system"
            elif selected_engine == "edge":
                voice_id = "en-US-AriaNeural"
        
        print(f"🎙️  Generating speech with {selected_engine} ({voice_id})...")
        timestamp = int(time.time() * 1000)
        output_filename = f"chat_{timestamp}.wav"
        output_path = f"./output/{output_filename}"
        
        tts_start = time.time()
        
        # Try engines in order of reliability: gtts (most reliable), system (offline), edge (can fail)
        engines_to_try = []
        if selected_engine in available_engines:
            engines_to_try.append(selected_engine)
        
        # Add fallback engines in priority order
        for fallback in ["gtts", "system", "edge"]:
            if fallback in available_engines and fallback not in engines_to_try:
                engines_to_try.append(fallback)
        
        tts_result = None
        for engine in engines_to_try:
            try:
                # Adjust voice ID for engine if needed
                if engine == "gtts" and not voice_id.startswith("gtts-"):
                    voice_id = "gtts-en"
                elif engine == "system":
                    voice_id = "system"
                elif engine == "edge" and not voice_id.endswith("Neural"):
                    voice_id = "en-US-AriaNeural"
                
                print(f"🎙️  Trying {engine} engine...")
                tts_result = await tts_manager.synthesize(
                    text=assistant_message,
                    voice_id=voice_id,
                    output_path=output_path,
                    engine=engine,
                    sample_rate=24000
                )
                print(f"✅ {engine} TTS succeeded")
                break
            except Exception as e:
                print(f"⚠️  {engine} TTS failed: {e}")
                continue
        
        if not tts_result:
            raise Exception("All TTS engines failed")
        
        tts_time = time.time() - tts_start
        print(f"✅ TTS generated in {tts_time:.1f}s")
        
        total_time = time.time() - start_time
        print(f"⚡ Total time: {total_time:.1f}s\n")
        
        return ChatResponse(
            success=True,
            response=assistant_message,
            audio_url=f"/output/{output_filename}",
            duration=tts_result['audio_duration'],
            history=history
        )
        
    except requests.exceptions.Timeout:
        raise HTTPException(status_code=504, detail="Ollama request timeout (60 seconds) - model may be loading or system overloaded")
    except Exception as e:
        print(f"❌ Error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/models")
async def get_models():
    """Get available Ollama models"""
    try:
        import requests
        response = requests.get(f"{ollama_host}/api/tags", timeout=10)
        
        if response.status_code == 200:
            models = response.json().get('models', [])
            return {
                "models": [
                    {
                        "name": m['name'],
                        "size": m.get('size', 0)
                    }
                    for m in models
                ]
            }
        else:
            return {"models": []}
    except:
        return {"models": []}


@app.get("/api/voices")
async def get_voices():
    """Get available TTS voices"""
    if not tts_manager:
        return {"voices": []}
    
    voices = tts_manager.get_available_voices()
    return {"voices": voices}


@app.post("/api/speech-to-text")
async def speech_to_text(file: UploadFile = File(...)):
    """Convert speech to text"""
    try:
        # Save uploaded file with original extension
        timestamp = int(time.time() * 1000)
        file_ext = ".webm" if file.filename and ".webm" in file.filename else ".wav"
        temp_path = f"uploads/temp_audio_{timestamp}{file_ext}"
        
        os.makedirs("uploads", exist_ok=True)
        
        with open(temp_path, "wb") as f:
            contents = await file.read()
            f.write(contents)
        
        print(f"Processing audio file: {temp_path} ({len(contents)} bytes)")
        
        # Try to use speech recognition with WebM support
        try:
            import speech_recognition as sr
            
            recognizer = sr.Recognizer()
            recognizer.energy_threshold = 300
            recognizer.dynamic_energy_threshold = True
            
            # Handle WebM files with pydub + FFmpeg conversion
            if file_ext == ".webm":
                print("Converting WebM to WAV using FFmpeg...")
                try:
                    from pydub import AudioSegment
                    import io
                    
                    # Load WebM and convert to WAV
                    audio = AudioSegment.from_file(temp_path, format="webm")
                    wav_io = io.BytesIO()
                    audio.export(wav_io, format="wav")
                    wav_io.seek(0)
                    
                    # Process with speech recognition
                    with sr.AudioFile(wav_io) as source:
                        recognizer.adjust_for_ambient_noise(source, duration=0.5)
                        audio_data = recognizer.record(source)
                    print("WebM converted and processed successfully")
                    
                except Exception as webm_error:
                    print(f"WebM conversion failed: {webm_error}")
                    raise Exception(f"WebM processing failed: {webm_error}")
            else:
                # Process WAV/other formats directly
                try:
                    with sr.AudioFile(temp_path) as source:
                        recognizer.adjust_for_ambient_noise(source, duration=0.5)
                        audio_data = recognizer.record(source)
                    print("Audio processed successfully")
                except Exception as audio_error:
                    print(f"Audio processing failed: {audio_error}")
                    raise Exception(f"Audio file processing failed: {audio_error}")
            
            print("Sending to Google Speech Recognition...")
            text = recognizer.recognize_google(audio_data, language='en-US')
            
            # Clean up temp file
            if os.path.exists(temp_path):
                os.remove(temp_path)
            
            print(f"Recognized text: {text}")
            
            return {
                "success": True,
                "text": text,
                "error": None
            }
            
        except sr.UnknownValueError:
            if os.path.exists(temp_path):
                os.remove(temp_path)
            return {
                "success": False,
                "text": "",
                "error": "Could not understand audio. Please speak clearly and try again."
            }
        except sr.RequestError as e:
            if os.path.exists(temp_path):
                os.remove(temp_path)
            return {
                "success": False,
                "text": "",
                "error": f"Speech recognition service error: {str(e)}"
            }
        except ImportError as e:
            if os.path.exists(temp_path):
                os.remove(temp_path)
            return {
                "success": False,
                "text": "",
                "error": "Speech recognition not available. Install: pip install SpeechRecognition pydub"
            }
        except Exception as e:
            if os.path.exists(temp_path):
                os.remove(temp_path)
            return {
                "success": False,
                "text": "",
                "error": f"Recognition failed: {str(e)}. Try using WAV format or install pydub for WebM support."
            }
            
    except Exception as e:
        return {
            "success": False,
            "text": "",
            "error": f"Upload error: {str(e)}"
        }




@app.post("/api/voice-clone")
async def voice_clone(file: UploadFile = File(...), text: str = Form(""), voice_name: str = Form("")):
    """Clone a voice from uploaded sample"""
    try:
        # Create directories
        os.makedirs("voice_samples", exist_ok=True)
        os.makedirs("output", exist_ok=True)
        
        # Generate voice name if not provided
        timestamp = int(time.time() * 1000)
        if not voice_name:
            voice_name = f"voice_{timestamp}"
        
        # Save uploaded voice sample
        sample_path = f"voice_samples/{voice_name}.wav"
        
        with open(sample_path, "wb") as f:
            contents = await file.read()
            f.write(contents)
        
        print(f"Voice sample saved: {voice_name} ({len(contents)} bytes)")
        
        # If text provided, try voice cloning
        if text:
            output_path = f"output/cloned_{voice_name}_{timestamp}.wav"
            
            # Try advanced voice cloning first
            try:
                from TTS.api import TTS
                print("Using Coqui TTS for voice cloning...")
                
                tts = TTS("tts_models/multilingual/multi-dataset/xtts_v2")
                tts.tts_to_file(
                    text=text,
                    speaker_wav=sample_path,
                    language="en",
                    file_path=output_path
                )
                
                return {
                    "success": True,
                    "voice_id": voice_name,
                    "audio_url": f"/output/cloned_{voice_name}_{timestamp}.wav",
                    "method": "coqui_xtts",
                    "message": f"Voice cloned successfully using Coqui TTS! Sample: '{voice_name}'"
                }
                
            except ImportError:
                print("Coqui TTS not available, using fallback...")
                # Fallback to regular TTS
                try:
                    import gtts
                    tts = gtts.gTTS(text=text, lang='en')
                    tts.save(output_path)
                    
                    return {
                        "success": False,
                        "voice_id": voice_name,
                        "audio_url": f"/output/cloned_{voice_name}_{timestamp}.wav",
                        "method": "gtts_fallback",
                        "message": f"Voice cloning failed: Advanced TTS not available. Voice sample saved as '{voice_name}' but cannot clone voice characteristics. Install 'pip install TTS torch torchaudio' for true voice cloning."
                    }
                    
                except Exception as e:
                    print(f"Fallback TTS failed: {e}")
                    return {
                        "success": True,
                        "voice_id": voice_name,
                        "message": f"Voice sample '{voice_name}' saved! Note: For true voice cloning, install Visual C++ Build Tools and run 'pip install TTS'."
                    }
                    
            except Exception as e:
                print(f"Advanced TTS failed: {e}")
                # Try fallback
                try:
                    import gtts
                    tts = gtts.gTTS(text=text, lang='en')
                    tts.save(output_path)
                    
                    return {
                        "success": False,
                        "voice_id": voice_name,
                        "audio_url": f"/output/cloned_{voice_name}_{timestamp}.wav",
                        "method": "gtts_fallback",
                        "message": f"Voice cloning failed: Cannot clone voice characteristics. Voice sample saved but using generic TTS. Install Coqui TTS for true voice cloning."
                    }
                except Exception as e2:
                    return {
                        "success": True,
                        "voice_id": voice_name,
                        "message": f"Voice sample saved but TTS failed: {str(e2)}"
                    }
        else:
            # Just save the sample
            return {
                "success": True,
                "voice_id": voice_name,
                "message": f"Voice sample '{voice_name}' uploaded successfully!"
            }
            
    except Exception as e:
        print(f"Voice cloning error: {e}")
        return {
            "success": False,
            "error": f"Voice cloning failed: {str(e)}"
        }


@app.get("/api/voice-samples")
async def get_voice_samples():
    """Get list of uploaded voice samples"""
    try:
        samples = []
        voice_dir = "voice_samples"
        
        if os.path.exists(voice_dir):
            for file in os.listdir(voice_dir):
                if file.endswith('.wav'):
                    voice_id = file[:-4]  # Remove .wav
                    file_path = os.path.join(voice_dir, file)
                    samples.append({
                        "voice_id": voice_id,
                        "file_size": os.path.getsize(file_path),
                        "created": os.path.getctime(file_path)
                    })
        
        return {"samples": samples}
        
    except Exception as e:
        return {"samples": [], "error": str(e)}


if __name__ == "__main__":
    import uvicorn
    
    print("\n" + "="*60)
    print("OLLAMA VOICE API SERVER")
    print("="*60)
    print(f"\nAPI: http://localhost:8000")
    print(f"UI:  http://localhost:8000")
    print(f"Docs: http://localhost:8000/docs")
    print("\nMake sure Ollama is running:")
    print("  ollama serve")
    print("\n" + "="*60 + "\n")
    
    uvicorn.run(
        app,
        host="0.0.0.0",
        port=8000,
        log_level="info"
    )
