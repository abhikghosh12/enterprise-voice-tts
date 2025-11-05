#!/usr/bin/env python3
"""
Simple Voice AI Demo - Working Version
"""

from fastapi import FastAPI, WebSocket
from fastapi.responses import HTMLResponse
from fastapi.middleware.cors import CORSMiddleware
import json
import uuid
import requests

app = FastAPI(title="Simple Voice AI Demo")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.websocket("/ws/chat")
async def websocket_chat(websocket: WebSocket):
    await websocket.accept()
    
    try:
        # Send greeting
        await websocket.send_json({
            "type": "greeting",
            "message": "Hello! I'm your AI assistant. Type a message to get started!"
        })
        
        while True:
            data = await websocket.receive_json()
            
            if data["type"] == "text_message":
                # Get AI response
                user_message = data["message"]
                
                try:
                    response = requests.post("http://localhost:8000/api/ollama/chat", json={
                        "message": user_message,
                        "model": "llama3.2:1b",
                        "engine": "gtts",
                        "voice_id": "gtts-en"
                    })
                    
                    if response.status_code == 200:
                        result = response.json()
                        if result.get('success'):
                            await websocket.send_json({
                                "type": "ai_response",
                                "text": result['response'],
                                "audio_url": result.get('audio_url'),
                                "duration": result.get('duration', 0)
                            })
                        else:
                            await websocket.send_json({
                                "type": "error",
                                "message": "AI service error"
                            })
                    else:
                        await websocket.send_json({
                            "type": "error", 
                            "message": "AI service unavailable"
                        })
                        
                except Exception as e:
                    await websocket.send_json({
                        "type": "error",
                        "message": f"Error: {str(e)}"
                    })
                    
    except Exception as e:
        print(f"WebSocket error: {e}")

@app.get("/")
async def get_demo():
    return HTMLResponse(content="""
<!DOCTYPE html>
<html>
<head>
    <title>Simple Voice AI Demo</title>
    <style>
        body { font-family: Arial, sans-serif; max-width: 800px; margin: 0 auto; padding: 20px; }
        .chat-container { border: 1px solid #ccc; height: 400px; overflow-y: auto; padding: 10px; margin: 20px 0; }
        .message { margin: 10px 0; padding: 10px; border-radius: 5px; }
        .user { background: #e3f2fd; text-align: right; }
        .ai { background: #f3e5f5; }
        .input-container { display: flex; gap: 10px; }
        input { flex: 1; padding: 10px; }
        button { padding: 10px 20px; cursor: pointer; }
        .audio-player { margin: 10px 0; }
    </style>
</head>
<body>
    <h1>🎙️ Simple Voice AI Demo</h1>
    <div id="chat" class="chat-container"></div>
    <div class="input-container">
        <input type="text" id="messageInput" placeholder="Type your message..." onkeypress="handleKeyPress(event)">
        <button onclick="sendMessage()">Send</button>
    </div>
    <div id="status">Ready</div>

    <script>
        let websocket = null;

        function connect() {
            websocket = new WebSocket('ws://localhost:8002/ws/chat');
            
            websocket.onopen = function() {
                updateStatus('Connected');
            };
            
            websocket.onmessage = function(event) {
                const data = JSON.parse(event.data);
                handleMessage(data);
            };
            
            websocket.onclose = function() {
                updateStatus('Disconnected');
                setTimeout(connect, 3000); // Reconnect
            };
        }

        function handleMessage(data) {
            const chat = document.getElementById('chat');
            
            switch(data.type) {
                case 'greeting':
                    addMessage('AI', data.message);
                    break;
                    
                case 'ai_response':
                    addMessage('AI', data.text);
                    if (data.audio_url) {
                        addAudio(data.audio_url);
                    }
                    break;
                    
                case 'error':
                    addMessage('System', 'Error: ' + data.message);
                    break;
            }
        }

        function addMessage(sender, text) {
            const chat = document.getElementById('chat');
            const div = document.createElement('div');
            div.className = 'message ' + (sender === 'User' ? 'user' : 'ai');
            div.innerHTML = `<strong>${sender}:</strong> ${text}`;
            chat.appendChild(div);
            chat.scrollTop = chat.scrollHeight;
        }

        function addAudio(audioUrl) {
            const chat = document.getElementById('chat');
            const div = document.createElement('div');
            div.className = 'audio-player';
            div.innerHTML = `
                <audio controls>
                    <source src="${audioUrl}" type="audio/wav">
                    Your browser does not support audio.
                </audio>
            `;
            chat.appendChild(div);
            chat.scrollTop = chat.scrollHeight;
        }

        function sendMessage() {
            const input = document.getElementById('messageInput');
            const message = input.value.trim();
            
            if (message && websocket) {
                addMessage('User', message);
                websocket.send(JSON.stringify({
                    type: 'text_message',
                    message: message
                }));
                input.value = '';
            }
        }

        function handleKeyPress(event) {
            if (event.key === 'Enter') {
                sendMessage();
            }
        }

        function updateStatus(status) {
            document.getElementById('status').textContent = 'Status: ' + status;
        }

        // Connect on page load
        connect();
    </script>
</body>
</html>
    """)

if __name__ == "__main__":
    import uvicorn
    print("🎙️ Simple Voice AI Demo")
    print("📡 Server: http://localhost:8002")
    print("💬 Text chat with voice responses!")
    
    uvicorn.run(app, host="0.0.0.0", port=8002)