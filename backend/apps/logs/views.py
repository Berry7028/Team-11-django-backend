"""
Logs API endpoints.
"""

from __future__ import annotations

from rest_framework import permissions, viewsets

from .models import LogEntry
from .serializers import LogEntrySerializer


class LogEntryViewSet(viewsets.ReadOnlyModelViewSet):
    """
    読み取り専用のログ一覧 API。
    """

    queryset = LogEntry.objects.select_related("user").all()
    serializer_class = LogEntrySerializer
    permission_classes = [permissions.IsAdminUser]

