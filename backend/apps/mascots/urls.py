from apps.common.routers import NoFormatSuffixRouter

from .views import MascotViewSet

router = NoFormatSuffixRouter(trailing_slash=False)
router.register("mascots", MascotViewSet, basename="mascot")

urlpatterns = router.urls

