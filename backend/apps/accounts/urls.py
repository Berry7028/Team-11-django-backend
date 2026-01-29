from django.urls import include, path

from backend.apps.common.routers import NoFormatSuffixRouter

from .views import CurrentUserView, UserProfileViewSet

router = NoFormatSuffixRouter(trailing_slash=False)
router.register("profiles", UserProfileViewSet, basename="user-profile")

urlpatterns = [
    path("me/", CurrentUserView.as_view(), name="accounts-me"),
    path("", include(router.urls)),
]

