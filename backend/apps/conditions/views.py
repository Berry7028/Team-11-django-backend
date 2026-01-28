"""
Conditions API endpoints.
"""

from __future__ import annotations

from rest_framework import permissions, viewsets

from .models import Condition
from .serializers import ConditionSerializer


class ConditionViewSet(viewsets.ModelViewSet):
    queryset = Condition.objects.select_related("owner", "quest").all()
    serializer_class = ConditionSerializer
    permission_classes = [permissions.IsAuthenticated]

    def perform_create(self, serializer: ConditionSerializer) -> None:
        serializer.save(owner=self.request.user)

