"""
AI API endpoints.
"""

from __future__ import annotations

from rest_framework import permissions, status
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView

from .services import generate_hint, generate_recommendations, get_mascot_state


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
    
