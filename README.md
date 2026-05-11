# Legacy Digital Asset Reporting Pipeline Migration

Digital Asset Reporting ETL is a small Python pipeline that converts legacy digital-asset trade exports into a structured SQLite reporting database. It focuses on reliable ETL design, data validation, rejected-record auditing, idempotent loading, pipeline-run tracking, and SQL-based reporting.

## Tech Stack

- Python 3 standard library
- SQLite
- SQL
- No frontend

## Project Structure

```text
legacy-digital-asset-reporting-etl/
  data/
    legacy_trades.csv
  src/
    extract.py
    transform.py
    load.py
    db.py
    pipeline.py
  sql/
    schema.sql
    analytics_queries.sql
  README.md
  requirements.txt
```

## How to Run

From this project directory:

```bash
python src/pipeline.py
```

The pipeline creates a local SQLite database named `reporting.db` in the project directory.

To inspect loaded trades:

```bash
sqlite3 reporting.db "SELECT * FROM trades;"
```

To run the reporting query:

```bash
sqlite3 reporting.db < sql/analytics_queries.sql
```

## ETL Architecture

### 1. Extract

`src/extract.py` reads raw legacy trade records from `data/legacy_trades.csv` using `csv.DictReader`.

### 2. Transform

`src/transform.py` validates, normalizes, and enriches each raw record.

The transform step:

- Requires `trade_id`
- Requires `symbol`
- Requires `trade_timestamp`
- Requires `price > 0`
- Requires `quantity > 0`
- Standardizes symbols such as `BTC/USD` into `BTC-USD`
- Calculates `notional_value = price * quantity`
- Adds `trade_date` for daily reporting
- Separates invalid records with clear rejection reasons

### 3. Load

`src/load.py` loads valid records into SQLite and rejected records into a separate audit table.

Valid trades are inserted with `INSERT OR IGNORE`, while `trade_id` is the primary key. This makes the load idempotent and prevents duplicate trades from being inserted when the pipeline is rerun.

### 4. Run Logging

Each execution writes a row to `pipeline_runs` with:

- Run timestamp
- Rows extracted
- Rows loaded
- Rows rejected
- Duplicate rows skipped

## Database Schema

The schema is defined in `sql/schema.sql`.

### `trades`

Stores valid normalized trades.

Key fields:

- `trade_id` primary key
- `symbol`
- `trade_timestamp`
- `trade_date`
- `side`
- `price`
- `quantity`
- `notional_value`
- `exchange`
- `loaded_at`

### `rejected_records`

Stores invalid raw records for data-quality review.

Key fields:

- `rejected_id` primary key
- `rejected_at`
- `row_number`
- `trade_id`
- `raw_record`
- `rejection_reason`

### `pipeline_runs`

Stores operational metadata about every ETL run.

Key fields:

- `run_id` primary key
- `run_timestamp`
- `rows_extracted`
- `rows_loaded`
- `rows_rejected`
- `duplicate_rows_skipped`

### `daily_trading_volume_by_symbol`

A reporting view that aggregates daily trading activity by symbol:

- `symbol`
- `trade_date`
- `trade_count`
- `total_quantity`
- `total_notional`

## Data-Quality Checks

The sample legacy CSV intentionally includes realistic migration issues:

- Valid BTC trades
- Valid ETH trades
- One duplicate `trade_id`
- One missing symbol
- One negative price
- One zero quantity
- One malformed symbol, `BTC/USD`, that is standardized to `BTC-USD`

Invalid rows are not silently dropped. They are stored in `rejected_records` with the exact rejection reason so analysts or operations teams can review and remediate source-system issues.

## Idempotency and Duplicate Prevention

The pipeline is safe to rerun.

Duplicate prevention is handled by two design choices:

1. `trade_id` is the primary key in the `trades` table.
2. Valid records are loaded with `INSERT OR IGNORE`.

On the first run, the first occurrence of a valid `trade_id` is inserted and the duplicate row is skipped. On later reruns, already-loaded trades are skipped instead of duplicated. The number of skipped duplicates is logged in `pipeline_runs`.

## Reporting Queries

`sql/analytics_queries.sql` includes a daily trading volume report:

```sql
SELECT
    symbol,
    trade_date,
    trade_count,
    total_quantity,
    total_notional
FROM daily_trading_volume_by_symbol
ORDER BY trade_date, symbol;
```

This query supports reporting use cases such as daily dashboard metrics, reconciliation checks, and volume monitoring by digital asset pair.

## How This Models Legacy Reporting Migration

This project models a common migration pattern: a legacy reporting process exports flat files, while a new reporting platform needs clean, queryable, auditable SQL tables.

The pipeline demonstrates how to:

- Move raw CSV data into a structured database
- Normalize inconsistent legacy formats
- Enforce data integrity during loading
- Preserve rejected records instead of losing them
- Make reruns safe through idempotent database writes
- Produce reporting-ready SQL views
- Track operational metrics for each pipeline run

## What I Would Improve Next

If this were extended into a production-style pipeline, I would add:

- Unit tests for validation and loading behavior
- A command-line argument for custom source and database paths
- Structured JSON logging
- A batch/run identifier on rejected records
- More robust timestamp parsing and timezone validation
- Referential tables for exchanges, symbols, and asset metadata
- Docker Compose for reproducible local execution
- CI checks for linting, formatting, and tests
- Data reconciliation reports between source files and database tables

## Project Summary

This project implements a compact Python and SQLite ETL pipeline for migrating legacy digital-asset trade exports into a structured reporting database. The pipeline extracts raw CSV trades, validates data-quality rules, standardizes legacy symbols like `BTC/USD`, calculates notional value, loads valid rows idempotently using `trade_id` as a primary key, and stores rejected rows with reasons. It also logs each pipeline run and provides a SQL reporting view for daily trading volume by symbol.
