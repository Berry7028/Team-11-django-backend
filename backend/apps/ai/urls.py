from django.urls import path

from .views import HintView, RecommendationsView

urlpatterns = [
    path("hints/", HintView.as_view(), name="ai-hints"),
    path("recommendations/", RecommendationsView.as_view(), name="ai-recommendations"),
]

