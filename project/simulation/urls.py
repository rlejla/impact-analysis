from django.urls import path
from .views import GuidelinesListView, SubmissionsListView

urlpatterns = [
    path('guidelines/', GuidelinesListView.as_view(), name='guidelines'),
    path('submissions/', SubmissionsListView.as_view(), name='submissions'),
]
