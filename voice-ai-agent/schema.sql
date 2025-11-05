-- Voice AI Contact Center Database Schema

-- Customers table
CREATE TABLE customers (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    phone_number VARCHAR(20) UNIQUE NOT NULL,
    email VARCHAR(255),
    name VARCHAR(255),
    metadata JSONB DEFAULT '{}',
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

-- Calls table
CREATE TABLE calls (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    call_sid VARCHAR(255) UNIQUE NOT NULL,
    customer_id UUID REFERENCES customers(id),
    direction VARCHAR(20) NOT NULL, -- 'inbound' or 'outbound'
    from_number VARCHAR(20),
    to_number VARCHAR(20),
    status VARCHAR(50), -- 'initiated', 'ringing', 'in-progress', 'completed', 'failed'
    duration INT, -- in seconds
    recording_url TEXT,
    started_at TIMESTAMP DEFAULT NOW(),
    ended_at TIMESTAMP,
    metadata JSONB DEFAULT '{}'
);

-- Conversation messages
CREATE TABLE messages (
    id BIGSERIAL PRIMARY KEY,
    call_id UUID REFERENCES calls(id) ON DELETE CASCADE,
    role VARCHAR(20) NOT NULL, -- 'user' or 'assistant'
    content TEXT NOT NULL,
    confidence FLOAT,
    timestamp TIMESTAMP DEFAULT NOW(),
    metadata JSONB DEFAULT '{}'
);

-- Transcripts (full call transcription)
CREATE TABLE transcripts (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    call_id UUID REFERENCES calls(id) ON DELETE CASCADE,
    full_text TEXT,
    language VARCHAR(10),
    created_at TIMESTAMP DEFAULT NOW()
);

-- Function calls (AI actions)
CREATE TABLE function_calls (
    id BIGSERIAL PRIMARY KEY,
    call_id UUID REFERENCES calls(id) ON DELETE CASCADE,
    function_name VARCHAR(100) NOT NULL,
    arguments JSONB,
    result JSONB,
    executed_at TIMESTAMP DEFAULT NOW()
);

-- Call analytics
CREATE TABLE call_analytics (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    call_id UUID REFERENCES calls(id) ON DELETE CASCADE,
    sentiment VARCHAR(20), -- 'positive', 'negative', 'neutral'
    intent VARCHAR(100),
    resolution VARCHAR(50), -- 'resolved', 'escalated', 'abandoned'
    customer_satisfaction INT CHECK (customer_satisfaction BETWEEN 1 AND 5),
    ai_confidence FLOAT,
    response_time_avg INT, -- average response time in ms
    metadata JSONB DEFAULT '{}',
    created_at TIMESTAMP DEFAULT NOW()
);

-- System metrics (aggregated)
CREATE TABLE metrics (
    id BIGSERIAL PRIMARY KEY,
    date DATE NOT NULL,
    metric_type VARCHAR(50) NOT NULL,
    metric_name VARCHAR(100) NOT NULL,
    value NUMERIC,
    metadata JSONB DEFAULT '{}',
    created_at TIMESTAMP DEFAULT NOW(),
    UNIQUE(date, metric_type, metric_name)
);

-- API keys for integration
CREATE TABLE api_keys (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    key VARCHAR(255) UNIQUE NOT NULL,
    name VARCHAR(255),
    customer_id UUID REFERENCES customers(id),
    permissions JSONB DEFAULT '{}',
    active BOOLEAN DEFAULT true,
    created_at TIMESTAMP DEFAULT NOW(),
    last_used_at TIMESTAMP
);

-- Indexes for performance
CREATE INDEX idx_calls_customer ON calls(customer_id);
CREATE INDEX idx_calls_status ON calls(status);
CREATE INDEX idx_calls_started_at ON calls(started_at);
CREATE INDEX idx_messages_call ON messages(call_id);
CREATE INDEX idx_messages_timestamp ON messages(timestamp);
CREATE INDEX idx_analytics_call ON call_analytics(call_id);
CREATE INDEX idx_analytics_sentiment ON call_analytics(sentiment);
CREATE INDEX idx_metrics_date ON metrics(date);
CREATE INDEX idx_customers_phone ON customers(phone_number);

-- Views for common queries

-- Active calls view
CREATE VIEW active_calls AS
SELECT 
    c.*,
    cu.name as customer_name,
    cu.phone_number as customer_phone
FROM calls c
LEFT JOIN customers cu ON c.customer_id = cu.id
WHERE c.status IN ('initiated', 'ringing', 'in-progress');

-- Daily statistics view
CREATE VIEW daily_stats AS
SELECT 
    DATE(started_at) as date,
    COUNT(*) as total_calls,
    COUNT(CASE WHEN status = 'completed' THEN 1 END) as completed_calls,
    COUNT(CASE WHEN status = 'failed' THEN 1 END) as failed_calls,
    AVG(duration) as avg_duration,
    SUM(duration) as total_duration
FROM calls
WHERE started_at >= CURRENT_DATE - INTERVAL '30 days'
GROUP BY DATE(started_at)
ORDER BY date DESC;

-- Customer activity view
CREATE VIEW customer_activity AS
SELECT 
    cu.id,
    cu.name,
    cu.phone_number,
    COUNT(c.id) as total_calls,
    MAX(c.started_at) as last_call_at,
    AVG(ca.customer_satisfaction) as avg_satisfaction,
    COUNT(CASE WHEN ca.sentiment = 'positive' THEN 1 END) as positive_calls,
    COUNT(CASE WHEN ca.sentiment = 'negative' THEN 1 END) as negative_calls
FROM customers cu
LEFT JOIN calls c ON cu.id = c.customer_id
LEFT JOIN call_analytics ca ON c.id = ca.call_id
GROUP BY cu.id, cu.name, cu.phone_number;

-- Functions

-- Update customer updated_at timestamp
CREATE OR REPLACE FUNCTION update_updated_at()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER update_customers_updated_at
    BEFORE UPDATE ON customers
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at();

-- Auto-create customer on new call
CREATE OR REPLACE FUNCTION create_customer_if_not_exists()
RETURNS TRIGGER AS $$
BEGIN
    IF NEW.from_number IS NOT NULL THEN
        INSERT INTO customers (phone_number)
        VALUES (NEW.from_number)
        ON CONFLICT (phone_number) DO NOTHING;
        
        -- Set customer_id
        SELECT id INTO NEW.customer_id
        FROM customers
        WHERE phone_number = NEW.from_number;
    END IF;
    
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER auto_create_customer
    BEFORE INSERT ON calls
    FOR EACH ROW
    EXECUTE FUNCTION create_customer_if_not_exists();

-- Sample data (for testing)

-- Insert sample customers
INSERT INTO customers (phone_number, email, name) VALUES
('+1234567890', 'john@example.com', 'John Doe'),
('+0987654321', 'jane@example.com', 'Jane Smith');

-- Sample metrics
INSERT INTO metrics (date, metric_type, metric_name, value) VALUES
(CURRENT_DATE, 'calls', 'total', 100),
(CURRENT_DATE, 'calls', 'completed', 85),
(CURRENT_DATE, 'calls', 'failed', 15),
(CURRENT_DATE, 'performance', 'avg_response_time_ms', 800),
(CURRENT_DATE, 'satisfaction', 'avg_rating', 4.2);
