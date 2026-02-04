from __future__ import annotations

import base64
import logging
import os
from typing import List

from google import genai
from google.genai import types

from .services import build_mascot_prompt
from .supabase_client import get_supabase_client

logger = logging.getLogger(__name__)


def _get_env(name: str) -> str:
    value = os.getenv(name)
    if not value:
        raise ValueError(f"{name} is not set")
    return value


def load_reference_images() -> List[bytes]:
    bucket = os.getenv("MASCOT_REFERENCE_BUCKET", "mascot-references")
    paths_raw = os.getenv("MASCOT_REFERENCE_PATHS", "")
    paths = [p.strip() for p in paths_raw.split(",") if p.strip()]
    normalized_paths: List[str] = []
    for path in paths:
        if path.startswith(f"{bucket}/"):
            normalized_paths.append(path[len(bucket) + 1 :])
        else:
            normalized_paths.append(path)
    if not paths:
        raise ValueError("MASCOT_REFERENCE_PATHS is empty")

    client = get_supabase_client()
    images: List[bytes] = []
    for path in normalized_paths:
        try:
            data = client.storage.from_(bucket).download(path)
        except Exception as exc:
            logger.error("Failed to download reference image: %s/%s", bucket, path)
            raise ValueError(f"Reference image not found: {bucket}/{path}") from exc
        if isinstance(data, str):
            data = data.encode("utf-8")
        images.append(data)
    return images


def _normalize_image_bytes(data: object) -> bytes:
    if isinstance(data, bytes):
        return data
    if isinstance(data, str):
        return base64.b64decode(data)
    raise ValueError("Unknown image data format")


def generate_mascot_images(
    personality: str,
    favorite_color: str,
    support_style: str,
    activity_level: str,
) -> List[bytes]:
    """
    5つの表情のマスコット画像を生成

    Returns:
        5つの画像データ（バイト列）のリスト [Sad, Bad, Okay, Good, Great]
    """

    api_key = _get_env("GOOGLE_GENAI_API_KEY")
    client = genai.Client(api_key=api_key)

    moods = ["Sad", "Bad", "Okay", "Good", "Great"]
    image_data_list: List[bytes] = []

    reference_images = load_reference_images()

    for mood in moods:
        prompt = build_mascot_prompt(
            personality, favorite_color, support_style, activity_level, mood
        )

        contents: list[object] = []
        for ref in reference_images:
            contents.append(types.Part.from_bytes(data=ref, mime_type="image/png"))
        contents.append(prompt)

        try:
            response = client.models.generate_content(
                model="gemini-3-pro-image-preview",
                contents=contents,
            )
            image_part = response.candidates[0].content.parts[0]
            image_bytes = _normalize_image_bytes(image_part.inline_data.data)
            image_data_list.append(image_bytes)
            logger.info("Generated %s mascot image successfully", mood)
        except Exception as exc:
            logger.error("Failed to generate %s image: %s", mood, str(exc))
            raise

    return image_data_list
