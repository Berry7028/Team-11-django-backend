from backend.apps.common.routers import NoFormatSuffixRouter

from .views import ConditionViewSet

router = NoFormatSuffixRouter(trailing_slash=False)
router.register("conditions", ConditionViewSet, basename="condition")

urlpatterns = router.urls

