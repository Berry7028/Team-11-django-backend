from __future__ import annotations

from django.conf import settings
from django.db import models


class LogEntry(models.Model):
    """
    シンプルなログ/監査用エントリ。
    """

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="log_entries",
    )
    action = models.CharField(max_length=255)
    metadata = models.JSONField(blank=True, default=dict)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self) -> str:
        return f"{self.action} ({self.created_at:%Y-%m-%d %H:%M:%S})"

