import unittest
from financeos_agents.collections import score_account, generate_collections


class Collections(unittest.TestCase):
    def test_high_risk_payment_plan(self):
        s = score_account({"account": "X", "loc": "L", "balance": 48200, "days": 62})
        self.assertGreaterEqual(s["risk"], 80)
        self.assertEqual(s["recommendation"], "plan")
        self.assertEqual(s["tone"], "bad")

    def test_low_risk_monitor(self):
        s = score_account({"account": "Y", "loc": "L", "balance": 11750, "days": 18})
        self.assertLess(s["risk"], 40)
        self.assertEqual(s["recommendation"], "monitor")
        self.assertEqual(s["tone"], "ok")

    def test_generate_sorted_by_risk(self):
        class ERP:
            def list_overdue_accounts(self):
                return [{"account": "A", "loc": "L", "balance": 11750, "days": 18},
                        {"account": "B", "loc": "L", "balance": 48200, "days": 62}]
        out = generate_collections(ERP())
        self.assertEqual(out[0]["account"], "B")  # highest risk first
        self.assertTrue(out[0]["draft"])


if __name__ == "__main__":
    unittest.main()
