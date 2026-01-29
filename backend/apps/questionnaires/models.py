from __future__ import annotations

from django.db import models


class Questionnaire(models.Model):
    title = models.CharField(max_length=255)
    description = models.TextField(blank=True)

    def __str__(self) -> str:
        return self.title


class Question(models.Model):
    questionnaire = models.ForeignKey(
        Questionnaire, on_delete=models.CASCADE, related_name="questions"
    )
    text = models.TextField()

    def __str__(self) -> str:
        return self.text[:50]


class Answer(models.Model):
    questionnaire = models.ForeignKey(
        Questionnaire, on_delete=models.CASCADE, related_name="answers"
    )
    submitted_at = models.DateTimeField(auto_now_add=True)
    payload = models.JSONField()

    def __str__(self) -> str:
        return f"Answer to {self.questionnaire_id} at {self.submitted_at}"

