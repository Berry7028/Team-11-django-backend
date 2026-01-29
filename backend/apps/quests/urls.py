from backend.apps.common.routers import NoFormatSuffixRouter

from .views import QuestViewSet

router = NoFormatSuffixRouter(trailing_slash=False)
router.register("quests", QuestViewSet, basename="quest")

urlpatterns = router.urls

