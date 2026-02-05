from __future__ import annotations

import os
from typing import Optional

from supabase import Client, create_client

_client: Optional[Client] = None


def get_supabase_client() -> Client:
    """
    Supabaseクライアントを取得する。
    環境変数が未設定の場合は例外を投げる。
    """
    global _client

    if _client is not None:
        return _client

    url = os.environ.get("SUPABASE_URL")
    key = os.environ.get("SUPABASE_SERVICE_KEY") or os.environ.get("SUPABASE_KEY")

    if not url or not key:
        raise ValueError(
            "SUPABASE_URL または SUPABASE_SERVICE_KEY/SUPABASE_KEY が未設定です。"
        )

    _client = create_client(url, key)
    return _client
