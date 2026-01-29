from __future__ import annotations

from django.conf import settings
from django.db import models

from apps.quests.models import Quest


class Condition(models.Model):
    """
    条件やステータスを表す簡易モデル。
    例: あるクエストが解放される条件など。
    """

    name = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    quest = models.ForeignKey(
        Quest,
        on_delete=models.CASCADE,
        related_name="conditions",
        null=True,
        blank=True,
    )
    owner = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="conditions",
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["name"]

    def __str__(self) -> str:
        return self.name

