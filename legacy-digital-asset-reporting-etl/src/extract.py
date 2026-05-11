"""Extract raw legacy trade records from CSV."""

from __future__ import annotations

import csv
from pathlib import Path
from typing import Dict, List


PROJECT_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_SOURCE_FILE = PROJECT_ROOT / "data" / "legacy_trades.csv"


def extract_trades(source_file: Path = DEFAULT_SOURCE_FILE) -> List[Dict[str, str]]:
    """Read raw trade records from a legacy CSV file."""
    with source_file.open("r", newline="", encoding="utf-8") as csv_file:
        reader = csv.DictReader(csv_file)
        return list(reader)
