from rest_framework.routers import DefaultRouter

from .views import MascotViewSet

router = DefaultRouter()
router.register("mascots", MascotViewSet, basename="mascot")

urlpatterns = router.urls

