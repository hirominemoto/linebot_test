from flask import Flask, request, abort
from linebot import LineBotApi, WebhookHandler
from linebot.exceptions import InvalidSignatureError
from linebot.models import MessageEvent, TextMessage, TextSendMessage

import os
import openai

app = Flask(__name__)

# LINE チャネル設定
line_bot_api = LineBotApi(os.environ["LINE_CHANNEL_ACCESS_TOKEN"])
handler = WebhookHandler(os.environ["LINE_CHANNEL_SECRET"])

# OpenAI API Key
openai.api_key = os.environ["OPENAI_API_KEY"]

@app.route("/callback", methods=['POST'])
def callback():
    signature = request.headers['X-Line-Signature']
    body = request.get_data(as_text=True)

    try:
        handler.handle(body, signature)
    except InvalidSignatureError:
        abort(400)

    return 'OK'

@handler.add(MessageEvent, message=TextMessage)
def handle_message(event):
    user_text = event.message.text

    # ChatGPT へリクエスト
    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=[
            {
                "role": "system",
                "content": (
                    "あなたは親しみやすく、明るく、相手に寄り添うキャラクターのひろみBotです。"
                    "友達に話しかけるように、やわらかい口調で返事をしてください。"
                    "必要であれば励ましたり、褒めたり、気遣いの言葉を入れてください。"
                    "でも砕けすぎず、節度のある言葉遣いでお願いします。"
                )
            },
            {
                "role": "user",
                "content": user_text
            }
        ]
    )
    bot_reply = response.choices[0].message.content.strip()

    line_bot_api.reply_message(
        event.reply_token,
        TextSendMessage(text=bot_reply))





