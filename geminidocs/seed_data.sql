-- Seed Watchlist for Sovereign Node (Bi-Modal)
-- Run this in your Supabase SQL Editor AFTER running schema.sql

-- 🛡️ THE TANK (Core 70%) - High Liquidity, Institutional Focus
INSERT INTO watchlist (ticker, market, bucket) VALUES
('THYAO.IS', 'BIST', 'CORE'),
('TUPRS.IS', 'BIST', 'CORE'),
('KCHOL.IS', 'BIST', 'CORE'),
('AKBNK.IS', 'BIST', 'CORE'),
('BIMAS.IS', 'BIST', 'CORE'),
('AAPL', 'US', 'CORE'),
('MSFT', 'US', 'CORE')
ON CONFLICT (ticker) DO UPDATE SET bucket = EXCLUDED.bucket, market = EXCLUDED.market;

-- 🚀 THE SNIPER (Satellite 30%) - High Volatility, Growth Focus
INSERT INTO watchlist (ticker, market, bucket) VALUES
('MIATK.IS', 'BIST', 'SATELLITE'),
('KONTR.IS', 'BIST', 'SATELLITE'),
('ASTOR.IS', 'BIST', 'SATELLITE'),
('YEOTK.IS', 'BIST', 'SATELLITE'),
('NVDA', 'US', 'SATELLITE'),
('TSLA', 'US', 'SATELLITE')
ON CONFLICT (ticker) DO UPDATE SET bucket = EXCLUDED.bucket, market = EXCLUDED.market;
