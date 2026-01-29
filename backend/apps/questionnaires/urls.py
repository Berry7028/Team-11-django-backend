from django.urls import path

from apps.common.routers import NoFormatSuffixRouter

from .views import (
    AnswerViewSet,
    MorningQuestionnaireView,
    NightQuestionnaireView,
    QuestionnaireViewSet,
)

router = NoFormatSuffixRouter(trailing_slash=False)
router.register("questionnaires", QuestionnaireViewSet, basename="questionnaire")
router.register("answers", AnswerViewSet, basename="answer")

urlpatterns = [
    path("morning", MorningQuestionnaireView.as_view(), name="questionnaire-morning"),
    path("night", NightQuestionnaireView.as_view(), name="questionnaire-night"),
    *router.urls,
]

