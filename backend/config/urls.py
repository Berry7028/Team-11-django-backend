"""Project URL configuration for the backend API."""

from django.contrib import admin
from django.urls import include, path

urlpatterns = [
    path("admin/", admin.site.urls),
    path("api/accounts/", include("apps.accounts.urls")),
    path("api/conditions/", include("apps.conditions.urls")),
    path("api/quests/", include("apps.quests.urls")),
    path("api/mascots/", include("apps.mascots.urls")),
    path("api/logs/", include("apps.logs.urls")),
    path("api/questionnaires/", include("apps.questionnaires.urls")),
    path("api/questionnaire/", include("apps.questionnaires.urls")),
    path("api/ai/", include("apps.ai.urls")),
]

