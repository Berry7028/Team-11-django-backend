"""
Quests API endpoints.

主なユースケース:
- RN からクエスト一覧を取得して表示
- クエスト作成/更新
"""

from __future__ import annotations

from datetime import date

from rest_framework import permissions, status, viewsets
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import Quest
from .serializers import QuestSerializer
from .supabase_client import get_supabase_client


def _get_user_uuid(request: Request) -> str | None:
    return request.headers.get("X-User-UUID")


class QuestsGetView(APIView):
    """
    当日分のクエストをSupabaseから取得する。
    GET /api/quests/get
    """

    permission_classes = [permissions.AllowAny]

    def get(self, request: Request) -> Response:
        uuid = _get_user_uuid(request)
        if not uuid:
            return Response(
                {"detail": "X-User-UUID ヘッダーが必要です。"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        try:
            client = get_supabase_client()
        except ValueError as exc:
            return Response(
                {"detail": "Supabase設定エラー", "error": str(exc)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )

        today = date.today().isoformat()

        try:
            result = (
                client.table("quests")
                .select("*")
                .eq("uuid", uuid)
                .eq("day", today)
                .execute()
            )
        except Exception as exc:
            return Response(
                {"detail": "Supabaseの取得に失敗しました。", "error": str(exc)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )

        return Response(result.data, status=status.HTTP_200_OK)


class QuestCompleteView(APIView):
    """
    クエストの完了/取り消しを行う。
    POST /api/quests/:quest_id/complete
    """

    permission_classes = [permissions.AllowAny]

    def post(self, request: Request, quest_id: int) -> Response:
        uuid = _get_user_uuid(request)
        if not uuid:
            return Response(
                {"detail": "X-User-UUID ヘッダーが必要です。"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        try:
            client = get_supabase_client()
        except ValueError as exc:
            return Response(
                {"detail": "Supabase設定エラー", "error": str(exc)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )

        try:
            # クエストを取得
            result = (
                client.table("quests")
                .select("*")
                .eq("id", quest_id)
                .eq("uuid", uuid)
                .execute()
            )

            if not result.data:
                return Response(
                    {"detail": "クエストが見つかりません。"},
                    status=status.HTTP_404_NOT_FOUND,
                )

            quest = result.data[0]
            new_completed = not quest["completed"]

            # completedフラグを更新
            update_result = (
                client.table("quests")
                .update({"completed": new_completed})
                .eq("id", quest_id)
                .eq("uuid", uuid)
                .execute()
            )

            if not update_result.data:
                return Response(
                    {"detail": "クエストの更新に失敗しました。"},
                    status=status.HTTP_500_INTERNAL_SERVER_ERROR,
                )

            return Response(update_result.data[0], status=status.HTTP_200_OK)

        except Exception as exc:
            return Response(
                {"detail": "Supabaseの操作に失敗しました。", "error": str(exc)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )


class QuestViewSet(viewsets.ModelViewSet):
    """
    /api/quests/quests/ 用の CRUD エンドポイント。
    """

    queryset = Quest.objects.select_related("owner").all()
    serializer_class = QuestSerializer
    permission_classes = [permissions.IsAuthenticated]

    def perform_create(self, serializer: QuestSerializer) -> None:
        serializer.save(owner=self.request.user)

