import unittest, sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from server import extract_json, normalize, demo_review

class GateTests(unittest.TestCase):
    def test_extract_json_plain(self):
        self.assertEqual(extract_json('{"risk_level":"low"}')["risk_level"], "low")
    def test_extract_json_noise(self):
        x=extract_json('result: {"risk_level":"medium","decision":"human_review"} end')
        self.assertEqual(x["decision"], "human_review")
    def test_normalize_invalid_defaults_safe(self):
        x=normalize({"risk_level":"banana","decision":"go"})
        self.assertEqual(x["risk_level"], "high")
        self.assertEqual(x["decision"], "human_review")
    def test_demo_high_risk_payment(self):
        x=demo_review("Send money to supplier","")
        self.assertEqual(x["risk_level"], "high")
        self.assertEqual(x["decision"], "human_review")
    def test_demo_low_risk_summary(self):
        x=demo_review("Summarize public notes","")
        self.assertEqual(x["decision"], "allow")

if __name__ == "__main__":
    unittest.main()
