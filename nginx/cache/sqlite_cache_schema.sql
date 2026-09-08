-- =============================================================================
-- LƯỢC ĐỒ CSDL BỘ ĐỆM SQLITE CHO EDGE GATEWAY (RESPONSE CACHE)
-- =============================================================================

CREATE TABLE IF NOT EXISTS response_cache (
    cache_key TEXT PRIMARY KEY,
    endpoint TEXT NOT NULL,
    request_hash TEXT NOT NULL,
    response_payload TEXT NOT NULL,
    status_code INTEGER DEFAULT 200,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    expires_at TIMESTAMP NOT NULL
);

CREATE INDEX IF NOT EXISTS idx_cache_key ON response_cache(cache_key);
CREATE INDEX IF NOT EXISTS idx_expires_at ON response_cache(expires_at);

-- Bật chế độ Write-Ahead Logging (WAL) để tăng tốc độ ghi đồng thời
PRAGMA journal_mode = WAL;
PRAGMA synchronous = NORMAL;
