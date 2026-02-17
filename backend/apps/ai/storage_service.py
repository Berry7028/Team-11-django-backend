from __future__ import annotations

import os
from typing import Dict, List

from .supabase_client import get_supabase_client

MAX_MASCOT_IMAGES = 5
MAX_IMAGE_BYTES = 5 * 1024 * 1024


def _extract_public_url(value: object) -> str:
    if isinstance(value, str):
        return value
    if isinstance(value, dict):
        if "publicUrl" in value:
            return value["publicUrl"]
        if "public_url" in value:
            return value["public_url"]
    raise ValueError("Unexpected public URL response")


def upload_mascot_images(user_uuid: str, image_data_list: List[bytes]) -> Dict[str, str]:
    """
    Supabase Storage に画像をアップロード

    Returns:
        各表情の画像URL辞書 {"Sad": "https://...", ...}
    """

    bucket = os.getenv("MASCOT_IMAGES_BUCKET", "mascot-images")

    if len(image_data_list) != MAX_MASCOT_IMAGES:
        raise ValueError(f"Expected {MAX_MASCOT_IMAGES} mascot images")
    for image_data in image_data_list:
        if not isinstance(image_data, bytes):
            raise ValueError("Image payload must be bytes")
        if len(image_data) > MAX_IMAGE_BYTES:
            raise ValueError("Image payload is too large")

    client = get_supabase_client()

    moods = ["Sad", "Bad", "Okay", "Good", "Great"]
    image_urls: Dict[str, str] = {}

    for mood, image_data in zip(moods, image_data_list):
        file_name = f"mascots/{user_uuid}/{mood.lower()}.png"
        client.storage.from_(bucket).upload(
            file_name,
            image_data,
            # Supabase expects header values as str/bytes; avoid bool in headers.
            file_options={"content-type": "image/png", "upsert": "true"},
        )
        public_url_raw = client.storage.from_(bucket).get_public_url(file_name)
        image_urls[mood] = _extract_public_url(public_url_raw)

    return image_urls
