from rest_framework.routers import DefaultRouter

from .views import ConditionViewSet

router = DefaultRouter()
router.register("conditions", ConditionViewSet, basename="condition")

urlpatterns = router.urls

