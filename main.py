import os
from fastapi import FastAPI, Request, HTTPException
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from anthropic import Anthropic
from linebot import LineBotApi, WebhookHandler
from linebot.exceptions import InvalidSignatureError
from linebot.models import MessageEvent, TextMessage, TextSendMessage
from dotenv import load_dotenv
from gmail import get_unread_emails, create_reply_draft, send_reply, revise_draft
from calendar_service import get_today_events, get_tomorrow_events, add_event, update_event
from task_service import add_task, suggest_task, get_progress, complete_task
from conversation_service import save_message, get_recent_messages
from digital_twin_service import update_digital_twin, get_summary
from strategist_service import analyze_with_strategist
from apscheduler.schedulers.background import BackgroundScheduler
from datetime import datetime, timezone

load_dotenv()

app = FastAPI()
templates = Jinja2Templates(directory="templates")
claude = Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))
line_bot_api = LineBotApi(os.getenv("LINE_CHANNEL_ACCESS_TOKEN"))
handler = WebhookHandler(os.getenv("LINE_CHANNEL_SECRET"))

# APSchedulerの設定
scheduler = BackgroundScheduler()

def check_task_deadlines():
    """締切24時間以内のタスクをチェックしてLINEに通知する関数"""
    from supabase import create_client
    import os
    
    supabase = create_client(
        os.getenv("SUPABASE_URL"),
        os.getenv("SUPABASE_KEY")
    )
    
    result = supabase.table("tasks").select("*").in_(
        "status", ["未着手", "進行中"]
    ).execute()
    
    tasks = result.data
    now = datetime.now(timezone.utc)
    warning_tasks = []
    
    for task in tasks:
        if task.get("deadline"):
            deadline_str = task["deadline"]
            if "+" not in deadline_str and "Z" not in deadline_str:
                deadline = datetime.fromisoformat(deadline_str).replace(tzinfo=timezone.utc)
            else:
                deadline = datetime.fromisoformat(deadline_str.replace("Z", "+00:00"))
            diff = deadline - now
            if 0 < diff.total_seconds() < 86400:
                warning_tasks.append(task)
            elif diff.total_seconds() <= 0:
                # 締切を過ぎているタスクは「期限切れ」にする
                supabase.table("tasks").update({"status": "期限切れ"}).eq("id", task["id"]).execute()
    
    if warning_tasks:
        user_id = os.getenv("LINE_USER_ID")
        if user_id:
            lines = ["⚠️ 締切が近いタスクがあります！"]
            for task in warning_tasks:
                deadline_str = task["deadline"]
                if "+" not in deadline_str and "Z" not in deadline_str:
                    deadline = datetime.fromisoformat(deadline_str).replace(tzinfo=timezone.utc)
                else:
                    deadline = datetime.fromisoformat(deadline_str.replace("Z", "+00:00"))
                lines.append(f"・{task['title']}（締切：{deadline.strftime('%m/%d %H:%M')}）")
            
            line_bot_api.push_message(
                user_id,
                TextSendMessage(text="\n".join(lines))
            )

from briefing_service import send_morning_briefing
from growth_report_service import generate_growth_report


def send_weekly_growth_report():
    """毎週月曜朝8時に成長レポートをLINEに送信する関数"""
    user_id = os.getenv("LINE_USER_ID")
    if not user_id:
        print("LINE_USER_IDが設定されていません")
        return

    try:
        report = generate_growth_report()
        message = (
            "📊 週次成長レポート\n\n"
            f"🌱 今週の成長・変化\n{report.get('growth_this_week', '取得失敗')}\n\n"
            f"👤 現在状態\n{report.get('current_state', '取得失敗')}\n\n"
            f"🎯 来週の優先提案\n{report.get('next_week_suggestions', '取得失敗')}"
        )
        line_bot_api.push_message(user_id, TextSendMessage(text=message))
        print("週次成長レポート送信完了")
    except Exception as e:
        print(f"週次成長レポート送信失敗：{e}")


# 1時間ごとに締切チェックを実行
scheduler.add_job(check_task_deadlines, 'interval', hours=1)

# 毎朝7時にブリーフィングを送信（日本時間）
scheduler.add_job(send_morning_briefing, 'cron', hour=7, minute=0, timezone='Asia/Tokyo')

# 毎週月曜朝8時に成長レポートを送信（日本時間）
scheduler.add_job(send_weekly_growth_report, 'cron', day_of_week='mon', hour=8, minute=0, timezone='Asia/Tokyo')

scheduler.start()

@app.get("/")
def read_root():
    return {"status": "秘書M稼働中"}


@app.get("/dashboard", response_class=HTMLResponse)
async def dashboard(request: Request):
    return templates.TemplateResponse(request, "dashboard.html")


@app.get("/api/dashboard")
async def api_dashboard():
    from supabase import create_client

    supabase = create_client(
        os.getenv("SUPABASE_URL"),
        os.getenv("SUPABASE_KEY")
    )

    # 今日の予定
    try:
        events = get_today_events()
    except Exception:
        events = None

    # 未完了タスク
    try:
        tasks_result = supabase.table("tasks").select("*").in_(
            "status", ["未着手", "進行中"]
        ).execute()
        tasks = tasks_result.data
    except Exception:
        tasks = None

    # 未読メール
    try:
        emails = get_unread_emails()
    except Exception:
        emails = None

    # デジタルツイン
    try:
        digital_twin = get_summary()
    except Exception:
        digital_twin = None

    # ブリーフィング履歴（直近5件）
    try:
        briefing_result = supabase.table("briefing_logs").select("*").order(
            "created_at", desc=True
        ).limit(5).execute()
        briefing_history = briefing_result.data
    except Exception:
        briefing_history = None

    return {
        "events": events,
        "tasks": tasks,
        "emails": emails,
        "digital_twin": digital_twin,
        "briefing_history": briefing_history,
    }

