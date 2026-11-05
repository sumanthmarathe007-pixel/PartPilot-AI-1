from __future__ import annotations

from .models import ElectricalSpec, CandidateAssessment, PartRecord, StockStatus, Freshness


def compatibility_check(request: ElectricalSpec, part: ElectricalSpec) -> tuple[bool, list[str]]:
    """Strict deterministic check. Unknown technical facts never count as compatible."""
    reasons: list[str] = []

    if request.voltage_v is None:
        reasons.append("request voltage is unknown")
    elif part.voltage_v is None:
        reasons.append("part voltage is unknown")
    elif request.voltage_v != part.voltage_v:
        reasons.append(f"voltage mismatch: request {request.voltage_v}V, part {part.voltage_v}V")

    if request.connector is None:
        reasons.append("request connector is unknown")
    elif part.connector is None:
        reasons.append("part connector is unknown")
    elif request.connector != part.connector:
        reasons.append(f"connector mismatch: request {request.connector}, part {part.connector}")

    if request.min_wattage_w is None:
        reasons.append("minimum request wattage is unknown")
    elif part.min_wattage_w is None:
        reasons.append("part wattage rating is unknown")
    elif part.min_wattage_w < request.min_wattage_w:
        reasons.append(
            f"insufficient wattage: request >= {request.min_wattage_w}W, part {part.min_wattage_w}W"
        )

    return len(reasons) == 0, reasons


def assess_candidate(request: ElectricalSpec, part: PartRecord, reserved: set[str],
                     verified_stock: StockStatus | None = None) -> CandidateAssessment:
    compatible, reasons = compatibility_check(request, part.spec)

    if part.part_id in reserved:
        reasons.append("part already reserved by an earlier dispatch")
        compatible = False

    stock = verified_stock if verified_stock is not None else part.snapshot_stock
    needs_verification = part.freshness != Freshness.RECENT and verified_stock is None

    # Aged/unknown snapshot is not authoritative. A recent snapshot is synchronized
    # at batch open per the challenge rules.
    stock_confirmed = (
        stock == StockStatus.AVAILABLE
        and (part.freshness == Freshness.RECENT or verified_stock == StockStatus.AVAILABLE)
    )

    safe = compatible and stock_confirmed
    if stock != StockStatus.AVAILABLE:
        reasons.append(f"stock not confirmed available ({stock.value})")
    if needs_verification:
        reasons.append("aged/unknown stock snapshot requires authoritative verification")

    return CandidateAssessment(
        part_id=part.part_id,
        compatible=compatible,
        reasons=reasons,
        stock_status=stock,
        stock_needs_verification=needs_verification,
        safe_to_dispatch=safe,
    )
