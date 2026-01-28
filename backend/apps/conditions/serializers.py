from __future__ import annotations

from rest_framework import serializers

from .models import Condition


class ConditionSerializer(serializers.ModelSerializer):
    owner_username = serializers.ReadOnlyField(source="owner.username")

    class Meta:
        model = Condition
        fields = [
            "id",
            "name",
            "description",
            "quest",
            "owner",
            "owner_username",
            "created_at",
        ]
        read_only_fields = ["owner", "owner_username", "created_at"]

