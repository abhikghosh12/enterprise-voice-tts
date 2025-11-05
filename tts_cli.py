"""
Simple CLI Tool for Quick TTS Generation
Usage: python tts_cli.py "Your text here" --voice en-US-GuyNeural
"""
import asyncio
import sys
import os
import argparse
from pathlib import Path

# Add engines to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'tts-engines'))

from engine_manager import get_engine_manager


class TTSCLI:
    """Command-line interface for TTS"""
    
    def __init__(self):
        self.manager = get_engine_manager()
        
    async def generate(
        self,
        text: str,
        voice_id: str = "en-US-lessac-medium",
        engine: str = "auto",
        output: str = None,
        play: bool = False
    ):
        """Generate speech from text"""
        
        # Auto-generate output filename if not provided
        if output is None:
            output = f"output_{voice_id.replace(':', '_')}_{int(asyncio.get_event_loop().time())}.wav"
        
        print(f"\n🎙️  TTS Generation")
        print(f"📝 Text: {text[:50]}{'...' if len(text) > 50 else ''}")
        print(f"🎭 Voice: {voice_id}")
        print(f"⚙️  Engine: {engine}")
        print(f"💾 Output: {output}")
        print()
        
        # Initialize engines
        print("⏳ Initializing TTS engine...")
        available_engines = ["piper", "edge", "silero"]
        if engine != "auto" and engine not in available_engines:
            available_engines = [engine]
        
        await self.manager.initialize_engines(available_engines)
        
        # Generate speech
        print("🔊 Generating speech...")
        import time
        start_time = time.time()
        
        try:
            result = await self.manager.synthesize(
                text=text,
                voice_id=voice_id,
                output_path=output,
                engine=engine,
                sample_rate=24000
            )
            
            elapsed = time.time() - start_time
            
            print(f"\n✅ Success!")
            print(f"   Engine used: {result['engine']}")
            print(f"   Generation time: {elapsed:.2f}s")
            print(f"   Audio duration: {result['audio_duration']:.2f}s")
            print(f"   File size: {result['file_size']/1024:.1f}KB")
            print(f"   Real-time factor: {elapsed/result['audio_duration']:.2f}x")
            print(f"   Output saved to: {output}")
            
            # Play audio if requested
            if play:
                self.play_audio(output)
            
            return result
            
        except Exception as e:
            print(f"\n❌ Error: {e}")
            import traceback
            traceback.print_exc()
            return None
    
    def play_audio(self, audio_file: str):
        """Play the generated audio"""
        print(f"\n🔊 Playing audio...")
        
        try:
            import platform
            system = platform.system()
            
            if system == "Windows":
                os.system(f'start {audio_file}')
            elif system == "Darwin":  # macOS
                os.system(f'afplay {audio_file}')
            elif system == "Linux":
                os.system(f'aplay {audio_file}')
            else:
                print("⚠️  Auto-play not supported on this platform")
                
        except Exception as e:
            print(f"⚠️  Could not play audio: {e}")
    
    async def list_voices(self, engine: str = None):
        """List all available voices"""
        
        print("\n🎭 Available Voices\n")
        
        if engine:
            # Initialize specific engine
            await self.manager.initialize_engines([engine])
            voices = self.manager.engines[engine].get_voices()
            
            print(f"{'Voice ID':<35} {'Name':<40} {'Language':<10}")
            print("-" * 85)
            
            for voice in voices:
                voice_id = voice.get("id", "N/A")
                name = voice.get("name", "N/A")
                lang = voice.get("language", "N/A")
                print(f"{voice_id:<35} {name:<40} {lang:<10}")
        else:
            # Show voices from all engines
            await self.manager.initialize_engines(["piper", "edge", "silero"])
            all_voices = self.manager.get_available_voices()
            
            print(f"{'Voice ID':<35} {'Name':<35} {'Engine':<10} {'Lang':<8}")
            print("-" * 90)
            
            for voice in all_voices:
                voice_id = voice.get("id", "N/A")
                name = voice.get("name", "N/A")
                engine = voice.get("engine", "N/A")
                lang = voice.get("language", "N/A")
                print(f"{voice_id:<35} {name:<35} {engine:<10} {lang:<8}")
        
        print()


async def main():
    """Main CLI entry point"""
    
    parser = argparse.ArgumentParser(
        description="Enterprise TTS CLI - Fast text-to-speech generation",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Generate speech with default voice
  python tts_cli.py "Hello world"
  
  # Use specific voice
  python tts_cli.py "Hello world" --voice en-US-GuyNeural
  
  # Use fastest engine
  python tts_cli.py "Hello world" --engine piper
  
  # Save to specific file
  python tts_cli.py "Hello world" --output hello.wav
  
  # Generate and play
  python tts_cli.py "Hello world" --play
  
  # List all voices
  python tts_cli.py --list-voices
  
  # List voices for specific engine
  python tts_cli.py --list-voices --engine piper
        """
    )
    
    parser.add_argument(
        "text",
        nargs="?",
        help="Text to convert to speech"
    )
    
    parser.add_argument(
        "-v", "--voice",
        default="en-US-lessac-medium",
        help="Voice ID to use (default: en-US-lessac-medium)"
    )
    
    parser.add_argument(
        "-e", "--engine",
        choices=["auto", "piper", "edge", "silero", "coqui"],
        default="auto",
        help="TTS engine to use (default: auto)"
    )
    
    parser.add_argument(
        "-o", "--output",
        help="Output file path (default: auto-generated)"
    )
    
    parser.add_argument(
        "-p", "--play",
        action="store_true",
        help="Play audio after generation"
    )
    
    parser.add_argument(
        "-l", "--list-voices",
        action="store_true",
        help="List all available voices"
    )
    
    parser.add_argument(
        "-f", "--file",
        help="Read text from file instead of command line"
    )
    
    args = parser.parse_args()
    
    cli = TTSCLI()
    
    # List voices mode
    if args.list_voices:
        await cli.list_voices(args.engine if args.engine != "auto" else None)
        return
    
    # Generate speech mode
    if not args.text and not args.file:
        parser.print_help()
        print("\n❌ Error: Please provide text or use --list-voices")
        return
    
    # Get text from file if specified
    if args.file:
        try:
            with open(args.file, 'r', encoding='utf-8') as f:
                text = f.read()
        except Exception as e:
            print(f"❌ Error reading file: {e}")
            return
    else:
        text = args.text
    
    # Generate speech
    await cli.generate(
        text=text,
        voice_id=args.voice,
        engine=args.engine,
        output=args.output,
        play=args.play
    )


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n\n⚠️  Interrupted by user")
    except Exception as e:
        print(f"\n❌ Fatal error: {e}")
        import traceback
        traceback.print_exc()
