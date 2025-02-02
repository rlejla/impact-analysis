from rest_framework.test import APITestCase
from django.urls import reverse
from rest_framework import status
from simulation.views import GUIDELINES_DATA


class GraphReportTests(APITestCase):
    def test_graph_report(self):
        payload = {
            "total_submissions": 1000,
            "outcome_changes": 237,
            "outcome_change_percentage": 23.7,
            "breakdown_by_industry": {
                "manufacturing": 26,
                "construction": 33,
                "retail": 25,
                "transportation": 35,
                "pharmaceuticals": 20,
                "healthcare": 34,
                "technology": 27,
                "financial": 19,
                "energy": 18
            },
            "breakdown_by_risk_factor": {
                "workplace_safety": 237,
                "reputation_risk": 73,
                "cyber_threats": 84,
                "economic_downturn": 88,
                "pandemic": 76,
                "natural_disasters": 73,
                "regulatory_changes": 82,
                "supply_chain": 76,
                "environmental": 67
            },
            "breakdown_by_company_size": {
                "small": 117,
                "medium": 43,
                "large": 77
            },
            "breakdown_by_location": {
                "TX": 29,
                "FL": 11,
                "MI": 18,
                "GA": 20,
                "IL": 32,
                "OH": 32,
                "NY": 18,
                "CA": 28,
                "PA": 24,
                "NC": 25
            },
            "time_impact": {
                "immediate": 44,
                "gradual": 193
            },
            "financial_impact": 5087600000.0,
            "near_miss_submissions": []
        }
        url = reverse("graphs")
        response = self.client.post(url, payload, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data = response.data
        self.assertIn("charts", data)
        self.assertIn("summaries", data)
        for key in ["industry_chart", "risk_factor_chart", "company_size_chart", "location_chart", "time_impact_chart"]:
            self.assertTrue(data["charts"].get(key, "").startswith("data:image/png;base64,"))
        for summary_key in ["industry_summary", "risk_factor_summary", "company_size_summary", "location_summary", "time_impact_summary", "financial_summary"]:
            self.assertIsInstance(data["summaries"].get(summary_key), str)
