from django.urls import path

from .views import HintView, RecommendationsView, MascotOnboardingView, MascotStateView

urlpatterns = [
    path("hints/", HintView.as_view(), name="ai-hints"),
    path("recommendations/", RecommendationsView.as_view(), name="ai-recommendations"),
    path("mascot-state/", MascotStateView.as_view()),
    path("onboarding/complete/", MascotOnboardingView.as_view()),
]
