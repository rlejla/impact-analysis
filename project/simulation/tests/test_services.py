import unittest
from simulation.services import (
    evaluate_condition,
    evaluate_guideline,
    evaluate_near_miss,
    get_baseline_results,
)

class TestServices(unittest.TestCase):
    def test_evaluate_condition_equals(self):
        submission = {"financials": {"revenue": 5000000}}
        condition = {"field": "financials.revenue", "operator": "equals", "value": 5000000}
        self.assertTrue(evaluate_condition(submission, condition))
        condition["value"] = 6000000
        self.assertFalse(evaluate_condition(submission, condition))

    def test_evaluate_condition_greater_equal(self):
        submission = {"financials": {"revenue": 7000000}}
        condition = {"field": "financials.revenue", "operator": ">=", "value": 6000000}
        self.assertTrue(evaluate_condition(submission, condition))
        condition["value"] = 8000000
        self.assertFalse(evaluate_condition(submission, condition))

    def test_evaluate_guideline_any_logic(self):
        submission = {"financials": {"revenue": 5000000}}
        guideline = {
            "conditions": {
                "logic": "any",
                "conditions": [
                    {"field": "financials.revenue", "operator": ">=", "value": 6000000},
                    {"field": "financials.revenue", "operator": "equals", "value": 5000000}
                ]
            }
        }
        self.assertTrue(evaluate_guideline(submission, guideline))

    def test_evaluate_near_miss(self):
        submission = {"financials": {"revenue": 5800000}}
        guideline = {
            "conditions": {
                "logic": "all",
                "conditions": [
                    {"field": "financials.revenue", "operator": ">=", "value": 6000000}
                ]
            }
        }
        self.assertTrue(evaluate_near_miss(submission, guideline, margin=0.1))
        self.assertFalse(evaluate_near_miss(submission, guideline, margin=0.01))

    def test_get_baseline_results_empty(self):
        submissions = [{"financials": {"revenue": 1000000}}, {"financials": {"revenue": 2000000}}]
        baseline = {"id": "test", "conditions": {"logic": "all", "conditions": []}}
        results = get_baseline_results(baseline, submissions)
        self.assertEqual(results, [False, False])

if __name__ == '__main__':
    unittest.main()
