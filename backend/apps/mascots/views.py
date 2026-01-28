"""
Mascots API endpoints.
"""

from __future__ import annotations

from rest_framework import permissions, viewsets

from .models import Mascot
from .serializers import MascotSerializer


class MascotViewSet(viewsets.ModelViewSet):
    queryset = Mascot.objects.all()
    serializer_class = MascotSerializer
    permission_classes = [permissions.AllowAny]

