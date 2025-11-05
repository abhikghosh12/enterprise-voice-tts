const express = require('express');
const multer = require('multer');
const Redis = require('ioredis');
const path = require('path');
const fs = require('fs').promises;
const { v4: uuidv4 } = require('uuid');
const cors = require('cors');
const rateLimit = require('express-rate-limit');

const app = express();
const PORT = process.env.PORT || 5000;

// Redis client
const redis = new Redis(process.env.REDIS_URL || 'redis://localhost:6379');

// Middleware
app.use(cors());
app.use(express.json({ limit: '10mb' }));
app.use(express.urlencoded({ extended: true }));
app.use(express.static('public'));
app.use('/output', express.static('output'));

// Rate limiting
const apiLimiter = rateLimit({
  windowMs: 15 * 60 * 1000, // 15 minutes
  max: 100, // Limit each IP to 100 requests per windowMs
  message: 'Too many requests from this IP, please try again later.'
});

// Authentication middleware
const authenticateToken = (req, res, next) => {
  const authHeader = req.headers['authorization'];
  const token = authHeader && authHeader.split(' ')[1];
  
  // For demo purposes, accept any token or no token
  // In production, validate against your token database
  if (process.env.NODE_ENV === 'production' && !token) {
    return res.status(401).json({ error: 'Authentication token required' });
  }
  
  next();
};

// File upload configuration
const storage = multer.diskStorage({
  destination: async (req, file, cb) => {
    const uploadDir = './uploads';
    await fs.mkdir(uploadDir, { recursive: true });
    cb(null, uploadDir);
  },
  filename: (req, file, cb) => {
    const uniqueName = `${uuidv4()}_${file.originalname}`;
    cb(null, uniqueName);
  }
});

const upload = multer({ 
  storage: storage,
  limits: { fileSize: 10 * 1024 * 1024 }, // 10MB limit
  fileFilter: (req, file, cb) => {
    if (file.mimetype === 'application/pdf') {
      cb(null, true);
    } else {
      cb(new Error('Only PDF files are allowed'));
    }
  }
});

// Voice models configuration
const VOICE_MODELS = [
  { id: 'en-US-GuyNeural', name: 'Morgan Freeman-like', language: 'en-US', gender: 'Male' },
  { id: 'en-GB-RyanNeural', name: 'David Attenborough-like', language: 'en-GB', gender: 'Male' },
  { id: 'en-IN-PrabhatNeural', name: 'Amitabh Bachchan-like', language: 'en-IN', gender: 'Male' },
  { id: 'en-GB-SoniaNeural', name: 'British English Female', language: 'en-GB', gender: 'Female' },
  { id: 'hi-IN-SwaraNeural', name: 'Hindi Female', language: 'hi-IN', gender: 'Female' },
  { id: 'hi-IN-MadhurNeural', name: 'Hindi Male', language: 'hi-IN', gender: 'Male' },
  { id: 'de-DE-KatjaNeural', name: 'German Female', language: 'de-DE', gender: 'Female' },
  { id: 'de-DE-ConradNeural', name: 'German Male', language: 'de-DE', gender: 'Male' },
  { id: 'en-US-JennyNeural', name: 'US English Female', language: 'en-US', gender: 'Female' },
  { id: 'en-IN-NeerjaNeural', name: 'Indian English Female', language: 'en-IN', gender: 'Female' }
];

// ============================================
// API Routes (Similar to Smallest.ai)
// ============================================

