import unittest
from financeos_agents.matching import three_way_match

POL = {"po_required_above": 10000, "capex_signoff_above": 20000}
GR = {"status": "received"}


class ThreeWayMatch(unittest.TestCase):
    def test_clean_within_tolerance(self):
        inv = {"id": "INV-1", "vendor": "Acme", "amount": 4200, "po_ref": "PO-1"}
        po = {"id": "PO-1", "total": 4200, "variance_ceiling": 0.05}
        r = three_way_match(inv, po, GR, POL)
        self.assertEqual(r["recommendation"], "approve")
        self.assertTrue(r["withinTolerance"])
        self.assertGreaterEqual(r["confidence"], 90)
        self.assertNotIn("mismatch", r["match"]["inv"])

    def test_price_variance_over_ceiling(self):
        inv = {"id": "INV-2", "vendor": "Sparkle", "amount": 8420, "po_ref": "PO-2"}
        po = {"id": "PO-2", "total": 7520, "variance_ceiling": 0.05, "contract_ref": "C-1"}
        r = three_way_match(inv, po, GR, POL)
        self.assertEqual(r["recommendation"], "escalate")
        self.assertEqual(r["tone"], "warn")
        self.assertFalse(r["withinTolerance"])
        self.assertLess(r["confidence"], 80)
        self.assertTrue(r["match"]["inv"].get("mismatch"))

    def test_missing_po_above_threshold(self):
        inv = {"id": "INV-3", "vendor": "SecureGuard", "amount": 15200, "po_ref": None}
        r = three_way_match(inv, None, {"status": "partial"}, POL)
        self.assertEqual(r["recommendation"], "hold")
        self.assertTrue(r["match"]["po"].get("mismatch"))
        self.assertLess(r["confidence"], 60)

    def test_over_approval_limit_clean(self):
        inv = {"id": "INV-4", "vendor": "Brightline", "amount": 24680, "po_ref": "PO-4"}
        po = {"id": "PO-4", "total": 24680, "variance_ceiling": 0.05}
        r = three_way_match(inv, po, GR, POL)
        self.assertEqual(r["recommendation"], "escalate")
        self.assertTrue(r["withinTolerance"])  # clean, just needs sign-off
        self.assertIn("approval limit", r["reason"])

    def test_duplicate(self):
        inv = {"id": "INV-5", "vendor": "Acme", "amount": 3180, "po_ref": "PO-5"}
        po = {"id": "PO-5", "total": 3180, "variance_ceiling": 0.05}
        paid = [{"id": "INV-44602", "vendor": "Acme", "amount": 3180, "similarity": 98}]
        r = three_way_match(inv, po, GR, POL, paid_invoices=paid)
        self.assertEqual(r["recommendation"], "reject")
        self.assertEqual(r["tone"], "bad")
        self.assertLess(r["confidence"], 50)
        self.assertEqual(r["sources"][0]["ref"], "INV-44602")

    def test_tax_jurisdiction(self):
        inv = {"id": "INV-6", "vendor": "Pacific", "amount": 6740, "tax": 540, "po_ref": "PO-6"}
        po = {"id": "PO-6", "total": 6200, "variance_ceiling": 0.05, "tax_exempt": True, "lease_ref": "L-1"}
        r = three_way_match(inv, po, GR, POL)
        self.assertEqual(r["recommendation"], "escalate")
        self.assertIn("Tax", r["reason"])


if __name__ == "__main__":
    unittest.main()
