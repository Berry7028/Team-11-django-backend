from __future__ import annotations

from rest_framework import serializers

from .models import LogEntry


class LogEntrySerializer(serializers.ModelSerializer):
    user_username = serializers.ReadOnlyField(source="user.username")

    class Meta:
        model = LogEntry
        fields = ["id", "user", "user_username", "action", "metadata", "created_at"]
        read_only_fields = ["user", "user_username", "created_at"]

