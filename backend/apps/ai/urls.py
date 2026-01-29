from django.urls import path

from .views import HintView

urlpatterns = [
    path("hints/", HintView.as_view(), name="ai-hints"),
]