// Get Speech API - Main TTS endpoint
app.post('/api/v1/lightning/get_speech', apiLimiter, authenticateToken, async (req, res) => {
  try {
    const { voice_id, text, sample_rate = 24000, add_wav_header = true, output_format = 'mp3' } = req.body;

    // Validation
    if (!voice_id || !text) {
      return res.status(400).json({ 
        error: 'Missing required parameters',
        required: ['voice_id', 'text']
      });
    }

    if (text.length > 5000) {
      return res.status(400).json({ 
        error: 'Text too long',
        maxLength: 5000,
        currentLength: text.length
      });
    }

    // Validate voice_id
    const voiceExists = VOICE_MODELS.find(v => v.id === voice_id);
    if (!voiceExists) {
      return res.status(400).json({ 
        error: 'Invalid voice_id',
        availableVoices: VOICE_MODELS.map(v => v.id)
      });
    }

    // Create job
    const jobId = uuidv4();
    const outputFilename = `audio_${jobId}.${output_format}`;
    
    const job = {
      id: jobId,
      type: 'text_to_speech',
      voice_id,
      text,
      sample_rate,
      add_wav_header,
      output_format,
      outputFilename,
      status: 'pending',
      createdAt: new Date().toISOString()
    };

    // Add job to Redis queue
    await redis.lpush('tts:jobs', JSON.stringify(job));
    await redis.set(`job:${jobId}`, JSON.stringify(job), 'EX', 3600); // Expire in 1 hour

    res.json({
      success: true,
      job_id: jobId,
      status: 'processing',
      message: 'Job queued successfully',
      estimated_time: Math.ceil(text.length / 50) + ' seconds'
    });

  } catch (error) {
    console.error('Error in get_speech:', error);
    res.status(500).json({ error: 'Internal server error', message: error.message });
  }
});

// Get available voices
app.get('/api/v1/voices', (req, res) => {
  res.json({
    success: true,
    count: VOICE_MODELS.length,
    voices: VOICE_MODELS
  });
});

// Get job status
app.get('/api/v1/jobs/:jobId', async (req, res) => {
  try {
    const { jobId } = req.params;
    const jobData = await redis.get(`job:${jobId}`);
    
    if (!jobData) {
      return res.status(404).json({ error: 'Job not found' });
    }

    const job = JSON.parse(jobData);
    
    const response = {
      job_id: jobId,
      status: job.status,
      progress: job.progress || 0,
      created_at: job.createdAt
    };

    if (job.status === 'completed') {
      response.result = {
        audio_url: `${req.protocol}://${req.get('host')}/output/${job.outputFilename}`,
        duration: job.duration,
        size: job.size
      };
    } else if (job.status === 'failed') {
      response.error = job.error;
    }

    res.json(response);
  } catch (error) {
    console.error('Error getting job status:', error);
    res.status(500).json({ error: 'Internal server error' });
  }
});

// PDF to Speech API
app.post('/api/v1/pdf/convert', upload.single('file'), apiLimiter, authenticateToken, async (req, res) => {
  try {
    if (!req.file) {
      return res.status(400).json({ error: 'No PDF file uploaded' });
    }

    const { voice_id = 'en-US-GuyNeural', sample_rate = 24000 } = req.body;

    // Validate voice_id
    const voiceExists = VOICE_MODELS.find(v => v.id === voice_id);
    if (!voiceExists) {
      return res.status(400).json({ 
        error: 'Invalid voice_id',
        availableVoices: VOICE_MODELS.map(v => v.id)
      });
    }

    const jobId = uuidv4();
    const outputFilename = `pdf_${jobId}.mp3`;

    const job = {
      id: jobId,
      type: 'pdf_to_speech',
      voice_id,
      sample_rate,
      inputFile: req.file.filename,
      outputFilename,
      status: 'pending',
      createdAt: new Date().toISOString()
    };

    await redis.lpush('tts:jobs', JSON.stringify(job));
    await redis.set(`job:${jobId}`, JSON.stringify(job), 'EX', 3600);

    res.json({
      success: true,
      job_id: jobId,
      status: 'processing',
      message: 'PDF conversion job queued successfully'
    });

  } catch (error) {
    console.error('Error in PDF convert:', error);
    res.status(500).json({ error: 'Internal server error', message: error.message });
  }
});

// Batch text to speech
app.post('/api/v1/batch/convert', apiLimiter, authenticateToken, async (req, res) => {
  try {
    const { items, voice_id = 'en-US-GuyNeural', sample_rate = 24000 } = req.body;

    if (!Array.isArray(items) || items.length === 0) {
      return res.status(400).json({ error: 'Items array is required and must not be empty' });
    }

    if (items.length > 50) {
      return res.status(400).json({ error: 'Maximum 50 items per batch request' });
    }

    const batchId = uuidv4();
    const jobIds = [];

    for (let i = 0; i < items.length; i++) {
      const item = items[i];
      const jobId = uuidv4();
      const outputFilename = `batch_${batchId}_${i}_${jobId}.mp3`;

      const job = {
        id: jobId,
        batchId,
        type: 'text_to_speech',
        voice_id: item.voice_id || voice_id,
        text: item.text,
        sample_rate,
        outputFilename,
        status: 'pending',
        createdAt: new Date().toISOString()
      };

      await redis.lpush('tts:jobs', JSON.stringify(job));
      await redis.set(`job:${jobId}`, JSON.stringify(job), 'EX', 3600);
      jobIds.push(jobId);
    }

    res.json({
      success: true,
      batch_id: batchId,
      job_ids: jobIds,
      total_items: items.length,
      message: 'Batch jobs queued successfully'
    });

  } catch (error) {
    console.error('Error in batch convert:', error);
    res.status(500).json({ error: 'Internal server error', message: error.message });
  }
});

