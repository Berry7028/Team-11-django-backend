from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .views import CurrentUserView, UserProfileViewSet

router = DefaultRouter()
router.register("profiles", UserProfileViewSet, basename="user-profile")

urlpatterns = [
    path("me/", CurrentUserView.as_view(), name="accounts-me"),
    path("", include(router.urls)),
]

