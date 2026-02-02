"""Project URL configuration for the backend API."""

from django.contrib import admin
from django.urls import include, path

urlpatterns = [
    path("api/quests/", include("apps.quests.urls")),
    path("api/questionnaires/", include("apps.questionnaires.urls")),
    path("api/questionnaire/", include("apps.questionnaires.urls")),
    path("api/ai/", include("apps.ai.urls")),
]

