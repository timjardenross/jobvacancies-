-- Run this in Supabase SQL Editor: https://app.supabase.com → SQL Editor

-- Jobs table
CREATE TABLE IF NOT EXISTS jobs (
    id          BIGSERIAL PRIMARY KEY,
    company     TEXT NOT NULL,
    title       TEXT NOT NULL,
    url         TEXT UNIQUE NOT NULL,
    description TEXT,
    posted_date TIMESTAMPTZ,
    scraped_date TIMESTAMPTZ DEFAULT NOW(),
    source      TEXT DEFAULT 'RSS',
    sector      TEXT,
    relevance_score INT DEFAULT 0,
    is_bookmarked   BOOLEAN DEFAULT FALSE,
    created_at  TIMESTAMPTZ DEFAULT NOW()
);

-- Feed logs table
CREATE TABLE IF NOT EXISTS feed_logs (
    id           BIGSERIAL PRIMARY KEY,
    company      TEXT NOT NULL,
    feed_url     TEXT,
    status       TEXT,
    last_checked TIMESTAMPTZ DEFAULT NOW(),
    entries_found INT DEFAULT 0
);

-- Indexes for common queries
CREATE INDEX IF NOT EXISTS idx_jobs_scraped_date    ON jobs (scraped_date DESC);
CREATE INDEX IF NOT EXISTS idx_jobs_relevance_score ON jobs (relevance_score DESC);
CREATE INDEX IF NOT EXISTS idx_jobs_company         ON jobs (company);
CREATE INDEX IF NOT EXISTS idx_jobs_is_bookmarked   ON jobs (is_bookmarked) WHERE is_bookmarked = TRUE;

-- Enable Row Level Security (optional but recommended)
ALTER TABLE jobs ENABLE ROW LEVEL SECURITY;
ALTER TABLE feed_logs ENABLE ROW LEVEL SECURITY;

-- Allow anon reads (for dashboard) and service role writes (for scraper)
CREATE POLICY "Allow anon read" ON jobs FOR SELECT USING (true);
CREATE POLICY "Allow service write" ON jobs FOR ALL USING (auth.role() = 'service_role');

CREATE POLICY "Allow anon read" ON feed_logs FOR SELECT USING (true);
CREATE POLICY "Allow service write" ON feed_logs FOR ALL USING (auth.role() = 'service_role');
