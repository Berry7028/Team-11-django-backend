from django.urls import path

from apps.common.routers import NoFormatSuffixRouter

from .views import QuestAdoptView, QuestCompleteView, QuestViewSet, QuestsGetView

router = NoFormatSuffixRouter(trailing_slash=False)
router.register("quests", QuestViewSet, basename="quest")

urlpatterns = [
    path("get", QuestsGetView.as_view(), name="quests-get"),
    path("<int:quest_id>/complete", QuestCompleteView.as_view(), name="quests-complete"),
    path("adopt", QuestAdoptView.as_view(), name="quests-adopt"),
] + router.urls
