from django.urls import path
from analytics.views import AnalyticView

urlpatterns = [
    path("", AnalyticView.dashboard),
    path("<str:dashId>", AnalyticView.dashboard),
]
