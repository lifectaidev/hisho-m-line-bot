import json
from anthropic import Anthropic
from dotenv import load_dotenv
import os
from digital_twin_service import get_digital_twin

load_dotenv()

claude = Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))


def generate_growth_report() -> dict:
    """デジタルツインの現在データからClaudeで成長レポートを生成して返す。"""
    twin = get_digital_twin()
    twin_json = json.dumps(twin, ensure_ascii=False, indent=2)

    prompt = f"""以下は昇悟さんのデジタルツインデータです。このデータをもとに、以下3つのサマリーを生成してください。

各サマリーは簡潔・具体的に、箇条書きで2〜3点まとめてください。
JSONのみ返してください。キーは growth_this_week / current_state / next_week_suggestions の3つです。

デジタルツインデータ：
{twin_json}

出力形式（例）：
{{
  "growth_this_week": "今週の成長・変化（ポートフォリオ進捗・感情状態・優先事項の変化などを根拠に具体的に）",
  "current_state": "デジタルツインの現在状態（今の仕事・目標・感情状態・障壁を端的に）",
  "next_week_suggestions": "来週の優先提案（目標・obstacles・prioritiesをもとに具体的なアクション3点）"
}}"""

    response = claude.messages.create(
        model="claude-sonnet-4-6",
        max_tokens=800,
        messages=[{"role": "user", "content": prompt}]
    )

    raw = response.content[0].text.strip().replace("```json", "").replace("```", "").strip()
    report = json.loads(raw)

    for key in ("growth_this_week", "current_state", "next_week_suggestions"):
        if isinstance(report.get(key), list):
            report[key] = "\n・".join(report[key])

    return report
