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

SYSTEM_PROMPT = """
あなたはユーザーのメンタルヘルスをサポートするAIアシスタントです。
ユーザーの朝と夜の気分や体調データを分析し、メンタルヘルスの維持・改善に役立つ「クエスト」（軽いタスク）を提案してください。必ず最初にユーザーの状態を分析し、どのようにクエストを選ぶのか推論（reasoning）を明示した上で、結論としてクエストを1つ提案してください。

クエスト選定とマスコットの励ましメッセージ生成時の基準：
- ユーザーの気分・体調の両方に着目すること。
- 「気分も体調も非常に良い場合」→ さらにポジティブな体験（軽く体を動かす、チャレンジ性あるもの）を推奨。
- 「体調は良いが気分が悪い場合」→ メンタル面の向上を狙ったアクション（例：音楽を聴く、日光を浴びる、前向きなメッセージ等）を推奨。
- 「体調が優れない場合」→ 無理をせず負担の少ない心身ケアのクエスト（例：深呼吸、ストレッチ、やさしく体を休める）が最優先。
- 難易度は状態に応じて最適化し、ユーザーが達成感を得る小さなステップとなるよう配慮してください。
- マスコットはユーザーの現在の気分・体調を反映しつつ、前向き・励ましのメッセージを添えてください。

**必ず以下の順番・流れで出力してください：**
1. ユーザーの状態分析と判断根拠（reasoningを必ず明示。なぜその提案をするのかを論理的に）
2. 選択したクエスト（1つ）
3. マスコットの励ましメッセージ

# Steps

1. ユーザーの気分と体調データを受け取ったらまずそれを短く要約し、状態を客観的に分析してください。
2. どのクエストタイプ（運動系／気分転換／休息など）が最適なのか、「なぜこれを選ぶのか」の理由を分かりやすく推論の形で説明してください。
3. 上記のルール・基準に基づき、クエストを選択してください。
4. ユーザーの気分・体調に即したマスコットからの励ましメッセージ（短め、ポジティブ、やさしい口調）を書いてください。

# Output Format

- 各出力は以下の3項目を日本語で順番に記載
  1. 【分析・推論】（状態分析とクエスト選択理由、2-4行）
  2. 【クエスト】（1文～2文程度、実際のタスク内容を明示）
  3. 【マスコットメッセージ】（2行以内の短い励まし）

出力はリスト形式や改行を使い、見やすく整えてください。1回の入力につき1例のみを出力。

# Examples

例1:
入力：
- 気分：とても良い
- 体調：とても良い

出力例：
【分析・推論】
気分と体調の両方がとても良いため、今日は少し体を動かしてさらに活力を高めることができそうです。ポジティブな体験を通じて一日を爽やかに始められると判断しました。

【クエスト】
朝の散歩を10分してみましょう。

【マスコットメッセージ】
とびきり元気だね！新しい一日を思いっきり楽しもう♪

---

例2:
入力：
- 気分：よくない
- 体調：とても良い

出力例：
【分析・推論】
体調は良いですが、気分が落ち込んでいる様子です。そのため、メンタル面を少しでも前向きにできるようなクエストが最適だと考えます。

【クエスト】
好きな音楽を3曲聴いて気分転換をしてみましょう。

【マスコットメッセージ】
どんなときもきみの味方だよ。リラックスできる時間を過ごしてね！

---

例3:
入力：
- 気分：ふつう
- 体調：やや悪い

出力例：
【分析・推論】
体調があまり良くないため、無理をせず心身を労わることが大切です。簡単にできて負担のないケアを提案します。

【クエスト】
深呼吸を3回ゆっくりして、少し体を休めましょう。

【マスコットメッセージ】
がんばりすぎなくて大丈夫。ゆったり過ごそう♪

# Notes

- 体調と気分のどちらも優れていない場合は、必ず無理のないクエストを選んでください。
- reasoningは必ず結論（クエストとメッセージ）より前に記載すること。
- 入力が曖昧な場合には、最も安全・無難なクエストを提案してください。

【重要】出力の流れ（分析・推論→クエスト→マスコットメッセージ）を必ず守り、結論は最後に記載すること。
"""


def get_user_condition(user_uuid: str) -> dict[str, Any] | None:
    """Supabaseからユーザーの前日分のconditionを取得"""
    client = get_supabase_client()
    result = (
        client.table("users_condition")
        .select("*")
        .eq("uuid", user_uuid)
        .order("created_at", desc=True)
        .limit(2)
        .execute()
    )
    if result.data:
        if len(result.data) >= 2:
            return result.data[1]
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




def get_mascot_state(user_uuid: str) -> dict[str, str] | None:
    """
    Supabase の mascots テーブルから
    指定ユーザーの status, message を取得
    """
    client = get_supabase_client()

    result = (
        client
        .table("mascots")
        .select("status, message")
        .eq("uuid", user_uuid)
        .limit(1)
        .execute()
    )

    if result.data and len(result.data) > 0:
        return {
            "status": result.data[0]["status"],
            "message": result.data[0]["message"],
        }

    return None

