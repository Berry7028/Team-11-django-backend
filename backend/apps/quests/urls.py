from rest_framework.routers import DefaultRouter

from .views import QuestViewSet

router = DefaultRouter()
router.register("quests", QuestViewSet, basename="quest")

urlpatterns = router.urls

