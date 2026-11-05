from __future__ import annotations

from .models import EvidenceRecord, Freshness, StockStatus


def record_evidence(evidence: list[EvidenceRecord], subject_id: str, field: str,
                    value, source: str, authoritative: bool = False, details: str = "") -> None:
    evidence.append(EvidenceRecord(
        subject_id=subject_id,
        field=field,
        value=value,
        source=source,
        authoritative=authoritative,
        details=details,
    ))


def stock_from_evidence(evidence: list[EvidenceRecord], part_id: str,
                        freshness: Freshness) -> StockStatus:
    """Return latest usable stock fact. Verify is authoritative; recent snapshot is trusted.

    Aged snapshot deliberately returns UNKNOWN here until verification is recorded.
    """
    for item in reversed(evidence):
        if item.subject_id != part_id or item.field != "stock":
            continue
        if item.source == "warehouse_verify" and item.authoritative:
            try:
                return StockStatus(str(item.value).lower())
            except ValueError:
                return StockStatus.UNKNOWN
        if item.source == "inspect_recent" and freshness == Freshness.RECENT:
            try:
                return StockStatus(str(item.value).lower())
            except ValueError:
                return StockStatus.UNKNOWN
    return StockStatus.UNKNOWN
