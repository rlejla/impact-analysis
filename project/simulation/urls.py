from django.urls import path
from .views import GuidelinesListView, SubmissionsListView, SimulationView, GraphReportView

urlpatterns = [
    path('guidelines/', GuidelinesListView.as_view(), name='guidelines'),
    path('submissions/', SubmissionsListView.as_view(), name='submissions'),
    path('simulate/', SimulationView.as_view(), name='simulate'),
    path('graphs/', GraphReportView.as_view(), name='graphs'),
]
