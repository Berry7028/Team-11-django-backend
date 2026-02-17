from __future__ import annotations

from rest_framework import status
from rest_framework.test import APISimpleTestCase


class AnswerViewSetTests(APISimpleTestCase):
    def test_answer_get_is_not_allowed(self) -> None:
        response = self.client.get("/api/questionnaires/answers")
        self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)
