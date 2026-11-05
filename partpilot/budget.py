from __future__ import annotations

from dataclasses import dataclass

TOOL_COSTS = {"inspect": 1, "clarify": 2, "verify": 2}


@dataclass
class BudgetLedger:
    initial_units: int = 14
    max_actions: int = 60
    spent_units: int = 0
    actions: int = 0

    @property
    def remaining_units(self) -> int:
        return max(0, self.initial_units - self.spent_units)

    @property
    def remaining_actions(self) -> int:
        return max(0, self.max_actions - self.actions)

    def can_spend(self, tool: str) -> bool:
        cost = TOOL_COSTS.get(tool)
        return cost is not None and self.remaining_units >= cost and self.remaining_actions >= 1

    def record(self, tool: str) -> None:
        if tool not in TOOL_COSTS:
            raise ValueError(f"Unknown paid tool: {tool}")
        if not self.can_spend(tool):
            raise RuntimeError(f"Cannot afford {tool}: remaining={self.remaining_units}, cost={TOOL_COSTS[tool]}")
        self.spent_units += TOOL_COSTS[tool]
        self.actions += 1

    def record_zero_cost_action(self) -> None:
        if self.remaining_actions < 1:
            raise RuntimeError("Maximum action count reached")
        self.actions += 1

    def snapshot(self) -> dict:
        return {
            "initial_units": self.initial_units,
            "spent_units": self.spent_units,
            "remaining_units": self.remaining_units,
            "actions": self.actions,
            "remaining_actions": self.remaining_actions,
        }
