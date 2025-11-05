# 📱 WhatsApp Bot Integration

Send voice messages automatically using your TTS engine.

## Setup

### 1. Install Dependencies

```bash
pip install pywhatkit pyautogui pywhatkit
# OR use the requirements in your project
pip install -r whatsapp_requirements.txt
```

### 2. WhatsApp Bot with Voice Messages

Create `whatsapp_voice_bot.py`:

```python
import pywhatkit as kit
import time
from datetime import datetime
import requests
import os
from pathlib import Path

class WhatsAppVoiceBot:
    """Send TTS voice messages via WhatsApp"""
    
    def __init__(self, tts_api_url="http://localhost:5000"):
        self.tts_api_url = tts_api_url
        self.output_dir = Path("whatsapp_audio")
        self.output_dir.mkdir(exist_ok=True)
    
    def generate_speech(self, text, voice_id="en-US-lessac-medium", engine="piper"):
        """Generate speech using TTS API"""
        try:
            # Request TTS
            response = requests.post(
                f"{self.tts_api_url}/api/v1/lightning/get_speech",
                json={
                    "text": text,
                    "voice_id": voice_id,
                    "engine": engine,
                    "sample_rate": 16000  # WhatsApp optimized
                }
            )
            response.raise_for_status()
            data = response.json()
            
            # Poll for completion
            job_id = data['job_id']
            audio_url = self._wait_for_completion(job_id)
            
            # Download audio
            audio_path = self.output_dir / f"voice_{int(time.time())}.mp3"
            self._download_audio(audio_url, audio_path)
            
            return str(audio_path)
            
        except Exception as e:
            print(f"TTS Error: {e}")
            return None
    
    def _wait_for_completion(self, job_id, timeout=30):
        """Wait for TTS job to complete"""
        start_time = time.time()
        
        while time.time() - start_time < timeout:
            response = requests.get(f"{self.tts_api_url}/api/v1/jobs/{job_id}")
            data = response.json()
            
            if data['status'] == 'completed':
                return data['result']['audio_url']
            elif data['status'] == 'failed':
                raise Exception(f"Job failed: {data.get('error')}")
            
            time.sleep(0.5)
        
        raise TimeoutError("TTS job timeout")
    
    def _download_audio(self, audio_url, output_path):
        """Download audio file"""
        response = requests.get(audio_url, stream=True)
        response.raise_for_status()
        
        with open(output_path, 'wb') as f:
            for chunk in response.iter_content(chunk_size=8192):
                f.write(chunk)
    
    def send_voice_message(
        self, 
        phone_number, 
        message_text, 
        schedule_time=None,
        voice_id="en-US-lessac-medium",
        engine="piper"
    ):
        """
        Send voice message via WhatsApp
        
        Args:
            phone_number: With country code (e.g., "+1234567890")
            message_text: Text to convert to speech
            schedule_time: (hour, minute) tuple or None for immediate
            voice_id: TTS voice model
            engine: TTS engine
        """
        try:
            # Generate speech
            print(f"Generating speech for: {message_text[:50]}...")
            audio_path = self.generate_speech(message_text, voice_id, engine)
            
            if not audio_path:
                print("Failed to generate speech")
                return False
            
            print(f"Speech generated: {audio_path}")
            
            # Send via WhatsApp
            if schedule_time:
                hour, minute = schedule_time
                print(f"Scheduling message for {hour}:{minute}")
                kit.sendwhats_image(
                    phone_number,
                    audio_path,
                    "",  # Empty caption
                    hour,
                    minute
                )
            else:
                # Send immediately
                print("Sending immediately...")
                now = datetime.now()
                kit.sendwhats_image(
                    phone_number,
                    audio_path,
                    "🎙️ Voice message",
                    now.hour,
                    now.minute + 1  # Send 1 minute from now
                )
            
            print("✅ Voice message sent successfully!")
            return True
            
        except Exception as e:
            print(f"❌ Error sending message: {e}")
            return False
    
    def send_announcement(
        self,
        phone_numbers,
        announcement_text,
        voice_id="en-US-GuyNeural"
    ):
        """Send announcement to multiple numbers"""
        print(f"Sending announcement to {len(phone_numbers)} recipients")
        
        # Generate speech once
        audio_path = self.generate_speech(announcement_text, voice_id)
        
        if not audio_path:
            print("Failed to generate speech")
            return
        
        # Send to all recipients
        success_count = 0
        for i, number in enumerate(phone_numbers):
            try:
                now = datetime.now()
                # Stagger messages by 2 minutes each
                send_time = (now.hour, now.minute + i * 2)
                
                self.send_voice_message(
                    number,
                    announcement_text,
                    schedule_time=send_time
                )
                
                success_count += 1
                print(f"Scheduled for {number}")
                
            except Exception as e:
                print(f"Failed for {number}: {e}")
        
        print(f"✅ Scheduled {success_count}/{len(phone_numbers)} messages")


# ===========================================
# Example Use Cases
# ===========================================

def example_reminder():
    """Send a reminder voice message"""
    bot = WhatsAppVoiceBot()
    
    bot.send_voice_message(
        phone_number="+1234567890",
        message_text="Hey! This is your reminder for the meeting at 3 PM today. Don't forget to bring the project documents.",
        voice_id="en-US-GuyNeural",
        engine="piper"  # Fast generation
    )


def example_daily_briefing():
    """Send daily briefing"""
    bot = WhatsAppVoiceBot()
    
    briefing = """
    Good morning! Here's your daily briefing:
    - You have 3 meetings today at 10 AM, 2 PM, and 4 PM
    - 5 new emails require your attention
    - Project deadline is in 2 days
    Have a productive day!
    """
    
    bot.send_voice_message(
        phone_number="+1234567890",
        message_text=briefing,
        schedule_time=(8, 0),  # 8:00 AM
        voice_id="en-US-lessac-medium"
    )


def example_team_announcement():
    """Send announcement to team"""
    bot = WhatsAppVoiceBot()
    
    team_numbers = [
        "+1234567890",
        "+1234567891",
        "+1234567892"
    ]
    
    announcement = """
    Team announcement: Our sprint review meeting has been rescheduled to Friday at 2 PM.
    Please prepare your demos and status updates.
    See you there!
    """
    
    bot.send_announcement(team_numbers, announcement)


def example_customer_notification():
    """Notify customer about order"""
    bot = WhatsAppVoiceBot()
    
    order_id = "ORD-12345"
    customer_name = "John"
    
    message = f"""
    Hello {customer_name},
    Your order {order_id} has been shipped and will arrive in 2-3 business days.
    Track your package at the link sent via email.
    Thank you for your order!
    """
    
    bot.send_voice_message(
        phone_number="+1234567890",
        message_text=message,
        voice_id="en-US-GuyNeural"
    )


def example_multilingual_message():
    """Send message in Hindi"""
    bot = WhatsAppVoiceBot()
    
    hindi_message = """
    नमस्ते! यह आपके लिए एक महत्वपूर्ण सूचना है।
    कृपया कल शाम 5 बजे मीटिंग के लिए उपलब्ध रहें।
    धन्यवाद!
    """
    
    bot.send_voice_message(
        phone_number="+91234567890",
        message_text=hindi_message,
        voice_id="hi-IN-MadhurNeural",
        engine="edge"  # Better for Hindi
    )


# ===========================================
# Scheduled Messages System
# ===========================================

class ScheduledMessenger:
    """Schedule recurring voice messages"""
    
    def __init__(self):
        self.bot = WhatsAppVoiceBot()
        self.schedules = []
    
    def add_schedule(
        self,
        phone_number,
        message_text,
        hour,
        minute,
        days_of_week=None,  # [0-6] where 0 is Monday
        voice_id="en-US-lessac-medium"
    ):
        """Add recurring schedule"""
        schedule = {
            'phone': phone_number,
            'message': message_text,
            'hour': hour,
            'minute': minute,
            'days': days_of_week or list(range(7)),  # All days by default
            'voice_id': voice_id
        }
        self.schedules.append(schedule)
    
    def run(self):
        """Run scheduler (call this in a loop or cron job)"""
        now = datetime.now()
        current_day = now.weekday()
        current_hour = now.hour
        current_minute = now.minute
        
        for schedule in self.schedules:
            if (current_day in schedule['days'] and
                current_hour == schedule['hour'] and
                current_minute == schedule['minute']):
                
                print(f"Sending scheduled message to {schedule['phone']}")
                self.bot.send_voice_message(
                    phone_number=schedule['phone'],
                    message_text=schedule['message'],
                    voice_id=schedule['voice_id']
                )


# Example: Daily standup reminder
def example_daily_standup():
    scheduler = ScheduledMessenger()
    
    # Monday to Friday at 9:55 AM
    scheduler.add_schedule(
        phone_number="+1234567890",
        message_text="Daily standup starting in 5 minutes! Please join the call.",
        hour=9,
        minute=55,
        days_of_week=[0, 1, 2, 3, 4]  # Mon-Fri
    )
    
    # Run scheduler
    while True:
        scheduler.run()
        time.sleep(60)  # Check every minute


# ===========================================
# Advanced: WhatsApp Business API Integration
# ===========================================

class WhatsAppBusinessBot:
    """
    Integration with WhatsApp Business API
    Requires: Twilio or similar WhatsApp Business API provider
    """
    
    def __init__(self, account_sid, auth_token, whatsapp_number, tts_api_url="http://localhost:5000"):
        from twilio.rest import Client
        self.client = Client(account_sid, auth_token)
        self.from_number = f"whatsapp:{whatsapp_number}"
        self.tts_bot = WhatsAppVoiceBot(tts_api_url)
    
    def send_voice_message(self, to_number, message_text, voice_id="en-US-lessac-medium"):
        """Send voice message via WhatsApp Business API"""
        # Generate speech
        audio_path = self.tts_bot.generate_speech(message_text, voice_id)
        
        if not audio_path:
            return False
        
        # Upload audio to your server (must be publicly accessible)
        audio_url = self._upload_to_server(audio_path)
        
        # Send via Twilio WhatsApp API
        message = self.client.messages.create(
            from_=self.from_number,
            to=f"whatsapp:{to_number}",
            media_url=[audio_url]
        )
        
        return message.sid
    
    def _upload_to_server(self, audio_path):
        """Upload audio to your public server"""
        # Implement your upload logic
        # Return public URL
        pass


# ===========================================
# Main Script
# ===========================================

if __name__ == "__main__":
    import sys
    
    if len(sys.argv) < 3:
        print("""
Usage:
  python whatsapp_voice_bot.py <phone_number> <message>
  
Example:
  python whatsapp_voice_bot.py "+1234567890" "Hello, this is a voice message"
  
Options:
  --voice    Voice model (default: en-US-lessac-medium)
  --engine   TTS engine (default: piper)
  --schedule HH:MM to schedule message
        """)
        sys.exit(1)
    
    phone_number = sys.argv[1]
    message = sys.argv[2]
    
    # Parse options
    voice_id = "en-US-lessac-medium"
    engine = "piper"
    schedule_time = None
    
    if "--voice" in sys.argv:
        idx = sys.argv.index("--voice")
        voice_id = sys.argv[idx + 1]
    
    if "--engine" in sys.argv:
        idx = sys.argv.index("--engine")
        engine = sys.argv[idx + 1]
    
    if "--schedule" in sys.argv:
        idx = sys.argv.index("--schedule")
        time_str = sys.argv[idx + 1]
        hour, minute = map(int, time_str.split(":"))
        schedule_time = (hour, minute)
    
    # Send message
    bot = WhatsAppVoiceBot()
    bot.send_voice_message(
        phone_number=phone_number,
        message_text=message,
        schedule_time=schedule_time,
        voice_id=voice_id,
        engine=engine
    )
```

