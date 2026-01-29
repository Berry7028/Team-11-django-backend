from backend.apps.common.routers import NoFormatSuffixRouter

from .views import LogEntryViewSet

router = NoFormatSuffixRouter(trailing_slash=False)
router.register("logs", LogEntryViewSet, basename="log-entry")

urlpatterns = router.urls

