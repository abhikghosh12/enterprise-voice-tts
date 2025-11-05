# 🚀 Deploy as Commercial API Service

Turn your TTS platform into a production-ready API service like Smallest.ai

## Table of Contents

1. [Architecture Overview](#architecture-overview)
2. [Production Deployment](#production-deployment)
3. [API Monetization](#api-monetization)
4. [Client Onboarding](#client-onboarding)
5. [Monitoring & Analytics](#monitoring--analytics)
6. [Scaling Strategy](#scaling-strategy)

---

## 🏗️ Architecture Overview

### Current vs Production Architecture

**Current (Local Development)**:
```
Browser → Node.js Server → Redis → Python Worker → Audio Files
```

**Production (Multi-Tenant SaaS)**:
```
Client Apps
    ↓
Load Balancer (Nginx)
    ↓
API Gateway (Kong/Tyk)
    ├─ Authentication
    ├─ Rate Limiting
    ├─ Usage Tracking
    └─ Request Routing
    ↓
API Servers (Horizontal Scaling)
    ↓
Redis Cluster (Job Queue)
    ↓
TTS Worker Pool (Auto-Scaling)
    ↓
CDN (Cloudflare) ← Audio Storage (S3/MinIO)
    ↓
Analytics Database (PostgreSQL)
```

---

## 🎯 Production Deployment

### Step 1: Enhanced API with Authentication

Update `server.js` to include proper authentication:

```javascript
// auth-middleware.js
const jwt = require('jsonwebtoken');
const { Pool } = require('pg');

const pool = new Pool({
  connectionString: process.env.DATABASE_URL
});

async function authenticateAPIKey(req, res, next) {
  const authHeader = req.headers['authorization'];
  const apiKey = authHeader && authHeader.split(' ')[1];
  
  if (!apiKey) {
    return res.status(401).json({ error: 'API key required' });
  }
  
  try {
    // Verify API key in database
    const result = await pool.query(
      'SELECT * FROM api_keys WHERE key = $1 AND active = true',
      [apiKey]
    );
    
    if (result.rows.length === 0) {
      return res.status(401).json({ error: 'Invalid API key' });
    }
    
    const apiKeyData = result.rows[0];
    
    // Check rate limits
    const usage = await checkRateLimit(apiKeyData.customer_id);
    if (usage.exceeded) {
      return res.status(429).json({ 
        error: 'Rate limit exceeded',
        limit: usage.limit,
        reset: usage.reset
      });
    }
    
    // Attach customer data to request
    req.customer = apiKeyData;
    
    // Track usage
    await trackUsage(apiKeyData.customer_id, req.body.text.length);
    
    next();
  } catch (error) {
    console.error('Auth error:', error);
    res.status(500).json({ error: 'Authentication failed' });
  }
}

async function checkRateLimit(customerId) {
  // Implement rate limiting logic
  const key = `rate_limit:${customerId}`;
  const count = await redis.incr(key);
  
  if (count === 1) {
    await redis.expire(key, 60); // 1 minute window
  }
  
  const limit = 100; // requests per minute
  return {
    exceeded: count > limit,
    limit: limit,
    remaining: Math.max(0, limit - count),
    reset: await redis.ttl(key)
  };
}

async function trackUsage(customerId, characterCount) {
  // Track usage for billing
  await pool.query(
    `INSERT INTO usage_logs (customer_id, characters, timestamp)
     VALUES ($1, $2, NOW())`,
    [customerId, characterCount]
  );
  
  // Update daily counter
  const today = new Date().toISOString().split('T')[0];
  await redis.hincrby(`usage:${customerId}:${today}`, 'characters', characterCount);
}

module.exports = { authenticateAPIKey };
```

### Step 2: Database Schema

Create PostgreSQL schema:

```sql
-- customers.sql

CREATE TABLE customers (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  email VARCHAR(255) UNIQUE NOT NULL,
  company_name VARCHAR(255),
  plan VARCHAR(50) NOT NULL, -- 'free', 'starter', 'pro', 'enterprise'
  status VARCHAR(50) DEFAULT 'active',
  created_at TIMESTAMP DEFAULT NOW(),
  updated_at TIMESTAMP DEFAULT NOW()
);

CREATE TABLE api_keys (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  customer_id UUID REFERENCES customers(id),
  key VARCHAR(255) UNIQUE NOT NULL,
  name VARCHAR(255),
  active BOOLEAN DEFAULT true,
  rate_limit INT DEFAULT 100, -- requests per minute
  created_at TIMESTAMP DEFAULT NOW(),
  last_used_at TIMESTAMP
);

CREATE TABLE usage_logs (
  id BIGSERIAL PRIMARY KEY,
  customer_id UUID REFERENCES customers(id),
  api_key_id UUID REFERENCES api_keys(id),
  endpoint VARCHAR(255),
  characters INT,
  audio_seconds DECIMAL(10,2),
  engine VARCHAR(50),
  voice_id VARCHAR(100),
  timestamp TIMESTAMP DEFAULT NOW(),
  cost DECIMAL(10,4)
);

CREATE TABLE subscriptions (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  customer_id UUID REFERENCES customers(id),
  plan VARCHAR(50),
  price_monthly DECIMAL(10,2),
  character_limit INT,
  start_date DATE,
  end_date DATE,
  auto_renew BOOLEAN DEFAULT true
);

-- Indexes for performance
CREATE INDEX idx_usage_customer ON usage_logs(customer_id, timestamp);
CREATE INDEX idx_api_keys_customer ON api_keys(customer_id);
CREATE INDEX idx_api_keys_key ON api_keys(key) WHERE active = true;
```

### Step 3: Customer Dashboard API

```javascript
// dashboard-api.js

// Get customer usage statistics
app.get('/api/v1/dashboard/usage', authenticateAPIKey, async (req, res) => {
  const customerId = req.customer.customer_id;
  const { period = 'month' } = req.query;
  
  try {
    // Get usage data
    const usage = await pool.query(`
      SELECT 
        DATE(timestamp) as date,
        SUM(characters) as characters,
        SUM(audio_seconds) as audio_seconds,
        COUNT(*) as requests,
        SUM(cost) as cost
      FROM usage_logs
      WHERE customer_id = $1
        AND timestamp >= NOW() - INTERVAL '1 ${period}'
      GROUP BY DATE(timestamp)
      ORDER BY date DESC
    `, [customerId]);
    
    // Get rate limit info
    const rateLimit = await checkRateLimit(customerId);
    
    res.json({
      usage: usage.rows,
      rate_limit: rateLimit,
      subscription: await getSubscriptionInfo(customerId)
    });
  } catch (error) {
    res.status(500).json({ error: error.message });
  }
});

// Get customer's API keys
app.get('/api/v1/dashboard/keys', authenticateAPIKey, async (req, res) => {
  const customerId = req.customer.customer_id;
  
  const keys = await pool.query(`
    SELECT id, name, key, active, rate_limit, created_at, last_used_at
    FROM api_keys
    WHERE customer_id = $1
    ORDER BY created_at DESC
  `, [customerId]);
  
  res.json({ keys: keys.rows });
});

// Generate new API key
app.post('/api/v1/dashboard/keys', authenticateAPIKey, async (req, res) => {
  const customerId = req.customer.customer_id;
  const { name, rate_limit } = req.body;
  
  // Generate secure API key
  const apiKey = `vtts_${crypto.randomBytes(32).toString('hex')}`;
  
  const result = await pool.query(`
    INSERT INTO api_keys (customer_id, key, name, rate_limit)
    VALUES ($1, $2, $3, $4)
    RETURNING *
  `, [customerId, apiKey, name, rate_limit]);
  
  res.json({ key: result.rows[0] });
});
```

### Step 4: Docker Production Setup

Create `docker-compose.production.yml`:

```yaml
version: '3.8'

services:
  # Nginx Load Balancer
  nginx:
    image: nginx:alpine
    ports:
      - "80:80"
      - "443:443"
    volumes:
      - ./nginx.conf:/etc/nginx/nginx.conf:ro
      - ./ssl:/etc/nginx/ssl:ro
    depends_on:
      - api-server
    restart: unless-stopped

  # API Servers (Multiple instances)
  api-server:
    build:
      context: .
      dockerfile: Dockerfile.web
    environment:
      - NODE_ENV=production
      - REDIS_URL=redis://redis:6379
      - DATABASE_URL=postgresql://user:pass@postgres:5432/tts_db
      - JWT_SECRET=${JWT_SECRET}
      - S3_BUCKET=${S3_BUCKET}
      - S3_ACCESS_KEY=${S3_ACCESS_KEY}
      - S3_SECRET_KEY=${S3_SECRET_KEY}
    depends_on:
      - redis
      - postgres
    restart: unless-stopped
    deploy:
      replicas: 3
      resources:
        limits:
          cpus: '1'
          memory: 1G

  # TTS Workers (Auto-scaling)
  tts-worker:
    build:
      context: .
      dockerfile: Dockerfile.tts-worker
    environment:
      - REDIS_URL=redis://redis:6379
      - S3_BUCKET=${S3_BUCKET}
      - S3_ACCESS_KEY=${S3_ACCESS_KEY}
      - S3_SECRET_KEY=${S3_SECRET_KEY}
      - ENABLE_GPU=true
    volumes:
      - ./models_cache:/app/models_cache
    restart: unless-stopped
    deploy:
      replicas: 4
      resources:
        limits:
          cpus: '2'
          memory: 4G
        reservations:
          devices:
            - driver: nvidia
              count: 1
              capabilities: [gpu]

  # Redis Cluster
  redis:
    image: redis:6-alpine
    command: redis-server --appendonly yes --requirepass ${REDIS_PASSWORD}
    volumes:
      - redis-data:/data
    restart: unless-stopped

  # PostgreSQL Database
  postgres:
    image: postgres:14-alpine
    environment:
      - POSTGRES_DB=tts_db
      - POSTGRES_USER=tts_user
      - POSTGRES_PASSWORD=${POSTGRES_PASSWORD}
    volumes:
      - postgres-data:/var/lib/postgresql/data
      - ./schema.sql:/docker-entrypoint-initdb.d/schema.sql
    restart: unless-stopped

  # MinIO (S3-compatible storage)
  minio:
    image: minio/minio
    command: server /data --console-address ":9001"
    environment:
      - MINIO_ROOT_USER=${MINIO_ROOT_USER}
      - MINIO_ROOT_PASSWORD=${MINIO_ROOT_PASSWORD}
    volumes:
      - minio-data:/data
    ports:
      - "9000:9000"
      - "9001:9001"
    restart: unless-stopped

  # Monitoring (Prometheus)
  prometheus:
    image: prom/prometheus
    volumes:
      - ./prometheus.yml:/etc/prometheus/prometheus.yml
      - prometheus-data:/prometheus
    ports:
      - "9090:9090"
    restart: unless-stopped

  # Grafana Dashboard
  grafana:
    image: grafana/grafana
    ports:
      - "3000:3000"
    environment:
      - GF_SECURITY_ADMIN_PASSWORD=${GRAFANA_PASSWORD}
    volumes:
      - grafana-data:/var/lib/grafana
    restart: unless-stopped

volumes:
  redis-data:
  postgres-data:
  minio-data:
  prometheus-data:
  grafana-data:
```

### Step 5: Nginx Configuration

Create `nginx.conf`:

```nginx
upstream api_servers {
    least_conn;
    server api-server:5000 max_fails=3 fail_timeout=30s;
}

# Rate limiting
limit_req_zone $binary_remote_addr zone=api_limit:10m rate=10r/s;

server {
    listen 80;
    server_name api.yourcompany.com;
    
    # Redirect to HTTPS
    return 301 https://$server_name$request_uri;
}

server {
    listen 443 ssl http2;
    server_name api.yourcompany.com;
    
    # SSL Configuration
    ssl_certificate /etc/nginx/ssl/fullchain.pem;
    ssl_certificate_key /etc/nginx/ssl/privkey.pem;
    ssl_protocols TLSv1.2 TLSv1.3;
    
    # Security Headers
    add_header X-Frame-Options "SAMEORIGIN" always;
    add_header X-XSS-Protection "1; mode=block" always;
    add_header X-Content-Type-Options "nosniff" always;
    
    # API Endpoints
    location /api/ {
        limit_req zone=api_limit burst=20 nodelay;
        
        proxy_pass http://api_servers;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        
        # Timeouts
        proxy_connect_timeout 60s;
        proxy_send_timeout 60s;
        proxy_read_timeout 60s;
        
        # CORS
        add_header 'Access-Control-Allow-Origin' '*' always;
        add_header 'Access-Control-Allow-Methods' 'GET, POST, OPTIONS' always;
        add_header 'Access-Control-Allow-Headers' 'Authorization, Content-Type' always;
        
        if ($request_method = 'OPTIONS') {
            return 204;
        }
    }
    
    # Audio Files (served from CDN)
    location /output/ {
        proxy_pass http://minio:9000/audio-files/;
        proxy_set_header Host $host;
        
        # Cache headers
        add_header Cache-Control "public, max-age=31536000";
        add_header X-Content-Type-Options "nosniff";
    }
    
    # Health Check
    location /health {
        access_log off;
        return 200 "healthy\n";
        add_header Content-Type text/plain;
    }
}
```

---

## 💰 API Monetization

### Pricing Plans

```javascript
// pricing-plans.js

const PRICING_PLANS = {
  free: {
    name: 'Free',
    price: 0,
    limits: {
      characters_per_month: 10000,
      requests_per_minute: 10,
      max_concurrent: 2,
      voices: ['basic-voices'],
      engines: ['piper']
    }
  },
  
  starter: {
    name: 'Starter',
    price: 29,
    limits: {
      characters_per_month: 500000,
      requests_per_minute: 100,
      max_concurrent: 10,
      voices: ['all'],
      engines: ['piper', 'edge']
    }
  },
  
  professional: {
    name: 'Professional',
    price: 99,
    limits: {
      characters_per_month: 2000000,
      requests_per_minute: 500,
      max_concurrent: 50,
      voices: ['all'],
      engines: ['all'],
      features: ['voice_cloning', 'priority_support']
    }
  },
  
  enterprise: {
    name: 'Enterprise',
    price: 'custom',
    limits: {
      characters_per_month: 'unlimited',
      requests_per_minute: 'custom',
      max_concurrent: 'unlimited',
      voices: ['all'],
      engines: ['all'],
      features: ['voice_cloning', 'dedicated_support', 'sla', 'on_premise']
    }
  }
};

// Usage-based pricing
const USAGE_PRICING = {
  per_character: 0.000015,  // $0.015 per 1000 characters
  per_second_audio: 0.002,   // $0.002 per second of audio
  voice_cloning: 0.50,       // $0.50 per clone request
  priority_processing: 2.0    // 2x cost for priority
};
```

### Stripe Integration

```javascript
// billing.js
const stripe = require('stripe')(process.env.STRIPE_SECRET_KEY);

async function createSubscription(customerId, planId) {
  const plan = PRICING_PLANS[planId];
  
  // Create Stripe subscription
  const subscription = await stripe.subscriptions.create({
    customer: customerId,
    items: [{ price: plan.stripe_price_id }],
    trial_period_days: 14
  });
  
  // Save to database
  await pool.query(`
    INSERT INTO subscriptions (customer_id, plan, price_monthly, start_date)
    VALUES ($1, $2, $3, NOW())
  `, [customerId, planId, plan.price]);
  
  return subscription;
}

async function handleUsageBasedBilling(customerId) {
  const usage = await getMonthlyUsage(customerId);
  
  const cost = 
    (usage.characters * USAGE_PRICING.per_character) +
    (usage.audio_seconds * USAGE_PRICING.per_second_audio) +
    (usage.voice_clones * USAGE_PRICING.voice_cloning);
  
  // Create invoice
  await stripe.invoiceItems.create({
    customer: customerId,
    amount: Math.round(cost * 100), // cents
    currency: 'usd',
    description: `TTS API Usage - ${usage.characters.toLocaleString()} characters`
  });
}
```

---

## 👥 Client Onboarding

### Self-Service Signup Flow

```javascript
// signup-api.js

app.post('/api/v1/auth/signup', async (req, res) => {
  const { email, password, company_name } = req.body;
  
  try {
    // Validate email
    if (!isValidEmail(email)) {
      return res.status(400).json({ error: 'Invalid email' });
    }
    
    // Check if user exists
    const existing = await pool.query(
      'SELECT id FROM customers WHERE email = $1',
      [email]
    );
    
    if (existing.rows.length > 0) {
      return res.status(400).json({ error: 'Email already registered' });
    }
    
    // Hash password
    const passwordHash = await bcrypt.hash(password, 10);
    
    // Create customer
    const customer = await pool.query(`
      INSERT INTO customers (email, password_hash, company_name, plan, status)
      VALUES ($1, $2, $3, 'free', 'active')
      RETURNING id, email, company_name, plan
    `, [email, passwordHash, company_name]);
    
    // Generate API key
    const apiKey = `vtts_${crypto.randomBytes(32).toString('hex')}`;
    await pool.query(`
      INSERT INTO api_keys (customer_id, key, name, rate_limit)
      VALUES ($1, $2, 'Default Key', 10)
    `, [customer.rows[0].id, apiKey]);
    
    // Send welcome email
    await sendWelcomeEmail(email, apiKey);
    
    // Create Stripe customer
    const stripeCustomer = await stripe.customers.create({
      email: email,
      metadata: { customer_id: customer.rows[0].id }
    });
    
    res.json({
      customer: customer.rows[0],
      api_key: apiKey,
      message: 'Account created successfully'
    });
    
  } catch (error) {
    console.error('Signup error:', error);
    res.status(500).json({ error: 'Signup failed' });
  }
});
```

### Welcome Email Template

```javascript
// email-templates.js

async function sendWelcomeEmail(email, apiKey) {
  const template = `
<!DOCTYPE html>
<html>
<head>
  <style>
    body { font-family: Arial, sans-serif; line-height: 1.6; }
    .container { max-width: 600px; margin: 0 auto; padding: 20px; }
    .header { background: #4CAF50; color: white; padding: 20px; text-align: center; }
    .content { padding: 20px; background: #f9f9f9; }
    .api-key { background: #fff; border: 2px solid #4CAF50; padding: 15px; margin: 20px 0; font-family: monospace; }
    .button { display: inline-block; padding: 12px 24px; background: #4CAF50; color: white; text-decoration: none; border-radius: 4px; }
  </style>
</head>
<body>
  <div class="container">
    <div class="header">
      <h1>🎙️ Welcome to Voice TTS API!</h1>
    </div>
    
    <div class="content">
      <h2>Your API Key</h2>
      <div class="api-key">${apiKey}</div>
      
      <h3>Quick Start</h3>
      <pre>
curl -X POST https://api.yourcompany.com/api/v1/lightning/get_speech \\
  -H "Authorization: Bearer ${apiKey}" \\
  -H "Content-Type: application/json" \\
  -d '{"text": "Hello world", "voice_id": "en-US-lessac-medium"}'
      </pre>
      
      <p>
        <a href="https://docs.yourcompany.com" class="button">View Documentation</a>
      </p>
      
      <h3>Free Plan Includes:</h3>
      <ul>
        <li>10,000 characters per month</li>
        <li>10 requests per minute</li>
        <li>Access to Piper engine (fastest)</li>
        <li>40+ voices</li>
      </ul>
      
      <p>Upgrade anytime for more features!</p>
    </div>
  </div>
</body>
</html>
  `;
  
  // Send via SendGrid, AWS SES, etc.
  await sendEmail({
    to: email,
    subject: 'Welcome to Voice TTS API - Your API Key',
    html: template
  });
}
```

---

## 📊 Monitoring & Analytics

### Metrics to Track

```javascript
// metrics.js
const prometheus = require('prom-client');

// Request metrics
const httpRequestDuration = new prometheus.Histogram({
  name: 'http_request_duration_seconds',
  help: 'Duration of HTTP requests in seconds',
  labelNames: ['method', 'route', 'status_code']
});

// TTS metrics
const ttsGenerationDuration = new prometheus.Histogram({
  name: 'tts_generation_duration_seconds',
  help: 'Duration of TTS generation',
  labelNames: ['engine', 'voice_id']
});

const ttsRequestsTotal = new prometheus.Counter({
  name: 'tts_requests_total',
  help: 'Total number of TTS requests',
  labelNames: ['customer_id', 'engine', 'status']
});

// Character usage
const charactersProcessed = new prometheus.Counter({
  name: 'characters_processed_total',
  help: 'Total characters processed',
  labelNames: ['customer_id', 'engine']
});

// Export metrics endpoint
app.get('/metrics', async (req, res) => {
  res.set('Content-Type', prometheus.register.contentType);
  res.end(await prometheus.register.metrics());
});
```

### Grafana Dashboard

Create `grafana-dashboard.json`:

```json
{
  "dashboard": {
    "title": "Voice TTS API Metrics",
    "panels": [
      {
        "title": "Requests per Minute",
        "targets": [{
          "expr": "rate(tts_requests_total[1m])"
        }]
      },
      {
        "title": "Average Response Time",
        "targets": [{
          "expr": "rate(http_request_duration_seconds_sum[5m]) / rate(http_request_duration_seconds_count[5m])"
        }]
      },
      {
        "title": "Characters Processed",
        "targets": [{
          "expr": "sum(rate(characters_processed_total[1h]))"
        }]
      },
      {
        "title": "Engine Distribution",
        "targets": [{
          "expr": "sum by (engine) (rate(tts_requests_total[5m]))"
        }]
      }
    ]
  }
}
```

---

## 📈 Scaling Strategy

### 1. Horizontal Scaling

```bash
# Scale API servers
docker-compose up -d --scale api-server=5

# Scale TTS workers
docker-compose up -d --scale tts-worker=10
```

### 2. Auto-Scaling (Kubernetes)

```yaml
# k8s/hpa.yaml
apiVersion: autoscaling/v2
kind: HorizontalPodAutoscaler
metadata:
  name: tts-worker
spec:
  scaleTargetRef:
    apiVersion: apps/v1
    kind: Deployment
    name: tts-worker
  minReplicas: 2
  maxReplicas: 20
  metrics:
  - type: Resource
    resource:
      name: cpu
      target:
        type: Utilization
        averageUtilization: 70
  - type: Pods
    pods:
      metric:
        name: queue_length
      target:
        type: AverageValue
        averageValue: "10"
```

### 3. CDN Integration (Cloudflare)

```javascript
// Upload to CDN
async function uploadToCloudflare(audioBuffer, filename) {
  const formData = new FormData();
  formData.append('file', audioBuffer, filename);
  
  const response = await fetch('https://api.cloudflare.com/client/v4/accounts/{account_id}/storage/kv/namespaces/{namespace_id}/values/{key}', {
    method: 'PUT',
    headers: {
      'Authorization': `Bearer ${process.env.CLOUDFLARE_API_TOKEN}`
    },
    body: audioBuffer
  });
  
  return `https://cdn.yourcompany.com/audio/${filename}`;
}
```

### 4. Database Optimization

```sql
-- Partitioning for large tables
CREATE TABLE usage_logs_2024_01 PARTITION OF usage_logs
FOR VALUES FROM ('2024-01-01') TO ('2024-02-01');

-- Materialized views for analytics
CREATE MATERIALIZED VIEW daily_usage_stats AS
SELECT 
  customer_id,
  DATE(timestamp) as date,
  SUM(characters) as total_characters,
  COUNT(*) as total_requests,
  SUM(cost) as total_cost
FROM usage_logs
GROUP BY customer_id, DATE(timestamp);

-- Refresh periodically
REFRESH MATERIALIZED VIEW daily_usage_stats;
```

---

## 🎯 Go-to-Market Checklist

### Pre-Launch
- [ ] Production infrastructure deployed
- [ ] API documentation published
- [ ] Pricing plans finalized
- [ ] Payment integration tested
- [ ] SSL certificates installed
- [ ] Monitoring dashboards setup
- [ ] Customer support system ready

### Launch
- [ ] Landing page live
- [ ] Self-service signup working
- [ ] Email notifications configured
- [ ] API keys generated automatically
- [ ] Usage tracking verified
- [ ] Billing system tested

### Post-Launch
- [ ] Monitor error rates
- [ ] Track signup conversions
- [ ] Collect customer feedback
- [ ] Optimize performance
- [ ] Add new features
- [ ] Scale infrastructure as needed

---

## 📚 Next Steps

1. **Deploy to Production**: Follow the Docker setup
2. **Set Up Monitoring**: Configure Grafana dashboards
3. **Enable Billing**: Integrate Stripe
4. **Launch Website**: Create landing page
5. **Start Marketing**: Reach out to potential customers

---

**You now have everything needed to launch a commercial TTS API service!** 🚀

Need help with specific aspects? Check the individual integration guides or open an issue.
