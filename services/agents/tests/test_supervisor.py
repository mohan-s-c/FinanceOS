import unittest
from financeos_agents.supervisor import compute_agent_health, evaluate, health_status


def rows(*outcomes_confs):
    return [{"agent": "AP Matching Agent", "outcome": o, "conf": c} for o, c in outcomes_confs]


class SupervisorHealth(unittest.TestCase):
    def test_override_rate_hand_computed(self):
        # 6 auto + 1 human_resolved + 1 overridden = 8 completed; 2 escalated.
        rs = rows(*[("auto", 95)] * 6, ("human_resolved", 80), ("overridden", 70),
                  ("escalated", 60), ("escalated", 62))
        m = compute_agent_health(rs)
        self.assertEqual(m["volume"], 10)
        self.assertAlmostEqual(m["override_rate"], 1 / 8, places=4)
        self.assertAlmostEqual(m["escalation_share"], 2 / 10, places=4)

    def test_status_watch_on_override(self):
        # 1/8 = 12.5% — above the 5% watch band, below the 15% alert band.
        rs = rows(*[("auto", 95)] * 7, ("overridden", 70))
        status, reasons = health_status(compute_agent_health(rs))
        self.assertEqual(status, "watch")
        self.assertTrue(any("override" in r for r in reasons))

    def test_status_alert_on_override(self):
        # 2/8 = 25% ≥ 15% ⇒ alert.
        rs = rows(*[("auto", 95)] * 6, ("overridden", 70), ("overridden", 71))
        status, _ = health_status(compute_agent_health(rs))
        self.assertEqual(status, "alert")

    def test_confidence_drift_watch(self):
        # Older half ~95, newer half ~70 ⇒ drift −25 ≤ −10 ⇒ watch.
        rs = rows(("auto", 95), ("auto", 96), ("auto", 94), ("auto", 95),
                  ("auto", 70), ("auto", 71), ("auto", 69), ("auto", 70))
        m = compute_agent_health(rs)
        self.assertLessEqual(m["conf_drift"], -10)
        status, reasons = health_status(m)
        self.assertEqual(status, "watch")
        self.assertTrue(any("drift" in r for r in reasons))

    def test_clean_agent_is_ok(self):
        rs = rows(*[("auto", 95)] * 9, ("escalated", 60))
        status, reasons = health_status(compute_agent_health(rs))
        self.assertEqual(status, "ok")
        self.assertEqual(reasons, ["all signals within bands"])

    def test_error_rate_alert(self):
        # 1 error vs 8 decisions = 1/9 ≈ 11% ≥ 10% ⇒ alert.
        rs = rows(*[("auto", 95)] * 8, ("error", 0))
        m = compute_agent_health(rs)
        self.assertAlmostEqual(m["error_rate"], 1 / 9, places=4)
        self.assertEqual(health_status(m)[0], "alert")

    def test_window_limits_rows(self):
        # 5 old overrides pushed out of a window of 4 clean rows.
        rs = rows(*[("overridden", 70)] * 5, *[("auto", 95)] * 4)
        m = compute_agent_health(rs, window=4)
        self.assertEqual(m["volume"], 4)
        self.assertEqual(m["override_rate"], 0.0)

    def test_config_rows_ignored(self):
        rs = rows(("config", 0), ("auto", 95), ("auto", 96), ("config", 0))
        self.assertEqual(compute_agent_health(rs)["volume"], 2)

    def test_evaluate_reports_every_roster_agent(self):
        roster = [{"id": "ap-matching", "name": "AP Matching Agent"},
                  {"id": "payment-run", "name": "Payment Run Agent"}]
        snaps = evaluate(rows(("auto", 95), ("auto", 96)), roster)
        self.assertEqual(len(snaps), 2)
        by_id = {s["agent_id"]: s for s in snaps}
        self.assertEqual(by_id["ap-matching"]["status"], "ok")
        # No telemetry must be visible, not green (fail-safe).
        self.assertEqual(by_id["payment-run"]["status"], "nodata")
        self.assertEqual(by_id["payment-run"]["volume"], 0)

    def test_snapshot_shape_for_persistence(self):
        snaps = evaluate(rows(*[("auto", 95)] * 3), [{"id": "ap-matching", "name": "AP Matching Agent"}])
        s = snaps[0]
        for key in ("agent_id", "name", "window", "status", "reasons", "override_rate",
                    "conf_drift", "volume", "error_rate", "latency_p95", "signals"):
            self.assertIn(key, s)
        self.assertEqual(s["window"], "last-200")
        self.assertEqual({sig["metric"] for sig in s["signals"]},
                         {"volume", "override_rate", "escalation_share", "avg_confidence", "conf_drift", "error_rate"})


if __name__ == "__main__":
    unittest.main()
