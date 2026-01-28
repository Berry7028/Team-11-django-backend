from __future__ import annotations

from django.db import models


class Mascot(models.Model):
    """
    アプリ内で利用するマスコットキャラクター。
    """

    name = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    image_url = models.URLField(blank=True)

    def __str__(self) -> str:
        return self.name

