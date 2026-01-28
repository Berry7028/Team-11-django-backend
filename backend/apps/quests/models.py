from __future__ import annotations

from django.conf import settings
from django.db import models


class Quest(models.Model):
    """
    RN 側で一覧・詳細・達成フローなどを扱うクエストモデル。
    """

    title = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    owner = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="owned_quests",
    )
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self) -> str:
        return self.title

