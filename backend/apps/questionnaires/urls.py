from rest_framework.routers import DefaultRouter

from .views import AnswerViewSet, QuestionnaireViewSet

router = DefaultRouter()
router.register("questionnaires", QuestionnaireViewSet, basename="questionnaire")
router.register("answers", AnswerViewSet, basename="answer")

urlpatterns = router.urls

