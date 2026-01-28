"""
Accounts API endpoints.

主なユースケース:
- React Native からのログイン後、`/api/accounts/me/` で現在ユーザー情報を取得
- `/api/accounts/profiles/` でプロフィール CRUD
"""

from __future__ import annotations

from django.contrib.auth import get_user_model
from rest_framework import permissions, viewsets
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import UserProfile
from .serializers import UserProfileSerializer, UserSerializer


User = get_user_model()


class CurrentUserView(APIView):
    """
    GET /api/accounts/me/

    - 認証済みユーザーの情報を返却
    - 未認証の場合は 401
    """

    permission_classes = [permissions.IsAuthenticated]

    def get(self, request: Request) -> Response:
        serializer = UserSerializer(request.user)
        return Response(serializer.data)


class UserProfileViewSet(viewsets.ModelViewSet):
    """
    /api/accounts/profiles/ 用の CRUD エンドポイント。

    RN 側では、プロフィール編集画面などから利用する想定。
    """

    queryset = UserProfile.objects.select_related("user").all()
    serializer_class = UserProfileSerializer
    permission_classes = [permissions.IsAuthenticated]

    def perform_create(self, serializer: UserProfileSerializer) -> None:
        serializer.save(user=self.request.user)

