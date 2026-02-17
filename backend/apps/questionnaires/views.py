"""
Questionnaires API endpoints.
"""

from __future__ import annotations

from datetime import datetime, timedelta, timezone

from rest_framework import mixins, permissions, status, viewsets
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import Answer, Questionnaire
from .serializers import (
    AnswerSerializer,
    QuestionnaireRequestSerializer,
    QuestionnaireSerializer,
)
from .supabase_client import get_supabase_client


class QuestionnaireViewSet(viewsets.ReadOnlyModelViewSet):
    """
    アンケート一覧/詳細を提供。
    """

    queryset = Questionnaire.objects.all()
    serializer_class = QuestionnaireSerializer
    permission_classes = [permissions.AllowAny]


class AnswerViewSet(mixins.CreateModelMixin, viewsets.GenericViewSet):
    """
    回答送信エンドポイント。
    """

    queryset = Answer.objects.none()
    serializer_class = AnswerSerializer
    permission_classes = [permissions.AllowAny]


def _get_user_uuid(request: Request) -> str | None:
    return request.headers.get("X-User-UUID")


def _replace_today_condition(
    uuid: str, is_morning: bool, mood: str, condition: str, free_text: str = ""
) -> dict:
    """
    同じ日の既存レコードを削除してから、新しいレコードを挿入する。
    気分と体調を分離して保存する。

    併せて、users_condition が肥大化しないように、各ユーザー直近2件のみ保持する。
    """
    supabase = get_supabase_client()

    today_start = datetime.now(timezone.utc).replace(
        hour=0, minute=0, second=0, microsecond=0
    )
    tomorrow_start = today_start + timedelta(days=1)

    # 同じ日の既存レコードを検索
    existing_result = (
        supabase.table("users_condition")
        .select("*")
        .eq("uuid", uuid)
        .gte("created_at", today_start.isoformat())
        .lt("created_at", tomorrow_start.isoformat())
        .execute()
    )

    if getattr(existing_result, "error", None):
        raise RuntimeError(existing_result.error)

    existing_data = existing_result.data[0] if existing_result.data else {}
    
    if not existing_data:
        latest_result = (
            supabase.table("users_condition")
            .select("*")
            .eq("uuid", uuid)
            .order("created_at", desc=True)
            .limit(1)
            .execute()
        )
        
        if getattr(latest_result, "error", None):
            raise RuntimeError(latest_result.error)
        
        if latest_result.data:
            latest_record = latest_result.data[0]

            latest_created_at_str = latest_record.get("created_at")
            if latest_created_at_str:
                if isinstance(latest_created_at_str, str):
                    latest_created_at_str = latest_created_at_str.replace("Z", "+00:00")
                    try:
                        latest_created_at = datetime.fromisoformat(latest_created_at_str)
                    except (ValueError, AttributeError):
                        latest_created_at = None
                elif isinstance(latest_created_at_str, datetime):
                    latest_created_at = latest_created_at_str
                else:
                    latest_created_at = None
                
                # 最新レコードが今日または昨日のものである場合のみ使用
                if latest_created_at and latest_created_at.tzinfo is None:
                    latest_created_at = latest_created_at.replace(tzinfo=timezone.utc)
                if latest_created_at and latest_created_at >= today_start - timedelta(days=1):
                    existing_data = latest_record

    # 既存レコードがあれば削除
    if existing_result.data:
        # idが存在する場合はidで削除、存在しない場合はuuidと日付範囲で削除
        if isinstance(existing_data, dict) and "id" in existing_data:
            for record in existing_result.data:
                if isinstance(record, dict) and "id" in record:
                    delete_result = (
                        supabase.table("users_condition")
                        .delete()
                        .eq("id", record["id"])
                        .execute()
                    )
                    if getattr(delete_result, "error", None):
                        raise RuntimeError(delete_result.error)
        else:
            delete_result = (
                supabase.table("users_condition")
                .delete()
                .eq("uuid", uuid)
                .gte("created_at", today_start.isoformat())
                .lt("created_at", tomorrow_start.isoformat())
                .execute()
            )
            if getattr(delete_result, "error", None):
                raise RuntimeError(delete_result.error)

    # 新しいレコードを作成（朝/夜の別のフィールドを適切に設定）
    insert_payload = {
        "uuid": uuid,
        "morning_mood": mood if is_morning else existing_data.get("morning_mood"),
        "morning_condition": (
            condition if is_morning else existing_data.get("morning_condition")
        ),
        "night_mood": (
            mood if not is_morning else existing_data.get("night_mood")
        ),
        "night_condition": (
            condition if not is_morning else existing_data.get("night_condition")
        ),
        "morning_note": (
            free_text if is_morning else existing_data.get("morning_note")
        ),
        "night_note": (
            free_text if not is_morning else existing_data.get("night_note")
        ),
    }

    insert_result = supabase.table("users_condition").insert(insert_payload).execute()

    if getattr(insert_result, "error", None):
        raise RuntimeError(insert_result.error)

    # 履歴肥大化防止: 各ユーザー直近2件のみ保持
    prune_result = (
        supabase.table("users_condition")
        .select("created_at")
        .eq("uuid", uuid)
        .order("created_at", desc=True)
        .limit(3)
        .execute()
    )
    if getattr(prune_result, "error", None):
        raise RuntimeError(prune_result.error)

    if prune_result.data and len(prune_result.data) > 2:
        cutoff = prune_result.data[1]["created_at"]
        delete_old_result = (
            supabase.table("users_condition")
            .delete()
            .eq("uuid", uuid)
            .lt("created_at", cutoff)
            .execute()
        )
        if getattr(delete_old_result, "error", None):
            raise RuntimeError(delete_old_result.error)

    if insert_result.data:
        return insert_result.data[0]

    return insert_payload


class MorningQuestionnaireView(APIView):
    permission_classes = [permissions.AllowAny]

    def post(self, request: Request) -> Response:
        uuid = _get_user_uuid(request)
        if not uuid:
            return Response(
                {"detail": "X-User-UUID ヘッダーが必要です。"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        serializer = QuestionnaireRequestSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        try:
            data = _replace_today_condition(
                uuid,
                True,
                serializer.validated_data["mood"],
                serializer.validated_data["condition"],
                serializer.validated_data.get("free_text", ""),
            )
        except RuntimeError:
            return Response(
                {"detail": "Supabaseの保存に失敗しました。"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )

        return Response(data, status=status.HTTP_201_CREATED)


class NightQuestionnaireView(APIView):
    permission_classes = [permissions.AllowAny]

    def post(self, request: Request) -> Response:
        uuid = _get_user_uuid(request)
        if not uuid:
            return Response(
                {"detail": "X-User-UUID ヘッダーが必要です。"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        serializer = QuestionnaireRequestSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        try:
            data = _replace_today_condition(
                uuid,
                False,
                serializer.validated_data["mood"],
                serializer.validated_data["condition"],
                serializer.validated_data.get("free_text", ""),
            )
        except RuntimeError:
            return Response(
                {"detail": "Supabaseの保存に失敗しました。"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )

        return Response(data, status=status.HTTP_201_CREATED)
