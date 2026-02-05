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


def _normalize_storage_path(bucket: str, path: str) -> str:
    cleaned = path.strip().lstrip("/")
    if cleaned.startswith(f"{bucket}/"):
        return cleaned[len(bucket) + 1 :]
    return cleaned


def _list_reference_paths(bucket: str, prefix: str) -> List[str]:
    client = get_supabase_client()
    normalized_prefix = prefix.strip().lstrip("/").rstrip("/")
    list_path = normalized_prefix or ""
    try:
        entries = client.storage.from_(bucket).list(
            path=list_path,
            options={"limit": 1000},
        )
    except TypeError:
        entries = client.storage.from_(bucket).list(path=list_path)

    paths: List[str] = []
    for entry in entries or []:
        if not isinstance(entry, dict):
            continue
        name = entry.get("name")
        if not name:
            continue
        if name.endswith("/"):
            continue
        if normalized_prefix:
            paths.append(f"{normalized_prefix}/{name}")
        else:
            paths.append(name)

    paths.sort()
    return paths


def load_reference_images() -> List[bytes]:
    bucket = os.getenv("MASCOT_REFERENCE_BUCKET", "mascot-references")
    paths_raw = os.getenv("MASCOT_REFERENCE_PATHS", "")
    prefix_raw = os.getenv("MASCOT_REFERENCE_PREFIX", "")

    using_explicit_paths = bool(paths_raw.strip())
    if using_explicit_paths:
        raw_paths = [p for p in paths_raw.split(",") if p.strip()]
        normalized_paths = [_normalize_storage_path(bucket, p) for p in raw_paths]
    else:
        normalized_paths = _list_reference_paths(bucket, prefix_raw)
        if not normalized_paths:
            raise ValueError("No reference images found in bucket")

    client = get_supabase_client()
    images: List[bytes] = []
    for path in normalized_paths:
        try:
            data = client.storage.from_(bucket).download(path)
        except Exception as exc:
            if using_explicit_paths:
                logger.error("Failed to download reference image: %s/%s", bucket, path)
                raise ValueError(
                    f"Reference image not found: {bucket}/{path}"
                ) from exc
            logger.warning(
                "Skipping non-file entry or inaccessible path: %s/%s",
                bucket,
                path,
            )
            continue
        if isinstance(data, str):
            data = data.encode("utf-8")
        images.append(data)

    if not images:
        raise ValueError("No reference images could be downloaded")

    if len(images) != 5:
        logger.warning(
            "Expected 5 reference images but found %s (bucket=%s prefix=%s)",
            len(images),
            bucket,
            prefix_raw or "/",
        )

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
    social_energy: str,
    decision_style: str,
    change_preference: str,
    stress_coping: str,
    emotional_expression: str,
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
            personality,
            favorite_color,
            support_style,
            activity_level,
            social_energy,
            decision_style,
            change_preference,
            stress_coping,
            emotional_expression,
            mood,
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
