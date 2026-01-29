from __future__ import annotations

from rest_framework import serializers

from .models import Quest


class QuestSerializer(serializers.ModelSerializer):
    owner_username = serializers.ReadOnlyField(source="owner.username")

    class Meta:
        model = Quest
        fields = [
            "id",
            "title",
            "description",
            "owner",
            "owner_username",
            "is_active",
            "created_at",
        ]
        read_only_fields = ["owner", "owner_username", "created_at"]

