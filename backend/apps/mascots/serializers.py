from __future__ import annotations

from rest_framework import serializers

from .models import Mascot


class MascotSerializer(serializers.ModelSerializer):
    class Meta:
        model = Mascot
        fields = ["id", "name", "description", "image_url"]

