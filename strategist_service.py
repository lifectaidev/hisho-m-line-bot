import os
from anthropic import Anthropic
from dotenv import load_dotenv
from digital_twin_service import get_digital_twin

load_dotenv()

claude = Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))


def analyze_with_strategist(user_message: str, reply_text: str) -> str | None:
    """デジタルツインを参照して警告・先読みコメントを返す。不要な場合はNone。"""
    twin = get_digital_twin()

    values = "\n".join(f"・{v}" for v in twin.get("values", []))
    decision_patterns = "\n".join(f"・{d}" for d in twin.get("decision_patterns", []))
    goals = twin.get("goals", {})
    obstacles = "\n".join(f"・{o}" for o in twin.get("current_obstacles", []))

    prompt = f"""あなたは昇悟さん専用の参謀AIです。
以下のプロファイルを参照して、今の会話に対して警告・先読みコメントが必要か判断してください。

【価値観】
{values}

【判断パターン】
{decision_patterns}

【目標】
年収：{goals.get('income', '')}
キャリア：{goals.get('career', '')}
タイムライン：{goals.get('timeline', '')}

【現在の障害】
{obstacles}

【今の会話】
昇悟：{user_message}
秘書M：{reply_text}

【判断基準】
- 昇悟さんの価値観・目標と矛盾しそうな方向性なら警告する
- このペースや方針だとリスクがあると読めるなら先読みコメントを出す
- 問題なければ何も返さない

【出力形式】
コメントが必要：「⚡参謀より：（1〜2文のコメント）」
不要：「NONE」とだけ返す"""

    response = claude.messages.create(
        model="claude-sonnet-4-6",
        max_tokens=200,
        messages=[{"role": "user", "content": prompt}]
    )

    result = response.content[0].text.strip()
    return None if result == "NONE" else result
