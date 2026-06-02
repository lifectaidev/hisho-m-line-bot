import os
import json
from datetime import date
from supabase import create_client
from anthropic import Anthropic
from dotenv import load_dotenv

load_dotenv()

supabase = create_client(
    os.getenv("SUPABASE_URL"),
    os.getenv("SUPABASE_KEY")
)
claude = Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))

INITIAL_TWIN = {
    "profile": {
        "name": "昇悟",
        "location": "名古屋",
        "updated_at": "2026-04-24"
    },
    "current_status": {
        "job": "福祉施設管理職",
        "portfolio_progress": "入居相談AI完成・秘書M開発中",
        "job_hunting": "転職活動準備中"
    },
    "goals": {
        "income": "年収840万以上",
        "work_style": "労働時間削減・独立",
        "career": "AIフリーランス・福祉×AI",
        "timeline": "12週間で秘書M完成"
    },
    "values": [
        "本質志向・表面的なものを嫌う",
        "消耗したくない",
        "実務に直結しないものに価値を感じない",
        "納得しないと動かない"
    ],
    "decision_patterns": [
        "浅い提案には即座に気づく",
        "白黒はっきりさせたい",
        "理想から逆算して考える",
        "まず2週間で動くものを作る"
    ],
    "strengths": [
        "福祉ドメイン知識",
        "問題意識の高さ",
        "本質を掴む力",
        "行動力・学習速度"
    ],
    "current_obstacles": [
        "ポートフォリオがまだ少ない",
        "収入の不安",
        "技術的な自信が途上"
    ],
    "priorities": {
        "this_week": [],
        "this_month": [],
        "top3": []
    },
    "emotional_state": {
        "energy": 0.8,
        "motivation": 0.9,
        "stress": 0.3,
        "last_updated": "2026-04-24"
    },
    "communication_preferences": {
        "style": "本質から入る・結論を先に",
        "dislikes": ["浅い肯定", "抽象論", "役に立たない長文"],
        "response_length": "短く・具体的に"
    }
}


def get_digital_twin() -> dict:
    """Supabaseからデジタルツインを取得。存在しない場合は初期値を挿入して返す。"""
    result = supabase.table("digital_twin").select("*").limit(1).execute()

    if result.data:
        return result.data[0]["data"]

    # 初回：初期値をSupabaseに保存
    supabase.table("digital_twin").insert({"data": INITIAL_TWIN}).execute()
    return INITIAL_TWIN


def update_digital_twin(conversation: str) -> str:
    """会話内容からデジタルツインの更新情報をClaudeで抽出し、Supabaseへ保存する。"""
    current = get_digital_twin()

    extraction_prompt = f"""以下の会話から、昇悟さんのデジタルツイン（人物モデル）を更新すべき情報を抽出してください。

更新が必要な場合のみ、変更するフィールドをJSON形式で返してください。
変更なし・または抽出できない場合は空のJSONオブジェクト {{}} を返してください。

更新できるフィールド：
- current_status.job / portfolio_progress / job_hunting
- goals.income / work_style / career / timeline
- values（リスト。追加する要素のみ）
- decision_patterns（リスト。追加する要素のみ）
- current_obstacles（リスト。追加する要素のみ）
- priorities.this_week / this_month / top3（リスト）
- emotional_state.energy / motivation / stress（0.0〜1.0の数値）

現在のデジタルツイン：
{json.dumps(current, ensure_ascii=False, indent=2)}

会話：
{conversation}

JSONのみ返答してください。"""

    response = claude.messages.create(
        model="claude-sonnet-4-6",
        max_tokens=500,
        messages=[{"role": "user", "content": extraction_prompt}]
    )

    raw = response.content[0].text.strip().replace("```json", "").replace("```", "").strip()
    updates = json.loads(raw)

    if not updates:
        return "デジタルツインの更新対象情報は見つかりませんでした。"

    updated = _merge(current, updates)
    updated["profile"]["updated_at"] = str(date.today())

    # Supabaseのレコードを更新（常に1レコード管理）
    result = supabase.table("digital_twin").select("id").limit(1).execute()
    record_id = result.data[0]["id"]
    supabase.table("digital_twin").update({"data": updated}).eq("id", record_id).execute()

    changed_keys = list(updates.keys())
    return f"デジタルツインを更新しました。\n更新フィールド：{', '.join(changed_keys)}"


def get_summary() -> str:
    """デジタルツインのサマリーを返す。"""
    twin = get_digital_twin()

    profile = twin.get("profile", {})
    status = twin.get("current_status", {})
    goals = twin.get("goals", {})
    emotion = twin.get("emotional_state", {})
    priorities = twin.get("priorities", {})

    top3 = priorities.get("top3", [])
    top3_str = "・" + "\n・".join(top3) if top3 else "未設定"

    energy = int(emotion.get("energy", 0) * 100)
    motivation = int(emotion.get("motivation", 0) * 100)
    stress = int(emotion.get("stress", 0) * 100)

    return (
        f"👤 {profile.get('name', '')}（{profile.get('location', '')}）\n"
        f"💼 {status.get('job', '')}\n"
        f"🎯 目標：{goals.get('career', '')}｜{goals.get('income', '')}\n"
        f"📅 タイムライン：{goals.get('timeline', '')}\n"
        f"🔝 優先TOP3：\n{top3_str}\n"
        f"⚡ エネルギー:{energy}% モチベ:{motivation}% ストレス:{stress}%\n"
        f"（更新日：{profile.get('updated_at', '')}）"
    )


def _merge(base: dict, updates: dict) -> dict:
    """辞書を再帰的にマージ。リストは追加、スカラーは上書き。"""
    result = base.copy()
    for key, value in updates.items():
        if key in result and isinstance(result[key], dict) and isinstance(value, dict):
            result[key] = _merge(result[key], value)
        elif key in result and isinstance(result[key], list) and isinstance(value, list):
            existing = result[key]
            for item in value:
                if item not in existing:
                    existing.append(item)
            result[key] = existing
        else:
            result[key] = value
    return result
