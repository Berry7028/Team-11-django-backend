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


def build_mascot_prompt(
    personality: str,
    favorite_color: str,
    support_style: str,
    activity_level: str,
    social_energy: str,
    decision_style: str,
    change_preference: str,
    stress_coping: str,
    emotional_expression: str,
    mood_status: str,
) -> str:
    """
    アンケート結果から Gemini 3 Pro Image Preview 用のプロンプトを生成する。
    参照画像と組み合わせて既存テイストに寄せる。
    """

    personality_traits = {
        "元気いっぱい": "energetic and cheerful, round and bouncy design",
        "おっとり穏やか": "calm and gentle, soft rounded features",
        "真面目で几帳面": "serious and organized, clean sharp lines",
        "天然でマイペース": "airheaded and easygoing, fluffy asymmetric design",
        "ツンデレ": "tsundere personality, sharp but cute features",
    }

    color_mapping = {
        "赤系": "warm red and orange tones",
        "青系": "cool blue tones",
        "緑系": "natural green tones",
        "黄色系": "bright yellow tones",
        "紫系": "mystical purple tones",
        "ピンク系": "soft pink tones",
    }

    support_styles = {
        "元気に励ます": "high-energy, upbeat encouragement",
        "優しく寄り添う": "gentle and empathetic encouragement",
        "論理的にアドバイス": "calm and thoughtful encouragement",
        "ユーモアで和ませる": "playful and humorous encouragement",
    }

    activity_levels = {
        "アクティブ": "dynamic pose with lively energy",
        "バランス型": "balanced and relaxed pose",
        "のんびり": "slow and cozy pose",
    }

    social_energies = {
        "人といると元気になる": "extroverted and socially energized",
        "ほどよくバランス": "balanced between social and quiet time",
        "一人の時間で充電する": "introverted, calm and reflective",
    }

    decision_styles = {
        "論理や事実を重視": "logic-driven and analytical",
        "気持ちや共感を重視": "empathy-driven and warm",
        "状況で使い分ける": "adaptive and balanced decision-making",
    }

    change_preferences = {
        "計画通りが安心": "structured and organized",
        "柔軟に合わせたい": "flexible and spontaneous",
        "ほどよく両方": "balanced between structure and flexibility",
    }

    stress_copings = {
        "一人で落ち着く": "recovers through quiet time",
        "誰かと話す": "recovers through conversation",
        "体を動かす": "recovers through movement",
        "よく寝る・休む": "recovers through rest",
    }

    emotional_expressions = {
        "表情や言葉に出す": "expressive and open",
        "内に留めがち": "reserved and gentle",
        "行動で示す": "shows feelings through actions",
    }

    mood_expressions = {
        "Sad": "very sad expression, downturned eyes, tears",
        "Bad": "slightly sad expression, worried look",
        "Okay": "neutral calm expression, gentle smile",
        "Good": "happy expression, bright smile",
        "Great": "extremely joyful expression, sparkling eyes, big smile",
    }

    prompt = f"""# マスコットイラスト指示書

かわいく親しみやすい、精神的健康をサポートするアプリ用の3D風マスコットキャラクターを作成してください。

## キャラクター特徴
- **性格:** {personality_traits.get(personality, personality)}
- **カラースキーム:** {color_mapping.get(favorite_color, favorite_color)}
- **応援スタイル:** {support_styles.get(support_style, support_style)}
- **ポーズ・活発度:** {activity_levels.get(activity_level, activity_level)}
- **社交性エネルギー:** {social_energies.get(social_energy, social_energy)}
- **決断スタイル:** {decision_styles.get(decision_style, decision_style)}
- **変化への好み:** {change_preferences.get(change_preference, change_preference)}
- **ストレス回復方法:** {stress_copings.get(stress_coping, stress_coping)}
- **感情表現:** {emotional_expressions.get(emotional_expression, emotional_expression)}
- **表情（気分に基づく）:** {mood_expressions.get(mood_status, "ニュートラルな表情")}

## その他条件
- スタイル: 3D風のデザイン、220x220px推奨
- 雰囲気: 親しみやすく、励ましてくれる印象
- 形式: デジタルイラスト、プロレベルのクオリティ
- 参照画像のキャラクターの形状、質感、配色、ライティングに一致させる


"""

    return prompt


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
ユーザーの朝と夜の気分や体調データを分析し、メンタルヘルスの維持・改善に役立つ「クエスト」（軽いタスク）を5件提案してください。必ず最初にユーザーの状態を分析し、どのようにクエストを選ぶのか推論（reasoning）を明示した上で、結論としてクエストを5件提案してください。

