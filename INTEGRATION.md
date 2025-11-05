# Integration Guide

## API Endpoints

### 1. Chat with Voice Response
```http
POST /api/ollama/chat
Content-Type: application/json

{
  "message": "Hello, how are you?",
  "model": "llama3.2:1b",
  "engine": "gtts",
  "voice_id": "gtts-en"
}
```

**Response:**
```json
{
  "success": true,
  "response": "I'm doing well, thank you!",
  "audio_url": "/output/chat_123456789.wav",
  "duration": 2.5
}
```

### 2. Speech-to-Text
```http
POST /api/speech-to-text
Content-Type: multipart/form-data

file: audio.wav
```

**Response:**
```json
{
  "success": true,
  "text": "Hello world",
  "error": null
}
```

### 3. Voice Cloning
```http
POST /api/voice-clone
Content-Type: multipart/form-data

file: voice_sample.wav
voice_name: "custom_voice"
text: "Test message"
```

## Integration Examples

### Python Client
```python
import requests

# Chat with AI
response = requests.post('http://localhost:8000/api/ollama/chat', json={
    'message': 'What is AI?',
    'model': 'llama3.2:1b',
    'engine': 'gtts',
    'voice_id': 'gtts-en'
})

data = response.json()
print(f"AI Response: {data['response']}")
print(f"Audio URL: {data['audio_url']}")
```

### JavaScript/Web
```javascript
// Chat with AI
const response = await fetch('/api/ollama/chat', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
        message: 'Hello AI',
        model: 'llama3.2:1b',
        engine: 'gtts',
        voice_id: 'gtts-en'
    })
});

const data = await response.json();
console.log('AI Response:', data.response);

// Play audio response
const audio = new Audio(data.audio_url);
audio.play();
```

### cURL
```bash
# Chat request
curl -X POST http://localhost:8000/api/ollama/chat \
  -H "Content-Type: application/json" \
  -d '{"message": "Hello", "model": "llama3.2:1b"}'

# Upload audio for transcription
curl -X POST http://localhost:8000/api/speech-to-text \
  -F "file=@audio.wav"
```

## Use Cases

1. **Customer Service Bots** - Voice-enabled chat support
2. **Voice Assistants** - Custom AI with your voice
3. **Content Creation** - Generate audio from text
4. **Accessibility Tools** - Text-to-speech for apps
5. **Phone Systems** - See `voice-ai-agent/` for Twilio integration

## Available Voices

- **Google TTS**: 14+ languages (gtts-en, gtts-es, etc.)
- **Edge TTS**: 100+ voices (en-US-AriaNeural, etc.)
- **System TTS**: Local system voice
- **Custom**: Upload voice samples for cloning