const Redis = require('ioredis');
const { exec } = require('child_process');
const { promisify } = require('util');
const fs = require('fs').promises;
const path = require('path');
const pdfParse = require('pdf-parse');

const execPromise = promisify(exec);
const redis = new Redis(process.env.REDIS_URL || 'redis://localhost:6379');

console.log('🔧 Enterprise Voice TTS Worker started');
console.log('📡 Connected to Redis:', process.env.REDIS_URL || 'redis://localhost:6379');

// Ensure output directory exists
async function ensureDirectories() {
  await fs.mkdir('./uploads', { recursive: true });
  await fs.mkdir('./output', { recursive: true });
}

// Extract text from PDF
async function extractTextFromPDF(pdfPath) {
  try {
    const dataBuffer = await fs.readFile(pdfPath);
    const data = await pdfParse(dataBuffer);
    return data.text;
  } catch (error) {
    console.error('Error extracting text from PDF:', error);
    throw error;
  }
}

// Convert text to speech using edge-tts
async function textToSpeech(text, voiceId, outputPath, sampleRate = 24000) {
  try {
    const command = `edge-tts --voice ${voiceId} --rate=+0% --text "${text.replace(/"/g, '\\"')}" --write-media "${outputPath}"`;
    
    console.log('🎙️  Generating speech...');
    const startTime = Date.now();
    
    await execPromise(command);
    
    const duration = ((Date.now() - startTime) / 1000).toFixed(2);
    console.log(`✅ Speech generated in ${duration}s`);
    
    // Get file stats
    const stats = await fs.stat(outputPath);
    
    return {
      duration: parseFloat(duration),
      size: stats.size
    };
  } catch (error) {
    console.error('Error in text-to-speech conversion:', error);
    throw error;
  }
}

// Process a single job
async function processJob(job) {
  console.log(`\n📋 Processing job ${job.id} (${job.type})`);
  
  try {
    // Update job status to processing
    job.status = 'processing';
    job.progress = 10;
    await redis.set(`job:${job.id}`, JSON.stringify(job));

    let text = '';
    let outputPath = '';

    if (job.type === 'text_to_speech') {
      text = job.text;
      outputPath = path.join('./output', job.outputFilename);
      
      job.progress = 30;
      await redis.set(`job:${job.id}`, JSON.stringify(job));
      
    } else if (job.type === 'pdf_to_speech') {
      // Extract text from PDF
      console.log('📄 Extracting text from PDF...');
      const pdfPath = path.join('./uploads', job.inputFile);
      text = await extractTextFromPDF(pdfPath);
      
      if (!text || text.trim().length === 0) {
        throw new Error('No text found in PDF');
      }
      
      console.log(`📝 Extracted ${text.length} characters`);
      outputPath = path.join('./output', job.outputFilename);
      
      job.progress = 50;
      await redis.set(`job:${job.id}`, JSON.stringify(job));
    }

    // Limit text length
    if (text.length > 5000) {
      text = text.substring(0, 5000);
      console.log('⚠️  Text truncated to 5000 characters');
    }

    // Convert to speech
    const result = await textToSpeech(
      text,
      job.voice_id,
      outputPath,
      job.sample_rate
    );

    // Update job as completed
    job.status = 'completed';
    job.progress = 100;
    job.duration = result.duration;
    job.size = result.size;
    job.completedAt = new Date().toISOString();

    await redis.set(`job:${job.id}`, JSON.stringify(job));
    
    // Update statistics
    await redis.incr('stats:total_jobs');
    await redis.incr('stats:completed_jobs');
    
    console.log(`✨ Job ${job.id} completed successfully`);
    
    // Clean up uploaded PDF if exists
    if (job.type === 'pdf_to_speech' && job.inputFile) {
      try {
        await fs.unlink(path.join('./uploads', job.inputFile));
        console.log('🗑️  Cleaned up uploaded PDF');
      } catch (err) {
        console.log('Warning: Could not delete uploaded file:', err.message);
      }
    }

  } catch (error) {
    console.error(`❌ Job ${job.id} failed:`, error.message);
    
    job.status = 'failed';
    job.error = error.message;
    job.failedAt = new Date().toISOString();
    
    await redis.set(`job:${job.id}`, JSON.stringify(job));
    await redis.incr('stats:failed_jobs');
  }
}

// Main worker loop
async function startWorker() {
  await ensureDirectories();
  
  console.log('👷 Worker ready, waiting for jobs...\n');

  while (true) {
    try {
      // Block until a job is available (BRPOP with 5 second timeout)
      const result = await redis.brpop('tts:jobs', 5);
      
      if (result) {
        const [, jobData] = result;
        const job = JSON.parse(jobData);
        await processJob(job);
      }
      
    } catch (error) {
      console.error('Worker error:', error);
      // Wait a bit before retrying
      await new Promise(resolve => setTimeout(resolve, 5000));
    }
  }
}

// Handle graceful shutdown
process.on('SIGTERM', async () => {
  console.log('\n🛑 SIGTERM received, shutting down worker...');
  await redis.quit();
  process.exit(0);
});

process.on('SIGINT', async () => {
  console.log('\n🛑 SIGINT received, shutting down worker...');
  await redis.quit();
  process.exit(0);
});

// Start the worker
startWorker().catch(error => {
  console.error('Fatal error starting worker:', error);
  process.exit(1);
});
