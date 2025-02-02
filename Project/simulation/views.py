import os
from rest_framework.views import APIView 
from rest_framework.pagination import PageNumberPagination

from .utils import load_json_data


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
    Returns paginated list of all guidelines.
    """
    def get(self, request):
        paginator = PageNumberPagination()
        result_page = paginator.paginate_queryset(GUIDELINES_DATA, request)
        return paginator.get_paginated_response(result_page)

class SubmissionsListView(APIView):
    """
    Returns paginated list of all submissions.
    """
    def get(self, request):
        paginator = PageNumberPagination()
        result_page = paginator.paginate_queryset(SUBMISSIONS_DATA, request)
        return paginator.get_paginated_response(result_page)


