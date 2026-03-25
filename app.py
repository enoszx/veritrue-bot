
import os
import json
from flask import Flask, request, abort
from linebot import LineBotApi, WebhookHandler
from linebot.exceptions import InvalidSignatureError
from linebot.models import (
    MessageEvent, TextMessage, TextSendMessage,
    QuickReply, QuickReplyButton, MessageAction,
    FollowEvent, URIAction, TemplateSendMessage, ButtonsTemplate
)

LINE_TOKEN = os.environ.get("LINE_TOKEN")
LINE_SECRET = os.environ.get("LINE_SECRET")

line_bot_api = LineBotApi(LINE_TOKEN)
handler = WebhookHandler(LINE_SECRET)
app = Flask(__name__)

with open("data.json", "r", encoding="utf-8") as f:
    car_data = json.load(f)

@app.route("/callback", methods=["POST"])
def callback():
    signature = request.headers["X-Line-Signature"]
    body = request.get_data(as_text=True)
    try:
        handler.handle(body, signature)
    except InvalidSignatureError:
        abort(400)
    return "OK"

@handler.add(FollowEvent)
def handle_follow(event):
    LIFF_URL = "https://liff.line.me/2009606359-Iq3VfpYG"
    line_bot_api.reply_message(
        event.reply_token,
        TemplateSendMessage(
            alt_text="開始查詢",
            template=ButtonsTemplate(
                title="Veritrue 篩選器",
                text="選擇條件，找到真正可信的業者",
                actions=[URIAction(label="開始篩選", uri=LIFF_URL)]
            )
        )
    )

@handler.add(MessageEvent, message=TextMessage)
def handle_message(event):
    text = event.message.text.strip()
    LIFF_URL = "https://liff.line.me/2009606359-Iq3VfpYG"

    if text.startswith("查詢:"):
        parts = text.split(":")
        category = parts[1]
        location = parts[2]
        conditions = parts[3] if len(parts) > 3 else ""
        top3 = sorted(car_data["results"], key=lambda x: x["trust_score"], reverse=True)[:3]
        reply = f"Veritrue {location}{category}推薦\n"
        if conditions:
            reply += f"篩選條件：{conditions}\n"
        reply += "\n"
        for i, r in enumerate(top3, 1):
            reply += f"#{i} {r['name']}\n"
            reply += f"評分：{r['rating']} ({r['review_count']}則評論)\n"
            reply += f"可信度：{r['trust_score']}分\n"
            reply += f"地址：{r['address']}\n\n"
        line_bot_api.reply_message(event.reply_token, TextSendMessage(text=reply))
    else:
        line_bot_api.reply_message(
            event.reply_token,
            TemplateSendMessage(
                alt_text="開始查詢",
                template=ButtonsTemplate(
                    title="Veritrue 篩選器",
                    text="選擇條件，找到真正可信的業者",
                    actions=[URIAction(label="開始篩選", uri=LIFF_URL)]
                )
            )
        )

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