## Usage Examples

### 1. Send Immediate Voice Message

```bash
python whatsapp_voice_bot.py "+1234567890" "Hello! This is a test voice message"
```

### 2. Schedule Message

```bash
python whatsapp_voice_bot.py "+1234567890" "Meeting reminder" --schedule 14:30
```

### 3. Use Specific Voice

```bash
python whatsapp_voice_bot.py "+1234567890" "Important announcement" --voice en-US-GuyNeural
```

### 4. Hindi Message

```bash
python whatsapp_voice_bot.py "+91234567890" "नमस्ते" --voice hi-IN-MadhurNeural --engine edge
```

## Integration with Your Existing Code

Update your existing `whatsapp_bot.py`:

```python
from tts_sdk import VoiceTTSClient

# Add TTS support to your existing bot
class EnhancedWhatsAppBot:
    def __init__(self):
        self.tts_client = VoiceTTSClient()
        # Your existing initialization
    
    def send_text_as_voice(self, phone_number, text):
        """Convert text to voice and send"""
        # Generate speech
        result = self.tts_client.synthesize(
            text=text,
            voiceId="en-US-lessac-medium",
            engine="piper"
        )
        
        # Download audio
        audio_path = f"temp_{int(time.time())}.mp3"
        self.tts_client.download_audio(result['audio_url'], audio_path)
        
        # Send via WhatsApp (your existing method)
        self.send_audio_message(phone_number, audio_path)
        
        # Cleanup
        os.remove(audio_path)
```

