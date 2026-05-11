"""Load transformed trade data and rejected rows into SQLite."""

from __future__ import annotations

import json
import sqlite3
from datetime import datetime, timezone
from typing import Dict, Iterable, Tuple


TRADE_COLUMNS = (
    "trade_id",
    "symbol",
    "trade_timestamp",
    "trade_date",
    "side",
    "price",
    "quantity",
    "notional_value",
    "exchange",
)


def load_trades(connection: sqlite3.Connection, valid_records: Iterable[Dict[str, object]]) -> Tuple[int, int]:
    """Insert valid trades idempotently and return loaded and duplicate counts."""
    loaded_count = 0
    duplicate_count = 0

    sql = f"""
        INSERT OR IGNORE INTO trades ({", ".join(TRADE_COLUMNS)})
        VALUES ({", ".join([":" + column for column in TRADE_COLUMNS])})
    """

    for record in valid_records:
        cursor = connection.execute(sql, record)
        if cursor.rowcount == 1:
            loaded_count += 1
        else:
            duplicate_count += 1

    return loaded_count, duplicate_count


def load_rejected_records(connection: sqlite3.Connection, rejected_records: Iterable[Dict[str, str]]) -> int:
    """Persist rejected legacy records and their validation failure reasons."""
    rejected_count = 0
    rejected_at = datetime.now(timezone.utc).isoformat()

    for record in rejected_records:
        connection.execute(
            """
            INSERT INTO rejected_records (
                rejected_at,
                row_number,
                trade_id,
                raw_record,
                rejection_reason
            ) VALUES (?, ?, ?, ?, ?)
            """,
            (
                rejected_at,
                record.get("row_number"),
                record.get("trade_id"),
                json.dumps(record, sort_keys=True),
                record.get("rejection_reason"),
            ),
        )
        rejected_count += 1

    return rejected_count


def log_pipeline_run(
    connection: sqlite3.Connection,
    rows_extracted: int,
    rows_loaded: int,
    rows_rejected: int,
    duplicate_rows_skipped: int,
) -> None:
    """Record pipeline run metrics for operational visibility."""
    connection.execute(
        """
        INSERT INTO pipeline_runs (
            run_timestamp,
            rows_extracted,
            rows_loaded,
            rows_rejected,
            duplicate_rows_skipped
        ) VALUES (?, ?, ?, ?, ?)
        """,
        (
            datetime.now(timezone.utc).isoformat(),
            rows_extracted,
            rows_loaded,
            rows_rejected,
            duplicate_rows_skipped,
        ),
    )
