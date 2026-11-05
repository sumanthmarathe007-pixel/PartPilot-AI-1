from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Optional


class Freshness(str, Enum):
    RECENT = "recent"
    AGED = "aged"
    UNKNOWN = "unknown"


class StockStatus(str, Enum):
    AVAILABLE = "available"
    UNAVAILABLE = "unavailable"
    UNKNOWN = "unknown"


class DecisionKind(str, Enum):
    DISPATCH = "dispatch"
    ESCALATE = "escalate"
    UNDECIDED = "undecided"


@dataclass
class ElectricalSpec:
    """Normalized technical requirement/specification. None means unknown, not wildcard."""
    voltage_v: Optional[float] = None
    connector: Optional[str] = None
    min_wattage_w: Optional[float] = None
    # True when customer wording leaves this field unresolved.
    ambiguous_fields: list[str] = field(default_factory=list)
    raw_text: str = ""
    confidence: dict[str, float] = field(default_factory=dict)


@dataclass
class PartRecord:
    part_id: str
    description: str
    spec: ElectricalSpec
    snapshot_stock: StockStatus = StockStatus.UNKNOWN
    freshness: Freshness = Freshness.UNKNOWN
    # Retain original organizer record for the protocol adapter.
    raw: dict[str, Any] = field(default_factory=dict)


@dataclass
class RequestRecord:
    request_id: str
    text: str
    spec: ElectricalSpec
    raw: dict[str, Any] = field(default_factory=dict)


@dataclass
class EvidenceRecord:
    subject_id: str
    field: str
    value: Any
    source: str
    # Examples: request_text, catalogue_description, inspect_recent,
    # inspect_aged, clarify_reply, warehouse_verify.
    authoritative: bool = False
    details: str = ""


@dataclass
class PartPilotState:
    remaining_tool_units: int = 14
    tool_units_spent: int = 0
    action_count: int = 0
    max_actions: int = 60
    evidence: list[EvidenceRecord] = field(default_factory=list)
    reserved_part_ids: set[str] = field(default_factory=set)
    decisions: dict[str, str] = field(default_factory=dict)
    # Store organizer-specific state here through the adapter.
    protocol_state: dict[str, Any] = field(default_factory=dict)


@dataclass
class CandidateAssessment:
    part_id: str
    compatible: bool
    reasons: list[str]
    stock_status: StockStatus
    stock_needs_verification: bool
    safe_to_dispatch: bool


@dataclass
class ProposedDecision:
    request_id: str
    kind: DecisionKind
    part_id: Optional[str] = None
    reason: str = ""

