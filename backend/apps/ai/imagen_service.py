from __future__ import annotations

import base64
import io
import logging
import os
from typing import List

from openai import OpenAI

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


def _generate_with_references(
    client: OpenAI,
    prompt: str,
    ref_images: List[bytes],
    extra_refs: List[bytes],
) -> bytes:
    all_images = ref_images + extra_refs
    image_inputs = [
        (f"ref_{i}.png", io.BytesIO(img), "image/png")
        for i, img in enumerate(all_images)
    ]

    response = client.images.edit(
        model="gpt-image-1.5",
        image=image_inputs,
        prompt=prompt,
        size="1024x1024",
        quality="low",
        background="transparent",
    )

    return base64.b64decode(response.data[0].b64_json)


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

    api_key = _get_env("OPENAI_API_KEY")
    client = OpenAI(api_key=api_key)

    moods = ["Sad", "Bad", "Okay", "Good", "Great"]
    image_data_list: List[bytes] = []

    reference_images = load_reference_images()

    generated: dict[str, bytes] = {}

    def _build_prompt(mood: str) -> str:
        return build_mascot_prompt(
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

    try:
        anchor_mood = "Okay"
        anchor_prompt = _build_prompt(anchor_mood)
        anchor_image = _generate_with_references(
            client, anchor_prompt, reference_images, []
        )
        generated[anchor_mood] = anchor_image
        logger.info("Generated %s mascot image successfully", anchor_mood)

        previous_image = anchor_image
        for mood in [m for m in moods if m != anchor_mood]:
            if not previous_image:
                raise ValueError("Previous mascot image is missing")
            prompt = _build_prompt(mood)
            image_bytes = _generate_with_references(
                client,
                prompt,
                reference_images,
                [anchor_image, previous_image],
            )
            generated[mood] = image_bytes
            previous_image = image_bytes
            logger.info("Generated %s mascot image successfully", mood)
    except Exception as exc:
        logger.error("Failed to generate mascot images: %s", str(exc))
        raise

    for mood in moods:
        image_data_list.append(generated[mood])

    return image_data_list
