"""
AI API endpoints.
"""

from __future__ import annotations

from rest_framework import permissions, status
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView

from .services import generate_hint


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

