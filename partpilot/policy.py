from __future__ import annotations

from .models import PartRecord, RequestRecord, CandidateAssessment, StockStatus, Freshness
from .compatibility import assess_candidate


def rank_candidates(request: RequestRecord, parts: list[PartRecord], reserved: set[str],
                    verified_stock: dict[str, StockStatus] | None = None) -> list[CandidateAssessment]:
    """Sort safe/reliable choices first; do not rank technical mismatches as dispatchable."""
    verified_stock = verified_stock or {}
    assessments = [
        assess_candidate(request.spec, p, reserved, verified_stock.get(p.part_id))
        for p in parts
    ]

    def key(a: CandidateAssessment):
        # Safe, compatible+needs-verification, then incompatible/unavailable.
        return (
            0 if a.safe_to_dispatch else 1,
            0 if a.compatible else 1,
            0 if not a.stock_needs_verification else 1,
            a.part_id,
        )

    return sorted(assessments, key=key)


def decide_after_evidence(request: RequestRecord, parts: list[PartRecord], reserved: set[str],
                          verified_stock: dict[str, StockStatus] | None = None) -> tuple[str, str | None, str]:
    ranked = rank_candidates(request, parts, reserved, verified_stock)
    safe = next((x for x in ranked if x.safe_to_dispatch), None)
    if safe:
        return "dispatch", safe.part_id, "All technical fields match and stock is confirmed available."

    technically_compatible = next((x for x in ranked if x.compatible), None)
    if technically_compatible:
        return "needs_stock_evidence", technically_compatible.part_id, \
            "A technically compatible candidate exists, but stock is not authoritatively confirmed."

    return "escalate", None, "No candidate has fully proven voltage, connector and wattage compatibility."
