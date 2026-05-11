"""SQLite database helpers for the reporting migration pipeline."""

from __future__ import annotations

import sqlite3
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_DB_FILE = PROJECT_ROOT / "reporting.db"
SCHEMA_FILE = PROJECT_ROOT / "sql" / "schema.sql"


def get_connection(db_file: Path = DEFAULT_DB_FILE) -> sqlite3.Connection:
    """Open a SQLite connection with row access by column name."""
    connection = sqlite3.connect(db_file)
    connection.row_factory = sqlite3.Row
    return connection


def initialize_database(connection: sqlite3.Connection, schema_file: Path = SCHEMA_FILE) -> None:
    """Create reporting tables and views if they do not already exist."""
    schema_sql = schema_file.read_text(encoding="utf-8")
    connection.executescript(schema_sql)
    connection.commit()