クエスト選定とマスコットの励ましメッセージ生成時の基準：
- **朝のメモ・夜のメモ（自由記述）を最優先に扱うこと。** メモに「やりたいこと」「避けたいこと」「具体的な状況」が書かれている場合は、その内容を反映したクエストを必ず含めてください。メモが空でない限り、少なくとも1つはメモの内容に沿ったクエストを提案すること。
- **「できなかったこと」がメモに書かれている場合は、負担の少ない「少しだけ」の代替案をクエストにすること。** 例：「今日はお風呂に入れなかった」→「シャワーだけでも浴びてみよう」、「外に出られなかった」→「窓を開けて外の空気を吸ってみよう」など、無理のない小さな一歩を提案する。
- **ユーザーの調子が良い場合（気分・体調が「良い」「とても良い」などポジティブ）**は、自由記述の内容を**強く反映するクエストは2件まで**に抑え、**残りのクエストは日常生活の中で無理なくできる運動系クエスト**（例: 軽いストレッチ、短い散歩、姿勢を整える、肩回し等）を提案してください。
- ユーザーの気分・体調の両方に着目すること。
- 「気分も体調も非常に良い場合」→ さらにポジティブな体験（軽く体を動かす、チャレンジ性あるもの）を推奨。
- 「体調は良いが気分が悪い場合」→ メンタル面の向上を狙ったアクション（例：音楽を聴く、日光を浴びる、前向きなメッセージ等）を推奨。
- 「体調が優れない場合」→ 無理をせず負担の少ない心身ケアのクエスト（例：深呼吸、ストレッチ、やさしく体を休める）が最優先。
- 難易度は状態に応じて最適化し、ユーザーが達成感を得る小さなステップとなるよう配慮してください。
- マスコットはユーザーの現在の気分・体調を反映しつつ、前向き・励ましのメッセージを添えてください。
- **最新2件のうち両方で気分が「つらい」になっている場合のみ**、マスコットの状態を「Bad」または「Sad」にしてください。1件だけ「つらい」の場合は急に「Bad」「Sad」にしないでください。

**必ず以下の順番・流れで出力してください：**
1. ユーザーの状態分析と判断根拠（reasoningを必ず明示。なぜその提案をするのかを論理的に）
2. 選択したクエスト（5件）
3. マスコットの励ましメッセージ

# Steps

1. **まず朝のメモ・夜のメモを確認する。** メモに具体的な希望・状況（やりたいこと、避けたいこと、制約など）が書かれていれば、それを最優先でクエストに反映する。
2. ユーザーの気分と体調データを受け取ったらそれを短く要約し、状態を客観的に分析してください。
3. どのクエストタイプ（運動系／気分転換／休息など）が最適なのか、「なぜこれを選ぶのか」の理由を分かりやすく推論の形で説明してください。メモの内容があればその反映理由も含める。
4. 上記のルール・基準に基づき、クエストを選択してください。
5. ユーザーの気分・体調に即したマスコットからの励ましメッセージ（短め、ポジティブ、やさしい口調）を書いてください。

# Output Format

- 各出力は以下の3項目を日本語で順番に記載
  1. 【分析・推論】（状態分析とクエスト選択理由、2-4行）
  2. 【クエスト】（5件、各1文～2文程度で実際のタスク内容を明示）
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
1. 朝の散歩を10分してみましょう。
2. その場で肩回しを10回して、体をほぐしましょう。
3. 背筋を伸ばして1分だけ深呼吸してみましょう。
4. 水を1杯飲んで、体を整えましょう。
5. 簡単なストレッチを2分だけやってみましょう。

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
1. 好きな音楽を3曲聴いて気分転換をしてみましょう。
2. その場で足首を回して軽くほぐしましょう。
3. 窓の外を1分見て、気分を切り替えましょう。
4. 肩をすくめて脱力する動きを5回やってみましょう。
5. 背中を伸ばすストレッチを1分だけやってみましょう。

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
1. 深呼吸を3回ゆっくりして、少し体を休めましょう。
2. 目を閉じて1分だけ静かに過ごしましょう。
3. できる範囲で首をゆっくり回してほぐしましょう。
4. ぬるめの飲み物を少しだけ飲んでみましょう。
5. 今日は早めに横になれる時間を作りましょう。

【マスコットメッセージ】
がんばりすぎなくて大丈夫。ゆったり過ごそう♪

---

例4（メモに「できなかったこと」がある場合）:
入力：
- 気分：ふつう
- 体調：やや悪い
- 夜のメモ：今日はお風呂に入れなかった

出力例：
【分析・推論】
体調がやや悪く、お風呂に入れなかったとのことです。無理に浴槽に入る必要はなく、負担の少ない「少しだけ」の代替として、シャワーだけ浴びるクエストを提案します。

【クエスト】
1. シャワーだけでも浴びてみよう。さっぱりするだけで気分が少し楽になるかも。
2. 肩回しをゆっくり5回やってみよう。
3. その場で足踏みを30秒だけしてみよう。
4. 窓を少し開けて外の空気を吸ってみよう。
5. 目を閉じて深呼吸を2回だけしてみよう。

【マスコットメッセージ】
今日はシャワーだけで十分だよ。無理しないでね♪

# Notes

