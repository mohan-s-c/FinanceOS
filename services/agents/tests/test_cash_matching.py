import unittest
from financeos_agents.cash_matching import match_deposit

INV = [
    {"id": "AR-7741", "customer": "Hertz", "amount": 24600, "age": 40},
    {"id": "AR-7726", "customer": "Hertz", "amount": 18200, "age": 30},
    {"id": "AR-7702", "customer": "Hertz", "amount": 12000, "age": 20},
    {"id": "AR-8042", "customer": "Northwind", "amount": 26800, "age": 25},
    {"id": "AR-8010", "customer": "Cobalt", "amount": 9400, "age": 35},
    {"id": "AR-8011", "customer": "Cobalt", "amount": 13750, "age": 15},
]


class CashMatch(unittest.TestCase):
    def test_remittance_exact(self):
        d = {"id": "D1", "amount": 54800, "customer": "Hertz", "remittance": ["AR-7741", "AR-7726", "AR-7702"]}
        r = match_deposit(d, INV)
        self.assertEqual(r["method"], "remittance")
        self.assertEqual(r["recommendation"], "apply")
        self.assertEqual(r["confidence"], 97)
        self.assertEqual(r["matchedCount"], 3)

    def test_exact_single(self):
        d = {"id": "D2", "amount": 26800, "payer": "Northwind wire"}
        r = match_deposit(d, INV)
        self.assertEqual(r["method"], "exact")
        self.assertEqual(r["recommendation"], "apply")
        self.assertEqual(r["suggestions"][0]["inv"], "AR-8042")

    def test_customer_batch(self):
        d = {"id": "D3", "amount": 23150, "customer": "Cobalt"}
        r = match_deposit(d, INV)
        self.assertEqual(r["method"], "batch")
        self.assertEqual(r["matchedCount"], 2)
        self.assertEqual(r["confidence"], 88)

    def test_fuzzy_review(self):
        d = {"id": "D4", "amount": 30000, "customer": "Hertz"}  # 18200+12000=30200 ~ 0.67%
        r = match_deposit(d, INV)
        self.assertEqual(r["method"], "fuzzy")
        self.assertEqual(r["recommendation"], "review")
        self.assertGreaterEqual(r["confidence"], 52)

    def test_unmatched(self):
        d = {"id": "D5", "amount": 18900, "payer": "ACH — unidentified"}
        r = match_deposit(d, INV)
        self.assertEqual(r["method"], "unmatched")
        self.assertEqual(r["recommendation"], "unmatched")
        self.assertEqual(r["invoicesLabel"], "No match")


if __name__ == "__main__":
    unittest.main()
