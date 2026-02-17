from __future__ import annotations

from types import SimpleNamespace
from unittest.mock import Mock

from django.test import SimpleTestCase

from .views import QuestViewSet


class QuestViewSetOwnershipTests(SimpleTestCase):
    def test_get_queryset_filters_by_request_user(self) -> None:
        queryset = Mock()
        view = QuestViewSet()
        view.queryset = queryset
        user = SimpleNamespace(id=1)
        view.request = SimpleNamespace(user=user)

        filtered_queryset = object()
        queryset.filter.return_value = filtered_queryset

        result = view.get_queryset()

        queryset.filter.assert_called_once_with(owner=user)
        self.assertIs(result, filtered_queryset)
