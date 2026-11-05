from __future__ import annotations


class InventoryLedger:
    """Batch-wide one-unit reservation tracker."""

    def __init__(self, initial_part_ids=()):
        self.initial_part_ids = set(initial_part_ids)
        self.reserved_part_ids: set[str] = set()

    def is_reserved(self, part_id: str) -> bool:
        return part_id in self.reserved_part_ids

    def reserve_after_successful_dispatch(self, part_id: str) -> None:
        if part_id in self.reserved_part_ids:
            raise ValueError(f"Part {part_id} has already been dispatched/reserved")
        if self.initial_part_ids and part_id not in self.initial_part_ids:
            raise ValueError(f"Unknown part id: {part_id}")
        self.reserved_part_ids.add(part_id)

    def available_to_this_batch(self, part_id: str) -> bool:
        return part_id not in self.reserved_part_ids
