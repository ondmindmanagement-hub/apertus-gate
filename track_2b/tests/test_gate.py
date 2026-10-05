import json
import unittest
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
from server import extract_json, normalize, demo_review

class GateTests(unittest.TestCase):
    def test_extract_json_plain(self):
        self.assertEqual(extract_json('{"risk_level":"low"}')["risk_level"], "low")

    def test_extract_json_noise(self):
        x = extract_json('result: {"risk_level":"medium","decision":"human_review"} end')
        self.assertEqual(x["decision"], "human_review")

    def test_extract_json_rejects_non_json(self):
        with self.assertRaises(ValueError):
            extract_json("not structured output")

    def test_normalize_invalid_defaults_safe(self):
        x = normalize({"risk_level":"banana","decision":"go"})
        self.assertEqual(x["risk_level"], "high")
        self.assertEqual(x["decision"], "human_review")

    def test_normalize_missing_fields_defaults_safe(self):
        x = normalize({})
        self.assertEqual(x["risk_level"], "high")
        self.assertEqual(x["decision"], "human_review")
        self.assertTrue(x["safe_next_step"])

    def test_normalize_unstructured_reasons(self):
        x = normalize({"risk_level":"low","decision":"allow","reasons":"text"})
        self.assertEqual(x["reasons"], ["Unstructured model response"])

    def test_normalize_bounds_reason_list(self):
        x = normalize({
            "risk_level":"medium",
            "decision":"human_review",
            "reasons":["x" * 500] * 10
        })
        self.assertEqual(len(x["reasons"]), 6)
        self.assertTrue(all(len(item) <= 300 for item in x["reasons"]))

    def test_demo_high_risk_payment(self):
        x = demo_review("Send money to supplier", "")
        self.assertEqual(x["risk_level"], "high")
        self.assertEqual(x["decision"], "human_review")

    def test_demo_destructive_action(self):
        x = demo_review("Delete the production customer database", "")
        self.assertEqual(x["risk_level"], "high")
        self.assertEqual(x["decision"], "human_review")

    def test_demo_sensitive_publication(self):
        x = demo_review("Publish private medical records", "")
        self.assertEqual(x["risk_level"], "high")
        self.assertEqual(x["decision"], "human_review")

    def test_demo_external_email(self):
        x = demo_review("Email a draft report to an external collaborator", "")
        self.assertEqual(x["risk_level"], "medium")
        self.assertEqual(x["decision"], "human_review")

    def test_demo_low_risk_summary(self):
        x = demo_review("Summarize public notes", "")
        self.assertEqual(x["decision"], "allow")

    def test_evaluation_dataset_matches_demo_policy(self):
        cases = json.loads((ROOT / "data" / "evaluation_cases.json").read_text())
        for case in cases:
            with self.subTest(case=case["id"]):
                result = demo_review(case["action"], case.get("context", ""))
                self.assertEqual(result["decision"], case["expected_decision"])
                self.assertEqual(result["risk_level"], case["expected_risk"])

if __name__ == "__main__":
    unittest.main()
