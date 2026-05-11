-- Daily trading volume by symbol for reporting dashboards.
SELECT
    symbol,
    trade_date,
    trade_count,
    total_quantity,
    total_notional
FROM daily_trading_volume_by_symbol
ORDER BY trade_date, symbol;

-- Latest pipeline run metrics for operational monitoring.
SELECT
    run_id,
    run_timestamp,
    rows_extracted,
    rows_loaded,
    rows_rejected,
    duplicate_rows_skipped
FROM pipeline_runs
ORDER BY run_id DESC
LIMIT 5;

-- Rejected records by data-quality rule.
SELECT
    rejection_reason,
    COUNT(*) AS rejected_count
FROM rejected_records
GROUP BY rejection_reason
ORDER BY rejected_count DESC;