- **朝のメモ・夜のメモに具体的な希望や状況が書かれている場合は、それを最優先にクエストに反映すること。** 例：「外に出たくない」→ 室内でできるクエストのみ、「散歩したい」→ 散歩系を1つ以上含める、など。
- **「今日は〇〇できなかった」のようにできなかったことが書かれている場合は、その行為の「軽い代替」（少しだけ・短時間で・一部分だけ）をクエストにすること。** 例：お風呂→シャワーだけ、外に出る→窓を開けて換気、など。責めずに「できたらいいね」程度の提案にする。
- 体調と気分のどちらも優れていない場合は、必ず無理のないクエストを選んでください。
- reasoningは必ず結論（クエストとメッセージ）より前に記載すること。
- 入力が曖昧な場合には、最も安全・無難なクエストを提案してください。

【重要】出力の流れ（分析・推論→クエスト→マスコットメッセージ）を必ず守り、結論は最後に記載すること。
"""


def get_user_conditions(user_uuid: str, limit: int = 2) -> list[dict[str, Any]]:
    """Supabaseからユーザーの最新N件のconditionを取得"""
    client = get_supabase_client()
    result = (
        client.table("users_condition")
        .select("*")
        .eq("uuid", user_uuid)
        .order("created_at", desc=True)
        .limit(limit)
        .execute()
    )
    return result.data if result.data else []


def get_user_personality(user_uuid: str) -> dict[str, Any] | None:
    """Supabaseからユーザーの性格設定を取得（mascotsテーブルから）"""
    client = get_supabase_client()
    result = (
        client.table("mascots")
        .select("personality_tags, personality_note")
        .eq("uuid", user_uuid)
        .limit(1)
        .execute()
    )
    if result.data and len(result.data) > 0:
        return {
            "personality_tags": result.data[0].get("personality_tags") or [],
            "personality_note": result.data[0].get("personality_note") or "",
        }
    return None


def get_user_condition(user_uuid: str) -> dict[str, Any] | None:
    """Supabaseからユーザーの最新のconditionを取得（後方互換）"""
    conditions = get_user_conditions(user_uuid, limit=1)
    return conditions[0] if conditions else None


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

    def _get_value(condition: dict[str, Any] | None, key: str, default: str) -> Any:
        if not condition:
            return default
        value = condition.get(key)
        return default if value in (None, "") else value

    # 1. users_condition を取得（最新2件: 最新 + 1つ前）
    conditions = get_user_conditions(user_uuid, limit=2)
    if not conditions:
        return {"error": "users_condition が見つかりません"}

    latest = conditions[0]
    previous = conditions[1] if len(conditions) > 1 else None

    # 1.5. ユーザーの性格設定を取得
    personality = get_user_personality(user_uuid)
    personality_tags = personality.get("personality_tags", []) if personality else []
    personality_note = personality.get("personality_note", "") if personality else ""

    # 2. OpenAIへのプロンプトを構築
    personality_section = ""
    if personality_tags or personality_note:
        personality_section = f"""
【マスコットの性格設定】
- 性格タグ: {", ".join(personality_tags) if personality_tags else "未設定"}
- 話し方の補足: {personality_note if personality_note else "未設定"}

※ マスコットの性格設定がある場合は、マスコットのメッセージをこの性格・話し方で生成してください。
  例: 「元気いっぱい」なら明るくテンション高めに、「おっとり」ならゆったり優しく、「ツンデレ」なら少し素っ気なくも応援する感じで。
"""

    user_input = f"""ユーザーの状態（最新2件）:
{personality_section}
【最新】(created_at: {_get_value(latest, "created_at", "不明")})
- 朝の気分: {_get_value(latest, "morning_mood", "未入力")}
- 朝の体調: {_get_value(latest, "morning_condition", "未入力")}
- 朝のメモ: {_get_value(latest, "morning_note", "未入力")}
- 夜の気分: {_get_value(latest, "night_mood", "未入力")}
- 夜の体調: {_get_value(latest, "night_condition", "未入力")}
- 夜のメモ: {_get_value(latest, "night_note", "未入力")}

【1つ前】(created_at: {_get_value(previous, "created_at", "データなし")})
- 朝の気分: {_get_value(previous, "morning_mood", "データなし")}
- 朝の体調: {_get_value(previous, "morning_condition", "データなし")}
- 朝のメモ: {_get_value(previous, "morning_note", "データなし")}
- 夜の気分: {_get_value(previous, "night_mood", "データなし")}
- 夜の体調: {_get_value(previous, "night_condition", "データなし")}
- 夜のメモ: {_get_value(previous, "night_note", "データなし")}

【重要】マスコットのstatusは、最新2件のうち両方で気分が「つらい」になっている場合のみ「Bad」または「Sad」にしてください。
1件だけ「つらい」の場合は、急に「Bad」「Sad」にしないでください。

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
def get_mascot_state(user_uuid: str) -> dict[str, Any] | None:
    """
    Supabase の mascots テーブルから
    指定ユーザーの status, message, image_urls を取得
    """
    client = get_supabase_client()

    result = (
        client.table("mascots")
        .select("status, message, image_urls")
        .eq("uuid", user_uuid)
        .limit(1)
        .execute()
    )

    if result.data and len(result.data) > 0:
        return {
            "status": result.data[0]["status"],
            "message": result.data[0]["message"],
            "image_urls": result.data[0].get("image_urls") or {},
        }

    return None
