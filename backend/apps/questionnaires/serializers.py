from __future__ import annotations

from rest_framework import serializers

from .models import Answer, Question, Questionnaire


class QuestionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Question
        fields = ["id", "text"]


class QuestionnaireSerializer(serializers.ModelSerializer):
    questions = QuestionSerializer(many=True, read_only=True)

    class Meta:
        model = Questionnaire
        fields = ["id", "title", "description", "questions"]


class AnswerSerializer(serializers.ModelSerializer):
    class Meta:
        model = Answer
        fields = ["id", "questionnaire", "submitted_at", "payload"]
        read_only_fields = ["submitted_at"]


class QuestionnaireRequestSerializer(serializers.Serializer):
    mood = serializers.ChoiceField(
        choices=["絶好調", "いい感じ", "ふつう", "モヤモヤ", "つらい"],
    )
    condition = serializers.ChoiceField(
        choices=["絶好調", "いい感じ", "ふつう", "少しだるい", "つらい"],
    )
    free_text = serializers.CharField(
        allow_blank=True,
        required=False,
        max_length=1000,
    )

