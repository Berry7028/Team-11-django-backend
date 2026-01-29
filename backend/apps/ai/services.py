"""
AI-related service functions.

本番では外部の LLM やレコメンドサービスなどに接続することを想定。
"""

from __future__ import annotations

import json
import os
from datetime import date
from typing import Any

from openai import OpenAI

from .supabase_client import get_supabase_client


def generate_hint(prompt: str) -> str:
    """
    与えられたプロンプトに対して簡易的なヒント文を返すダミー実装。

    本実装では外部サービス連携に差し替える。
    """

    return f"Hint for: {prompt[:50]}..."


# --- AI Recommendations ---

QUEST_SELECTION_TOOLS = [
    {
        "type": "function",
        "name": "save_recommendations",
        "description": "ユーザーの状態に基づいてクエストとマスコットの状態を保存する",
        "parameters": {
            "type": "object",
            "properties": {
                "quests": {
                    "type": "array",
                    "description": "ユーザーに提案するクエスト5件",
                    "items": {
                        "type": "object",
                        "properties": {
                            "title": {
                                "type": "string",
                                "description": "クエストのタイトル",
                            },
                            "description": {
                                "type": "string",
                                "description": "クエストの説明（なぜこのクエストを選んだか含む）",
                            },
                        },
                        "required": ["title", "description"],
                        "additionalProperties": False,
                    },
                },
                "mascot": {
                    "type": "object",
                    "description": "マスコットの状態",
                    "properties": {
                        "status": {
                            "type": "string",
                            "enum": ["Sad", "Bad", "Okay", "Good", "Great"],
                            "description": "マスコットの気分状態",
                        },
                        "message": {
                            "type": "string",
                            "description": "マスコットからユーザーへのメッセージ",
                        },
                    },
                    "required": ["status", "message"],
                    "additionalProperties": False,
                },
            },
            "required": ["quests", "mascot"],
            "additionalProperties": False,
        },
        "strict": True,
    },
]

SYSTEM_PROMPT = """あなたはユーザーのメンタルヘルスをサポートするAIアシスタントです。
                    ユーザーの朝と夜の気分・体調データを分析し、適切なクエスト（軽いタスク）を提案してください。

                    クエストは以下の観点で選んでください：
                    - ユーザーの現在の気分や体調に合った難易度
                    - ストレス軽減や気分転換に役立つもの
                    - 達成感を得やすい小さな目標

                マスコットの状態は、ユーザーの気分を反映させつつ、励ましのメッセージを添えてください。"""


def get_user_condition(user_uuid: str) -> dict[str, Any] | None:
    """Supabaseからユーザーの最新のconditionを取得"""
    client = get_supabase_client()
    result = (
        client.table("users_condition")
        .select("*")
        .eq("uuid", user_uuid)
        .order("created_at", desc=True)
        .limit(1)
        .execute()
    )
    if result.data:
        return result.data[0]
    return None


def save_quests(user_uuid: str, quests: list[dict[str, str]], today: date) -> None:
    """当日のクエストを保存（既存の当日分は削除）"""
    client = get_supabase_client()

    # 当日分を削除
    client.table("quests").delete().eq("uuid", user_uuid).eq(
        "day", today.isoformat()
    ).execute()

    # 新規クエストを挿入
    records = [
        {
            "uuid": user_uuid,
            "title": q["title"],
            "description": q["description"],
            "completed": False,
            "day": today.isoformat(),
        }
        for q in quests
    ]
    client.table("quests").insert(records).execute()


def save_mascot(user_uuid: str, mascot: dict[str, str]) -> None:
    """マスコット状態を保存（既存があれば更新）"""
    client = get_supabase_client()

    existing = (
        client.table("mascots").select("id").eq("uuid", user_uuid).limit(1).execute()
    )

    if existing.data:
        client.table("mascots").update(
            {"status": mascot["status"], "message": mascot["message"]}
        ).eq("uuid", user_uuid).execute()
    else:
        client.table("mascots").insert(
            {
                "uuid": user_uuid,
                "status": mascot["status"],
                "message": mascot["message"],
            }
        ).execute()


def generate_recommendations(user_uuid: str) -> dict[str, Any]:
    """
    ユーザーのconditionを元にOpenAIでクエスト・マスコット状態を生成し、Supabaseに保存する。

    Returns:
        dict: {"quests": [...], "mascot": {...}} or {"error": "..."}
    """
    # 1. users_condition を取得
    condition = get_user_condition(user_uuid)
    if not condition:
        return {"error": "users_condition が見つかりません"}

    # 2. OpenAIへのプロンプトを構築
    user_input = f"""ユーザーの状態:
            - 朝の気分: {condition.get("morning_mood", "未入力")}
            - 朝の体調: {condition.get("morning_condition", "未入力")}
            - 朝のメモ: {condition.get("morning_note", "未入力")}
            - 夜の気分: {condition.get("night_mood", "未入力")}
            - 夜の体調: {condition.get("night_condition", "未入力")}
            - 夜のメモ: {condition.get("night_note", "未入力")}

            この情報を元に、5つのクエストとマスコットの状態を生成してください。"""

    # 3. OpenAI API呼び出し (function calling)
    openai_client = OpenAI(api_key=os.environ.get("OPENAI_API_KEY"))

    response = openai_client.responses.create(
        model="gpt-5.2",
        input=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": user_input},
        ],
        tools=QUEST_SELECTION_TOOLS,
    )

    # 4. Function call結果をパース
    function_call = None
    for item in response.output:
        if item.type == "function_call" and item.name == "save_recommendations":
            function_call = item
            break

    if not function_call:
        return {"error": "AIからの応答が不正です"}

    try:
        args = json.loads(function_call.arguments)
    except json.JSONDecodeError:
        return {"error": "AIからの応答をパースできませんでした"}

    quests = args.get("quests", [])
    mascot = args.get("mascot", {})

    # 5. Supabaseに保存
    today = date.today()
    save_quests(user_uuid, quests, today)
    save_mascot(user_uuid, mascot)

    return {"quests": quests, "mascot": mascot}

