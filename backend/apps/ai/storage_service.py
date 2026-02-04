from __future__ import annotations

import os
from typing import Dict, List

from .supabase_client import get_supabase_client


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
    client = get_supabase_client()

    moods = ["Sad", "Bad", "Okay", "Good", "Great"]
    image_urls: Dict[str, str] = {}

    for mood, image_data in zip(moods, image_data_list):
        file_name = f"mascots/{user_uuid}/{mood.lower()}.png"
        client.storage.from_(bucket).upload(
            file_name,
            image_data,
            file_options={"content-type": "image/png"},
        )
        public_url_raw = client.storage.from_(bucket).get_public_url(file_name)
        image_urls[mood] = _extract_public_url(public_url_raw)

    return image_urls
