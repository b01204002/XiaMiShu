from flask import Flask, request, abort, jsonify
from linebot import LineBotApi, WebhookHandler
from linebot.exceptions import InvalidSignatureError, LineBotApiError
from linebot.models import MessageEvent, TextSendMessage, TextMessage, FlexSendMessage
from variables import line_channel
from main import text_processor

LINE_CHANNEL_SECRET = line_channel.get('LINE_CHANNEL_SECRET')
LINE_CHANNEL_ACCESS_TOKEN = line_channel.get('LINE_CHANNEL_ACCESS_TOKEN')
LINE_USER_ID = line_channel.get('LINE_USER_ID')

app = Flask(__name__)
line_bot_api = LineBotApi(LINE_CHANNEL_ACCESS_TOKEN)
handler = WebhookHandler(LINE_CHANNEL_SECRET)


# 接收 LINE 的資訊
@app.route("/callback", methods=['POST'])
def callback():
    signature = request.headers['X-Line-Signature']
    body = request.get_data(as_text=True)
    try:
        handler.handle(body, signature)

    except InvalidSignatureError as e:
        abort(400)

    return 'OK'


@handler.add(MessageEvent, message=TextMessage)
def handle(event):
    user_id = event.source.user_id
    text = event.message.text
    r_type, r_content = text_processor(user_id, text)
    if r_type == 'text':
        line_bot_api.reply_message(
            event.reply_token,
            TextSendMessage(text=r_content)
        )
    else:
        pass


if __name__ == "__main__":
    app.run()