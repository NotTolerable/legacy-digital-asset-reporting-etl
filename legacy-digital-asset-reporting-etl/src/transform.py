"""Validate and normalize legacy trade records."""

from __future__ import annotations

from dataclasses import dataclass
from decimal import Decimal, InvalidOperation
from typing import Dict, Iterable, List


@dataclass(frozen=True)
class TransformResult:
    """Container for valid transformed rows and rejected legacy rows."""

    valid_records: List[Dict[str, object]]
    rejected_records: List[Dict[str, str]]


def standardize_symbol(symbol: str) -> str:
    """Normalize legacy symbol formats, for example BTC/USD -> BTC-USD."""
    return symbol.strip().upper().replace("/", "-")


def _parse_positive_decimal(value: str, field_name: str, reasons: List[str]) -> Decimal:
    try:
        parsed = Decimal(value)
    except (InvalidOperation, TypeError):
        reasons.append(f"{field_name} must be numeric")
        return Decimal("0")

    if parsed <= 0:
        reasons.append(f"{field_name} must be greater than 0")
    return parsed


def transform_trades(records: Iterable[Dict[str, str]]) -> TransformResult:
    """Validate, standardize, and enrich raw legacy trade records."""
    valid_records: List[Dict[str, object]] = []
    rejected_records: List[Dict[str, str]] = []

    for row_number, record in enumerate(records, start=2):
        reasons: List[str] = []
        trade_id = (record.get("trade_id") or "").strip()
        symbol = (record.get("symbol") or "").strip()
        timestamp = (record.get("trade_timestamp") or "").strip()
        side = (record.get("side") or "").strip().lower()
        exchange = (record.get("exchange") or "").strip()

        if not trade_id:
            reasons.append("trade_id is required")
        if not symbol:
            reasons.append("symbol is required")
        if not timestamp:
            reasons.append("trade_timestamp is required")

        price = _parse_positive_decimal(record.get("price", ""), "price", reasons)
        quantity = _parse_positive_decimal(record.get("quantity", ""), "quantity", reasons)

        if reasons:
            rejected = dict(record)
            rejected["row_number"] = str(row_number)
            rejected["rejection_reason"] = "; ".join(reasons)
            rejected_records.append(rejected)
            continue

        standardized_symbol = standardize_symbol(symbol)
        notional_value = price * quantity
        trade_date = timestamp[:10]

        valid_records.append(
            {
                "trade_id": trade_id,
                "symbol": standardized_symbol,
                "trade_timestamp": timestamp,
                "trade_date": trade_date,
                "side": side,
                "price": str(price),
                "quantity": str(quantity),
                "notional_value": str(notional_value),
                "exchange": exchange,
            }
        )

    return TransformResult(valid_records=valid_records, rejected_records=rejected_records)
