from __future__ import annotations

from django.conf import settings
from django.db import models


class UserProfile(models.Model):
    """
    Basic user profile extension.

    RN 側からは「現在ログイン中ユーザー情報」取得などで利用する想定。
    """

    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="profile",
    )
    display_name = models.CharField(max_length=150, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "User profile"
        verbose_name_plural = "User profiles"

    def __str__(self) -> str:
        return self.display_name or self.user.get_username()

