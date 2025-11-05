"""
Enterprise TTS Worker - High Performance
Multi-engine support with automatic optimization
"""
import asyncio
import json
import logging
import os
import sys
from pathlib import Path
import time

# Add engines to path
sys.path.insert(0, os.path.dirname(__file__))

from engine_manager import get_engine_manager
import redis.asyncio as aioredis

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler('tts_worker.log')
    ]
)
logger = logging.getLogger(__name__)


class TTSWorker:
    """High-performance TTS worker with multiple engine support"""
    
    def __init__(self, redis_url: str = "redis://localhost:6379"):
        self.redis_url = redis_url
        self.redis = None
        self.engine_manager = get_engine_manager()
        self.stats = {
            "total_jobs": 0,
            "successful_jobs": 0,
            "failed_jobs": 0,
            "total_processing_time": 0
        }
        
    async def initialize(self):
        """Initialize worker components"""
        logger.info("🚀 Initializing Enterprise TTS Worker")
        
        # Connect to Redis
        self.redis = await aioredis.from_url(self.redis_url, decode_responses=True)
        logger.info(f"✅ Connected to Redis: {self.redis_url}")
        
        # Initialize TTS engines
        # Start with fastest engines first
        await self.engine_manager.initialize_engines(["piper", "edge", "silero", "coqui"])
        
        # Ensure directories exist
        Path("./uploads").mkdir(exist_ok=True)
        Path("./output").mkdir(exist_ok=True)
        
        logger.info("🎯 Worker ready and waiting for jobs")
        
    async def process_job(self, job_data: dict):
        """Process a single TTS job"""
        job_id = job_data.get("id")
        logger.info(f"\n{'='*60}")
        logger.info(f"📋 Processing Job: {job_id}")
        logger.info(f"   Type: {job_data.get('type')}")
        logger.info(f"   Voice: {job_data.get('voice_id')}")
        logger.info(f"{'='*60}")
        
        start_time = time.time()
        
        try:
            # Update job status to processing
            job_data["status"] = "processing"
            job_data["progress"] = 10
            await self.redis.set(f"job:{job_id}", json.dumps(job_data), ex=3600)
            
            # Extract job details
            job_type = job_data.get("type")
            voice_id = job_data.get("voice_id")
            sample_rate = job_data.get("sample_rate", 24000)
            output_filename = job_data.get("outputFilename")
            output_path = Path("./output") / output_filename
            
            # Get text based on job type
            if job_type == "text_to_speech":
                text = job_data.get("text", "")
                
            elif job_type == "pdf_to_speech":
                # Extract text from PDF
                pdf_path = Path("./uploads") / job_data.get("inputFile")
                text = await self._extract_pdf_text(pdf_path)
                
                job_data["progress"] = 30
                await self.redis.set(f"job:{job_id}", json.dumps(job_data), ex=3600)
                
            else:
                raise ValueError(f"Unknown job type: {job_type}")
            
            # Validate text
            if not text or len(text.strip()) == 0:
                raise ValueError("No text to synthesize")
            
            # Limit text length
            if len(text) > 5000:
                logger.warning(f"⚠️  Text truncated from {len(text)} to 5000 characters")
                text = text[:5000]
            
            logger.info(f"📝 Text length: {len(text)} characters")
            
            # Update progress
            job_data["progress"] = 50
            await self.redis.set(f"job:{job_id}", json.dumps(job_data), ex=3600)
            
            # Synthesize speech
            result = await self.engine_manager.synthesize(
                text=text,
                voice_id=voice_id,
                output_path=str(output_path),
                engine="auto",  # Auto-select best engine
                sample_rate=sample_rate
            )
            
            # Update job as completed
            processing_time = time.time() - start_time
            
            job_data.update({
                "status": "completed",
                "progress": 100,
                "duration": processing_time,
                "size": result["file_size"],
                "audio_duration": result["audio_duration"],
                "engine_used": result["engine"],
                "completedAt": time.strftime("%Y-%m-%d %H:%M:%S")
            })
            
            await self.redis.set(f"job:{job_id}", json.dumps(job_data), ex=3600)
            
            # Update statistics
            self.stats["successful_jobs"] += 1
            self.stats["total_processing_time"] += processing_time
            await self._update_stats()
            
            logger.info(f"✨ Job {job_id} completed in {processing_time:.2f}s")
            logger.info(f"   Engine: {result['engine']}")
            logger.info(f"   Audio duration: {result['audio_duration']:.2f}s")
            logger.info(f"   File size: {result['file_size']/1024:.1f}KB")
            
            # Cleanup
            if job_type == "pdf_to_speech":
                try:
                    pdf_path.unlink()
                    logger.info("🗑️  Cleaned up uploaded PDF")
                except:
                    pass
            
        except Exception as e:
            processing_time = time.time() - start_time
            
            logger.error(f"❌ Job {job_id} failed: {str(e)}")
            logger.exception(e)
            
            job_data.update({
                "status": "failed",
                "error": str(e),
                "failedAt": time.strftime("%Y-%m-%d %H:%M:%S"),
                "duration": processing_time
            })
            
            await self.redis.set(f"job:{job_id}", json.dumps(job_data), ex=3600)
            
            self.stats["failed_jobs"] += 1
            await self._update_stats()
    
    async def _extract_pdf_text(self, pdf_path: Path) -> str:
        """Extract text from PDF file"""
        logger.info(f"📄 Extracting text from: {pdf_path.name}")
        
        try:
            import PyPDF2
            
            text = ""
            with open(pdf_path, 'rb') as file:
                pdf_reader = PyPDF2.PdfReader(file)
                for page_num in range(len(pdf_reader.pages)):
                    page = pdf_reader.pages[page_num]
                    text += page.extract_text()
            
            logger.info(f"✅ Extracted {len(text)} characters from {len(pdf_reader.pages)} pages")
            return text.strip()
            
        except Exception as e:
            logger.error(f"Failed to extract PDF text: {e}")
            raise
    
    async def _update_stats(self):
        """Update global statistics"""
        self.stats["total_jobs"] = self.stats["successful_jobs"] + self.stats["failed_jobs"]
        
        await self.redis.set("stats:total_jobs", self.stats["total_jobs"])
        await self.redis.set("stats:completed_jobs", self.stats["successful_jobs"])
        await self.redis.set("stats:failed_jobs", self.stats["failed_jobs"])
        
        if self.stats["successful_jobs"] > 0:
            avg_time = self.stats["total_processing_time"] / self.stats["successful_jobs"]
            await self.redis.set("stats:avg_processing_time", f"{avg_time:.2f}")
    
    async def run(self):
        """Main worker loop"""
        await self.initialize()
        
        logger.info("\n" + "="*60)
        logger.info("🎙️  ENTERPRISE TTS WORKER ACTIVE")
        logger.info("="*60)
        logger.info(f"Engines loaded: {', '.join(self.engine_manager.engines.keys())}")
        logger.info("Waiting for jobs from Redis queue...")
        logger.info("="*60 + "\n")
        
        while True:
            try:
                # Block and wait for jobs (timeout 5 seconds)
                result = await self.redis.brpop("tts:jobs", timeout=5)
                
                if result:
                    queue_name, job_json = result
                    job_data = json.loads(job_json)
                    await self.process_job(job_data)
                
            except KeyboardInterrupt:
                logger.info("\n⚠️  Received shutdown signal")
                break
                
            except Exception as e:
                logger.error(f"Worker error: {e}")
                logger.exception(e)
                await asyncio.sleep(5)  # Wait before retrying
        
        logger.info("🛑 Worker shutting down...")
        await self.redis.close()


async def main():
    """Entry point"""
    redis_url = os.getenv("REDIS_URL", "redis://localhost:6379")
    worker = TTSWorker(redis_url)
    
    try:
        await worker.run()
    except KeyboardInterrupt:
        logger.info("\n👋 Goodbye!")


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n👋 Worker stopped")
