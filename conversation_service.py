import os
from supabase import create_client
from dotenv import load_dotenv

load_dotenv()

# Supabaseクライアントの初期化
supabase = create_client(
    os.getenv("SUPABASE_URL"),
    os.getenv("SUPABASE_KEY")
)

def save_message(role: str, content: str):
    """会話をSupabaseに保存する"""
    try:
        supabase.table("conversations").insert({
            "role": role,
            "content": content,
        }).execute()
    except Exception as e:
        print(f"会話保存エラー: {e}")

def get_recent_messages(limit: int = 10) -> list:
    """直近の会話履歴を取得してClaudeに渡せる形式で返す"""
    try:
        result = supabase.table("conversations")\
            .select("role, content")\
            .order("timestamp", desc=True)\
            .limit(limit)\
            .execute()

        # 古い順に並び替えてから返す
        messages = result.data[::-1]
        return [{"role": m["role"], "content": m["content"]} for m in messages]

    except Exception as e:
        print(f"会話取得エラー: {e}")
        return []