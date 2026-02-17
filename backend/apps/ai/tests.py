from __future__ import annotations

from django.test import SimpleTestCase

from .storage_service import upload_mascot_images


class UploadMascotImagesValidationTests(SimpleTestCase):
    def test_rejects_unexpected_image_count(self) -> None:
        with self.assertRaises(ValueError):
            upload_mascot_images("user-1", [b"img1"])

    def test_rejects_too_large_image(self) -> None:
        large = b"a" * (5 * 1024 * 1024 + 1)
        images = [b"ok", b"ok", large, b"ok", b"ok"]
        with self.assertRaises(ValueError):
            upload_mascot_images("user-1", images)
