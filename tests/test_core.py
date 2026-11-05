import unittest

from partpilot.models import ElectricalSpec, PartRecord, Freshness, StockStatus
from partpilot.compatibility import compatibility_check, assess_candidate
from partpilot.budget import BudgetLedger
from partpilot.inventory import InventoryLedger
from partpilot.parsing import parse_spec_fallback


class PartPilotCoreTests(unittest.TestCase):
    def test_higher_wattage_is_compatible(self):
        request = ElectricalSpec(voltage_v=12, connector="usb-c", min_wattage_w=10)
        part = ElectricalSpec(voltage_v=12, connector="usb-c", min_wattage_w=20)
        ok, reasons = compatibility_check(request, part)
        self.assertTrue(ok)
        self.assertFalse(reasons)

    def test_unknown_connector_is_not_safe(self):
        request = ElectricalSpec(voltage_v=12, connector="usb-c", min_wattage_w=10)
        part = ElectricalSpec(voltage_v=12, connector=None, min_wattage_w=20)
        ok, reasons = compatibility_check(request, part)
        self.assertFalse(ok)
        self.assertTrue(any("connector" in reason for reason in reasons))

    def test_lower_wattage_fails(self):
        request = ElectricalSpec(voltage_v=12, connector="usb-c", min_wattage_w=20)
        part = ElectricalSpec(voltage_v=12, connector="usb-c", min_wattage_w=10)
        ok, _ = compatibility_check(request, part)
        self.assertFalse(ok)

    def test_aged_stock_requires_verification(self):
        request = ElectricalSpec(voltage_v=12, connector="usb-c", min_wattage_w=10)
        part = PartRecord(
            part_id="P-1", description="12V USB-C 20W",
            spec=ElectricalSpec(voltage_v=12, connector="usb-c", min_wattage_w=20),
            snapshot_stock=StockStatus.AVAILABLE, freshness=Freshness.AGED,
        )
        assessment = assess_candidate(request, part, set())
        self.assertTrue(assessment.compatible)
        self.assertTrue(assessment.stock_needs_verification)
        self.assertFalse(assessment.safe_to_dispatch)

    def test_recent_stock_can_be_used(self):
        request = ElectricalSpec(voltage_v=12, connector="usb-c", min_wattage_w=10)
        part = PartRecord(
            part_id="P-1", description="12V USB-C 20W",
            spec=ElectricalSpec(voltage_v=12, connector="usb-c", min_wattage_w=20),
            snapshot_stock=StockStatus.AVAILABLE, freshness=Freshness.RECENT,
        )
        assessment = assess_candidate(request, part, set())
        self.assertTrue(assessment.safe_to_dispatch)

    def test_budget_costs_and_caps(self):
        ledger = BudgetLedger()
        ledger.record("inspect")
        ledger.record("clarify")
        ledger.record("verify")
        self.assertEqual(ledger.spent_units, 5)
        self.assertEqual(ledger.remaining_units, 9)

    def test_cannot_overspend(self):
        ledger = BudgetLedger(initial_units=2)
        ledger.record("verify")
        self.assertFalse(ledger.can_spend("inspect"))

    def test_inventory_prevents_double_dispatch(self):
        ledger = InventoryLedger(["P-1"])
        ledger.reserve_after_successful_dispatch("P-1")
        self.assertFalse(ledger.available_to_this_batch("P-1"))

    def test_unique_assignment_does_not_double_allocate_part(self):
        from partpilot.assignment import maximum_unique_assignment
        result = maximum_unique_assignment({"R1": ["P1", "P2"], "R2": ["P1"], "R3": ["P3"]})
        self.assertEqual(len(result), 3)
        self.assertEqual(len(set(result.values())), 3)
        self.assertEqual(result["R2"], "P1")


if __name__ == "__main__":
    unittest.main()
