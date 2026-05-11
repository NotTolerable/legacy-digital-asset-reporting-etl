"""Command-line entry point for the legacy digital-asset reporting ETL pipeline."""

from __future__ import annotations

import logging

from db import get_connection, initialize_database
from extract import DEFAULT_SOURCE_FILE, extract_trades
from load import load_rejected_records, load_trades, log_pipeline_run
from transform import transform_trades


logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
LOGGER = logging.getLogger(__name__)


def run_pipeline() -> None:
    """Run extract, transform, load, and operational audit logging steps."""
    LOGGER.info("Starting legacy digital-asset reporting ETL pipeline")
    LOGGER.info("Extracting raw trades from %s", DEFAULT_SOURCE_FILE)
    raw_records = extract_trades()
    LOGGER.info("Rows extracted: %s", len(raw_records))

    transform_result = transform_trades(raw_records)
    LOGGER.info("Valid transformed rows: %s", len(transform_result.valid_records))
    LOGGER.info("Rejected rows: %s", len(transform_result.rejected_records))

    with get_connection() as connection:
        initialize_database(connection)
        rows_loaded, duplicate_rows_skipped = load_trades(connection, transform_result.valid_records)
        rows_rejected = load_rejected_records(connection, transform_result.rejected_records)
        log_pipeline_run(
            connection=connection,
            rows_extracted=len(raw_records),
            rows_loaded=rows_loaded,
            rows_rejected=rows_rejected,
            duplicate_rows_skipped=duplicate_rows_skipped,
        )
        connection.commit()

    LOGGER.info("Rows loaded: %s", rows_loaded)
    LOGGER.info("Duplicate rows skipped: %s", duplicate_rows_skipped)
    LOGGER.info("Rejected rows stored: %s", rows_rejected)
    LOGGER.info("Pipeline completed successfully")


if __name__ == "__main__":
    run_pipeline()
