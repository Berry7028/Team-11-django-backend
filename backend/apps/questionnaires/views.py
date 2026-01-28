"""
Questionnaires API endpoints.
"""

from __future__ import annotations

from rest_framework import permissions, viewsets

from .models import Answer, Questionnaire
from .serializers import AnswerSerializer, QuestionnaireSerializer


class QuestionnaireViewSet(viewsets.ReadOnlyModelViewSet):
    """
    アンケート一覧/詳細を提供。
    """

    queryset = Questionnaire.objects.all()
    serializer_class = QuestionnaireSerializer
    permission_classes = [permissions.AllowAny]


class AnswerViewSet(viewsets.ModelViewSet):
    """
    回答送信エンドポイント。
    """

    queryset = Answer.objects.all()
    serializer_class = AnswerSerializer
    permission_classes = [permissions.AllowAny]