// Analytics endpoint
app.get('/api/v1/analytics', authenticateToken, async (req, res) => {
  try {
    const stats = {
      total_jobs: await redis.get('stats:total_jobs') || 0,
      completed_jobs: await redis.get('stats:completed_jobs') || 0,
      failed_jobs: await redis.get('stats:failed_jobs') || 0,
      average_processing_time: await redis.get('stats:avg_processing_time') || 0,
      popular_voices: VOICE_MODELS.slice(0, 5).map(v => ({
        voice_id: v.id,
        name: v.name,
        usage_count: Math.floor(Math.random() * 1000) // Mock data
      }))
    };

    res.json({
      success: true,
      stats,
      timestamp: new Date().toISOString()
    });
  } catch (error) {
    console.error('Error getting analytics:', error);
    res.status(500).json({ error: 'Internal server error' });
  }
});

// Health check endpoint
app.get('/api/v1/health', async (req, res) => {
  try {
    await redis.ping();
    res.json({ 
      status: 'healthy',
      redis: 'connected',
      timestamp: new Date().toISOString()
    });
  } catch (error) {
    res.status(503).json({ 
      status: 'unhealthy',
      redis: 'disconnected',
      error: error.message
    });
  }
});

// ============================================
// Web Interface Routes
// ============================================

app.get('/', (req, res) => {
  res.sendFile(path.join(__dirname, 'public', 'index.html'));
});

// Legacy PDF upload endpoint (for web interface)
app.post('/upload', upload.single('pdf'), async (req, res) => {
  try {
    if (!req.file) {
      return res.status(400).json({ error: 'No file uploaded' });
    }

    const { voice = 'en-US-GuyNeural' } = req.body;
    const jobId = uuidv4();
    const outputFilename = `output_${jobId}.mp3`;

    const job = {
      id: jobId,
      type: 'pdf_to_speech',
      voice_id: voice,
      inputFile: req.file.filename,
      outputFilename,
      status: 'pending',
      createdAt: new Date().toISOString()
    };

    await redis.lpush('tts:jobs', JSON.stringify(job));
    await redis.set(`job:${jobId}`, JSON.stringify(job), 'EX', 3600);

    res.json({
      message: 'File uploaded and queued for processing',
      jobId: jobId,
      filename: req.file.filename
    });
  } catch (error) {
    console.error('Upload error:', error);
    res.status(500).json({ error: 'Upload failed', message: error.message });
  }
});

// Check job status (for web interface)
app.get('/status/:jobId', async (req, res) => {
  try {
    const { jobId } = req.params;
    const jobData = await redis.get(`job:${jobId}`);
    
    if (!jobData) {
      return res.status(404).json({ error: 'Job not found' });
    }

    const job = JSON.parse(jobData);
    res.json(job);
  } catch (error) {
    console.error('Status check error:', error);
    res.status(500).json({ error: 'Failed to check status' });
  }
});

// Error handling
app.use((err, req, res, next) => {
  console.error('Error:', err);
  res.status(500).json({ error: 'Something went wrong!', message: err.message });
});

// Start server
app.listen(PORT, () => {
  console.log(`🚀 Enterprise Voice TTS API Server running on port ${PORT}`);
  console.log(`📡 API Endpoint: http://localhost:${PORT}/api/v1`);
  console.log(`🌐 Web Dashboard: http://localhost:${PORT}`);
  console.log(`📊 Health Check: http://localhost:${PORT}/api/v1/health`);
});

// Graceful shutdown
process.on('SIGTERM', async () => {
  console.log('SIGTERM received, closing server...');
  await redis.quit();
  process.exit(0);
});
