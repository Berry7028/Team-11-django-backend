"""
AI-related service functions.

本番では外部の LLM やレコメンドサービスなどに接続することを想定。
"""

from __future__ import annotations


def generate_hint(prompt: str) -> str:
    """
    与えられたプロンプトに対して簡易的なヒント文を返すダミー実装。

    本実装では外部サービス連携に差し替える。
    """

    return f"Hint for: {prompt[:50]}..."

