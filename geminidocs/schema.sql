-- Sovereign Node Database Schema (Bi-Modal Operator Edition)
-- Run these in the Supabase SQL Editor

-- 1. Metadata Table (The Heartbeat & Regime)
CREATE TABLE IF NOT EXISTS metadata (
    id INTEGER PRIMARY KEY DEFAULT 1,
    last_success TIMESTAMP WITH TIME ZONE,
    worker_status TEXT,
    error_log TEXT,
    bist_regime TEXT DEFAULT 'NEUTRAL', -- 'BULL' or 'BEAR'
    us_regime TEXT DEFAULT 'NEUTRAL',
    bist_adx REAL,
    us_adx REAL,
    usd_try_trend TEXT, -- 'UP' or 'DOWN'
    circuit_breaker TEXT DEFAULT 'SAFE', -- 'SAFE' or 'TRIPPED'
    capital_try REAL DEFAULT 100000.0,
    capital_usd REAL DEFAULT 10000.0,
    risk_pct REAL DEFAULT 1.0,
    CONSTRAINT single_row CHECK (id = 1)
);

-- Initialize metadata
INSERT INTO metadata (id, last_success, worker_status) 
VALUES (1, NOW(), 'INITIALIZING')
ON CONFLICT (id) DO NOTHING;

-- 2. Watchlist Table
CREATE TABLE IF NOT EXISTS watchlist (
    ticker TEXT PRIMARY KEY,
    market TEXT DEFAULT 'BIST', -- 'BIST' or 'US'
    bucket TEXT DEFAULT 'CORE',  -- 'CORE' or 'SATELLITE'
    added_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- 3. Limits Table
CREATE TABLE IF NOT EXISTS limits (
    ticker TEXT REFERENCES watchlist(ticker) ON DELETE CASCADE,
    run_date TEXT,
    bucket TEXT,
    current_price REAL,
    prev_price REAL,
    buy_limit REAL,
    sell_target REAL,
    stop_loss REAL,
    sma_200 REAL,
    sma_50 REAL,
    atr_14 REAL,
    liquidity_zone_top REAL,
    liquidity_zone_bot REAL,
    adv_20 REAL, -- 20-day Average Daily Value
    max_pos_size REAL, -- 1% ADV Cap
    cvd REAL,
    cvd_gradient REAL,
    gap_penalty_multiplier REAL,
    alpha_score REAL,
    stink_bid REAL,
    options_advice TEXT,
    status TEXT, -- 'ACTION', 'APPROACHING', 'NEUTRAL', 'REJECTED...'
    last_updated TIMESTAMP WITH TIME ZONE,
    PRIMARY KEY (ticker, run_date)
);

-- 4. Portfolio Table (Journaling)
CREATE TABLE IF NOT EXISTS portfolio (
    id SERIAL PRIMARY KEY,
    ticker TEXT REFERENCES watchlist(ticker),
    bucket TEXT,
    entry_price REAL,
    entry_date TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    qty INTEGER,
    status TEXT DEFAULT 'OPEN', 
    exit_target REAL,
    stop_loss REAL,
    exit_price REAL,
    exit_date TIMESTAMP WITH TIME ZONE,
    net_pnl REAL, -- After 0.3% friction
    notes TEXT
);

-- 5. Paper Portfolio Table (The Laboratory)
CREATE TABLE IF NOT EXISTS paper_portfolio (
    id SERIAL PRIMARY KEY,
    ticker TEXT,
    reason_for_rejection TEXT,
    paper_entry_price REAL,
    entry_date TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    paper_exit_price REAL,
    exit_date TIMESTAMP WITH TIME ZONE,
    paper_pnl REAL,
    notes TEXT
);
