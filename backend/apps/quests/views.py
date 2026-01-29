"""
Quests API endpoints.

主なユースケース:
- RN からクエスト一覧を取得して表示
- クエスト作成/更新
"""

from __future__ import annotations

from rest_framework import permissions, viewsets

from .models import Quest
from .serializers import QuestSerializer


class QuestViewSet(viewsets.ModelViewSet):
    """
    /api/quests/quests/ 用の CRUD エンドポイント。
    """

    queryset = Quest.objects.select_related("owner").all()
    serializer_class = QuestSerializer
    permission_classes = [permissions.IsAuthenticated]

    def perform_create(self, serializer: QuestSerializer) -> None:
        serializer.save(owner=self.request.user)