@app.get("/api/growth-report")
async def api_growth_report():
    try:
        report = generate_growth_report()
        return report
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/webhook")
async def webhook(request: Request):
    signature = request.headers.get("X-Line-Signature", "")
    body = await request.body()
    
    try:
        handler.handle(body.decode("utf-8"), signature)
    except InvalidSignatureError:
        raise HTTPException(status_code=400, detail="Invalid signature")
    
    return "OK"

@handler.add(MessageEvent, message=TextMessage)
def handle_message(event):
    user_message = event.message.text
    user_id = event.source.user_id
    
    # キーワードで処理を振り分け
    if "メール確認" in user_message:
        try:
            reply_text = get_unread_emails()
        except Exception as e:
            reply_text = f"メール取得中にエラーが発生しました：{str(e)}"
    
    elif "返信して" in user_message:
        try:
            reply_text = create_reply_draft(user_id, user_message)
        except Exception as e:
            reply_text = f"下書き作成中にエラーが発生しました：{str(e)}"
    
    elif "送信して" in user_message:
        try:
            reply_text = send_reply(user_id)
        except Exception as e:
            reply_text = f"送信中にエラーが発生しました：{str(e)}"
    
    elif "修正して" in user_message:
        try:
            reply_text = revise_draft(user_id, user_message)
        except Exception as e:
            reply_text = f"修正中にエラーが発生しました：{str(e)}"
    elif "今日の予定" in user_message:
        try:
            reply_text = get_today_events()
        except Exception as e:
            reply_text = f"予定取得中にエラーが発生しました：{str(e)}"
    
    elif "明日の予定" in user_message:
        try:
            reply_text = get_tomorrow_events()
        except Exception as e:
            reply_text = f"予定取得中にエラーが発生しました：{str(e)}"
    
    elif "追加して" in user_message and ("時" in user_message or "予定" in user_message):
        try:
            reply_text = add_event(user_message)
        except Exception as e:
            reply_text = f"予定追加中にエラーが発生しました：{str(e)}"
    
    elif "変更して" in user_message and "時" in user_message:
        try:
            reply_text = update_event(user_message)
        except Exception as e:
            reply_text = f"予定変更中にエラーが発生しました：{str(e)}"

    elif "タスクに追加" in user_message or "タスク追加" in user_message:
        try:
            reply_text = add_task(user_message)
        except Exception as e:
            reply_text = f"タスク追加中にエラーが発生しました：{str(e)}"
    
    elif "何やる" in user_message or "タスク提案" in user_message:
        try:
            reply_text = suggest_task()
        except Exception as e:
            reply_text = f"タスク提案中にエラーが発生しました：{str(e)}"
    
    elif "進捗どう" in user_message or "進捗確認" in user_message:
        try:
            reply_text = get_progress()
        except Exception as e:
            reply_text = f"進捗確認中にエラーが発生しました：{str(e)}"
    
    elif "完了にして" in user_message or "タスク完了" in user_message:
        try:
            reply_text = complete_task(user_message)
        except Exception as e:
            reply_text = f"タスク完了中にエラーが発生しました：{str(e)}"

    elif "締切チェック" in user_message:
        try:
            check_task_deadlines()
            reply_text = "締切チェックを実行しました。"
        except Exception as e:
            reply_text = f"締切チェック中にエラーが発生しました：{str(e)}"

    elif "プロファイル確認" in user_message:
        try:
            reply_text = get_summary()
        except Exception as e:
            reply_text = f"プロファイル確認中にエラーが発生しました：{str(e)}"

    else:
        # 過去の会話履歴を取得
        history = get_recent_messages(limit=10)

        # 今のメッセージを履歴に追加
        history.append({"role": "user", "content": user_message})

        # 昇悟さんのメッセージを保存
        save_message("user", user_message)

        response = claude.messages.create(
            model="claude-sonnet-4-6",
            max_tokens=1000,
            system="あなたは昇悟さん専用の秘書Mです。簡潔に、具体的に答えてください。",
            messages=history
        )
        reply_text = response.content[0].text

        # 秘書Mの返答を保存
        save_message("assistant", reply_text)

        # LINEへ返答後、デジタルツインを更新
        line_bot_api.reply_message(
            event.reply_token,
            TextSendMessage(text=reply_text)
        )
        try:
            update_digital_twin(f"昇悟：{user_message}\n秘書M：{reply_text}")
        except Exception:
            pass

        try:
            comment = analyze_with_strategist(user_message, reply_text)
            if comment:
                user_id = os.getenv("LINE_USER_ID")
                if user_id:
                    line_bot_api.push_message(user_id, TextSendMessage(text=comment))
        except Exception:
            pass
        return

    line_bot_api.reply_message(
        event.reply_token,
        TextSendMessage(text=reply_text)
    )