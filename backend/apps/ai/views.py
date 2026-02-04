"""
AI API endpoints.
"""

from __future__ import annotations

import logging

from rest_framework import permissions, status
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView

from .imagen_service import generate_mascot_images
from .services import generate_hint, generate_recommendations, get_mascot_state
from .storage_service import upload_mascot_images
from .supabase_client import get_supabase_client

logger = logging.getLogger(__name__)


class HintView(APIView):
    """
    POST /api/ai/hints/

    リクエスト:
    - body: { "prompt": string }

    レスポンス:
    - body: { "hint": string }
    """

    permission_classes = [permissions.AllowAny]

    def post(self, request: Request) -> Response:
        prompt = request.data.get("prompt", "")
        if not prompt:
            return Response(
                {"detail": "prompt is required"},
                status=status.HTTP_400_BAD_REQUEST,
            )
        hint = generate_hint(prompt)
        return Response({"hint": hint})


class RecommendationsView(APIView):
    """
    POST /api/ai/recommendations/

    ユーザーのconditionを元にAIがクエストとマスコット状態を生成しSupabaseに保存する。

    リクエストヘッダー:
    - X-User-UUID: string (必須)

    レスポンス:
    - 成功時: { "quests": [...], "mascot": {...} }
    - エラー時: { "error": "..." }
    """

    permission_classes = [permissions.AllowAny]

    def post(self, request: Request) -> Response:
        user_uuid = request.headers.get("X-User-UUID")
        if not user_uuid:
            return Response(
                {"error": "X-User-UUID ヘッダーが必要です"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        result = generate_recommendations(user_uuid)

        if "error" in result:
            return Response(result, status=status.HTTP_400_BAD_REQUEST)

        return Response(result, status=status.HTTP_200_OK)



class MascotStateView(APIView):
    permission_classes = [permissions.AllowAny]

    def get(self, request: Request) -> Response:
        user_uuid = request.headers.get("X-User-UUID")

        if not user_uuid:
            return Response(
                {"error": "X-User-UUID ヘッダーが必要です"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        mascot = get_mascot_state(user_uuid)

        if mascot is None:
            return Response(
                {"error": "mascot not found"},
                status=status.HTTP_404_NOT_FOUND,
            )

        return Response(mascot, status=status.HTTP_200_OK)


class MascotOnboardingView(APIView):
    """
    POST /api/ai/onboarding/complete/

    アンケート結果からマスコット画像を生成して保存する。
    """

    permission_classes = [permissions.AllowAny]

    def post(self, request: Request) -> Response:
        user_uuid = request.headers.get("X-User-UUID")
        if not user_uuid:
            return Response(
                {"error": "X-User-UUID ヘッダーが必要です"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        personality = request.data.get("personality")
        favorite_color = request.data.get("favorite_color")
        support_style = request.data.get("support_style")
        activity_level = request.data.get("activity_level")
        social_energy = request.data.get("social_energy")
        decision_style = request.data.get("decision_style")
        change_preference = request.data.get("change_preference")
        stress_coping = request.data.get("stress_coping")
        emotional_expression = request.data.get("emotional_expression")

        if not all(
            [
                personality,
                favorite_color,
                support_style,
                activity_level,
                social_energy,
                decision_style,
                change_preference,
                stress_coping,
                emotional_expression,
            ]
        ):
            return Response(
                {"error": "All fields are required"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        try:
            image_data_list = generate_mascot_images(
                personality,
                favorite_color,
                support_style,
                activity_level,
                social_energy,
                decision_style,
                change_preference,
                stress_coping,
                emotional_expression,
            )
            image_urls = upload_mascot_images(user_uuid, image_data_list)

            client = get_supabase_client()
            existing = (
                client.table("mascots")
                .select("id")
                .eq("uuid", user_uuid)
                .limit(1)
                .execute()
            )

            if existing.data and len(existing.data) > 0:
                client.table("mascots").update(
                    {
                        "image_urls": image_urls,
                    }
                ).eq("uuid", user_uuid).execute()
            else:
                client.table("mascots").insert(
                    {
                        "uuid": user_uuid,
                        "status": "Okay",
                        "message": "よろしくね！一緒に頑張ろう！",
                        "image_urls": image_urls,
                    }
                ).execute()

            return Response(
                {
                    "mascot_id": user_uuid,
                    "image_urls": image_urls,
                    "message": "あなた専用のキャラクターが完成しました！",
                },
                status=status.HTTP_201_CREATED,
            )
        except Exception as exc:
            logger.error("Onboarding failed: %s", str(exc))
            return Response(
                {"error": "Failed to generate mascot", "details": str(exc)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )
    