## Automation Scripts

### Daily News Briefing

```python
def send_daily_news():
    """Send daily news as voice message"""
    import feedparser
    
    bot = WhatsAppVoiceBot()
    
    # Fetch news
    feed = feedparser.parse('http://news.google.com/rss')
    
    # Create briefing
    briefing = "Good morning! Here are today's top news headlines:\n\n"
    for i, entry in enumerate(feed.entries[:5], 1):
        briefing += f"{i}. {entry.title}\n"
    
    # Send to subscribers
    subscribers = ["+1234567890", "+1234567891"]
    
    for number in subscribers:
        bot.send_voice_message(
            phone_number=number,
            message_text=briefing,
            schedule_time=(7, 0)  # 7 AM
        )
```

### Weather Updates

```python
def send_weather_update():
    """Send weather forecast as voice"""
    import requests
    
    bot = WhatsAppVoiceBot()
    
    # Get weather data
    response = requests.get('https://api.openweathermap.org/data/2.5/weather?q=London&appid=YOUR_API_KEY')
    weather = response.json()
    
    message = f"""
    Good morning! Today's weather forecast:
    Temperature: {weather['main']['temp']}°C
    Conditions: {weather['weather'][0]['description']}
    Humidity: {weather['main']['humidity']}%
    Have a great day!
    """
    
    bot.send_voice_message(
        phone_number="+1234567890",
        message_text=message,
        schedule_time=(6, 30)
    )
```

## Tips

1. **Optimize for WhatsApp**: Use 16kHz sample rate
   ```python
   sample_rate=16000  # Smaller file size
   ```

2. **Keep Messages Short**: WhatsApp voice messages work best under 2 minutes

3. **Use Fast Engine**: Piper engine for real-time responses
   ```python
   engine="piper"  # 0.3s generation time
   ```

4. **Handle Errors**: Always check if audio generation succeeded

5. **Rate Limiting**: Don't spam - WhatsApp may block

---

**Performance**: Generate 30-second audio in 0.3-0.8 seconds with Piper!

**Privacy**: All voice generation happens on your local TTS server.
