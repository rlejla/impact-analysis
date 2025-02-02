import os
from rest_framework.views import APIView 
from rest_framework.pagination import PageNumberPagination
from rest_framework.response import Response
from rest_framework import status
from .serializers import GuidelineSerializer
from .services import analyze_impact_advanced

from .utils import load_json_data, generate_pie_chart, generate_bar_chart


BASE_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'simulation', 'data')
GUIDELINES_PATH = os.path.join(BASE_DIR, 'guidelines.json')
SUBMISSIONS_PATH = os.path.join(BASE_DIR, 'submissions.json')

GUIDELINES_DATA = []
SUBMISSIONS_DATA = []

try:
    GUIDELINES_DATA = load_json_data(GUIDELINES_PATH)
except Exception as e:
    print(f"An error occurred while loading the guidelines data: {e}")

try:
    SUBMISSIONS_DATA = load_json_data(SUBMISSIONS_PATH)
except Exception as e:
    print(f"An error occurred while loading the submissions data: {e}")


class GuidelinesListView(APIView):
    """
    Returns a list of all guidelines.
    """
    def get(self, request):
        return Response(GUIDELINES_DATA, status=status.HTTP_200_OK)

class SubmissionsListView(APIView):
    """
    Returns a list of all submissions.
    """
    def get(self, request):
        return Response(SUBMISSIONS_DATA, status=status.HTTP_200_OK)
    
class SimulationView(APIView):
    """
    Accepts a guideline payload.
    If the guideline does not have an ID, it is added to the list of guidelines.
    If the guideline has an ID, it is compared to the existing guideline with the same ID.
    Returns an impact report.
    """
    def post(self, request):
        serializer = GuidelineSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        guideline_payload = serializer.validated_data
        guideline_id = guideline_payload.get("id")

        simulation_guidelines = GUIDELINES_DATA.copy()

        if not guideline_id: 
            GUIDELINES_DATA.append(guideline_payload)
            baseline = {}  
            impact = analyze_impact_advanced(SUBMISSIONS_DATA, baseline, guideline_payload)
            return Response(impact, status=status.HTTP_200_OK)
        else:
            existing_guideline = next((g for g in simulation_guidelines if g.get("id") == guideline_id), None)
            if not existing_guideline:
                return Response(
                    {"detail": f"Guideline with id {guideline_id} does not exist."},
                    status=status.HTTP_400_BAD_REQUEST
                )
            impact = analyze_impact_advanced(SUBMISSIONS_DATA, existing_guideline, guideline_payload)
            return Response(impact, status=status.HTTP_200_OK)
        
class GraphReportView(APIView):
    """
    Accepts an impact report JSON payload and returns a JSON response containing:
      - Base64-encoded images for charts.
      - Narrative text summaries tying together the data.
    """
    def post(self, request):
        impact = request.data

        charts = {
            "industry_chart": generate_bar_chart(impact.get("breakdown_by_industry", {}), "Industry Breakdown"),
            "risk_factor_chart": generate_bar_chart(impact.get("breakdown_by_risk_factor", {}), "Risk Factor Breakdown"),
            "company_size_chart": generate_bar_chart(impact.get("breakdown_by_company_size", {}), "Company Size Breakdown"),
            "location_chart": generate_bar_chart(impact.get("breakdown_by_location", {}), "Location Breakdown"),
            "time_impact_chart": generate_pie_chart(impact.get("time_impact", {}), "Time Impact")
        }

        summaries = self.generate_summaries(impact)
        return Response({"charts": charts, "summaries": summaries}, status=status.HTTP_200_OK)

    def generate_summaries(self, impact: dict) -> dict:
        total = impact.get("total_submissions", 0)
        outcome_changes = impact.get("outcome_changes", 0)
        outcome_percentage = impact.get("outcome_change_percentage", 0)
        industry_data = impact.get("breakdown_by_industry", {})
        risk_data = impact.get("breakdown_by_risk_factor", {})
        size_data = impact.get("breakdown_by_company_size", {})
        location_data = impact.get("breakdown_by_location", {})
        time_data = impact.get("time_impact", {})
        financial = impact.get("financial_impact", 0)

        industry_max = max(industry_data.items(), key=lambda x: x[1])[0] if industry_data else "N/A"
        risk_max = max(risk_data.items(), key=lambda x: x[1])[0] if risk_data else "N/A"
        size_small = size_data.get("small", "N/A")
        location_max = max(location_data.items(), key=lambda x: x[1])[0] if location_data else "N/A"
        immediate = time_data.get("immediate", 0)
        gradual = time_data.get("gradual", 0)

        industry_summary = (
            f"Out of {total} submissions, {outcome_changes} ({outcome_percentage}%) showed changes. "
            f"The industry most impacted is {industry_max}."
        )
        risk_factor_summary = (
            f"The dominant risk factor is {risk_max}, which plays a key role in the outcome differences."
        )
        company_size_summary = (
            f"Small companies are most affected, with {size_small} impacted submissions."
        )
        location_summary = (
            f"Geographically, {location_max} exhibits the highest impact."
        )
        time_impact_summary = (
            f"Immediate changes affected {immediate} submissions, while gradual changes impacted {gradual}, "
            "suggesting that future renewals may follow these patterns."
        )
        financial_summary = (
            f"The projected financial impact is approximately ${financial:,.2f}, indicating significant economic implications."
        )

        return {
            "industry_summary": industry_summary,
            "risk_factor_summary": risk_factor_summary,
            "company_size_summary": company_size_summary,
            "location_summary": location_summary,
            "time_impact_summary": time_impact_summary,
            "financial_summary": financial_summary,
        }