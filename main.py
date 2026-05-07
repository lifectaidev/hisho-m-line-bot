import os
from fastapi import FastAPI, Request, HTTPException
from anthropic import Anthropic
from linebot import LineBotApi, WebhookHandler
from linebot.exceptions import InvalidSignatureError
from linebot.models import MessageEvent, TextMessage, TextSendMessage
from dotenv import load_dotenv

load_dotenv()

app = FastAPI()
claude = Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))
line_bot_api = LineBotApi(os.getenv("LINE_CHANNEL_ACCESS_TOKEN"))
handler = WebhookHandler(os.getenv("LINE_CHANNEL_SECRET"))

@app.get("/")
def read_root():
    return {"status": "秘書M稼働中"}

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
    
    response = claude.messages.create(
        model="claude-sonnet-4-6",
        max_tokens=1000,
        system="あなたは昇悟さん専用の秘書Mです。簡潔に、具体的に答えてください。",
        messages=[{"role": "user", "content": user_message}]
    )
    
    reply_text = response.content[0].text
    
    line_bot_api.reply_message(
        event.reply_token,
        TextSendMessage(text=reply_text)
    )