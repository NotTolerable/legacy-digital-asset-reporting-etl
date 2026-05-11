CREATE TABLE IF NOT EXISTS trades (
    trade_id TEXT PRIMARY KEY,
    symbol TEXT NOT NULL,
    trade_timestamp TEXT NOT NULL,
    trade_date TEXT NOT NULL,
    side TEXT,
    price NUMERIC NOT NULL CHECK (price > 0),
    quantity NUMERIC NOT NULL CHECK (quantity > 0),
    notional_value NUMERIC NOT NULL,
    exchange TEXT,
    loaded_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS rejected_records (
    rejected_id INTEGER PRIMARY KEY AUTOINCREMENT,
    rejected_at TEXT NOT NULL,
    row_number INTEGER,
    trade_id TEXT,
    raw_record TEXT NOT NULL,
    rejection_reason TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS pipeline_runs (
    run_id INTEGER PRIMARY KEY AUTOINCREMENT,
    run_timestamp TEXT NOT NULL,
    rows_extracted INTEGER NOT NULL,
    rows_loaded INTEGER NOT NULL,
    rows_rejected INTEGER NOT NULL,
    duplicate_rows_skipped INTEGER NOT NULL
);

CREATE VIEW IF NOT EXISTS daily_trading_volume_by_symbol AS
SELECT
    symbol,
    trade_date,
    COUNT(*) AS trade_count,
    SUM(quantity) AS total_quantity,
    SUM(notional_value) AS total_notional
FROM trades
GROUP BY symbol, trade_date;
