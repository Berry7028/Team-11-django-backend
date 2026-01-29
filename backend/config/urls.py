"""Project URL configuration for the backend API."""

from django.contrib import admin
from django.urls import include, path

urlpatterns = [
    path("admin/", admin.site.urls),
    path("api/accounts/", include("backend.apps.accounts.urls")),
    path("api/conditions/", include("backend.apps.conditions.urls")),
    path("api/quests/", include("backend.apps.quests.urls")),
    path("api/mascots/", include("backend.apps.mascots.urls")),
    path("api/logs/", include("backend.apps.logs.urls")),
    path("api/questionnaires/", include("backend.apps.questionnaires.urls")),
    path("api/questionnaire/", include("backend.apps.questionnaires.urls")),
    path("api/ai/", include("backend.apps.ai.urls")),
]

