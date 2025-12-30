-- Sentiment Space SQLite Database Schema
-- Stores processed thoughts with summaries and sentiment analysis

CREATE TABLE IF NOT EXISTS thoughts (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    raw_text TEXT NOT NULL,
    summary TEXT,
    sentiment TEXT,
    confidence REAL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Index for faster queries
CREATE INDEX IF NOT EXISTS idx_thoughts_created_at ON thoughts(created_at DESC);
CREATE INDEX IF NOT EXISTS idx_thoughts_sentiment ON thoughts(sentiment);
