from linebot import LineBotApi, WebhookParser
from linebot.exceptions import InvalidSignatureError, LineBotApiError
from linebot.models import MessageEvent, TextSendMessage

line_bot_api = LineBotApi('TZU3KV2zYK+C3Se3SKx5sRLznbn96lTfipO0VexQ6+sQg8tQu1wO2kI8yvsVHaYXxXe1LNHq7X1w2UpWecLkUm9t+E9aswvywiNndB2pMRufUIoVOQczZFNcABIUnBHEKzS7AavP1eAZDjrxwF0algdB04t89/1O/w1cDnyilFU=')
parser = WebhookParser('7fe285a3ad113b8a7d3a59c8d60b70af')


@csrf_exempt
def callback(request):
    if request.method == 'POST':
        signature = request.META['HTTP_X_LINE_SIGNATURE']
        body = request.body.decode('utf-8')

        try:
            events = parser.parse(body, signature)  # 傳入的事件
        except InvalidSignatureError:
            return HttpResponseForbidden()
        except LineBotApiError:
            return HttpResponseBadRequest()

        for event in events:
            if isinstance(event, MessageEvent):  # 如果有訊息事件
                line_bot_api.reply_message(  # 回復傳入的訊息文字
                    event.reply_token,
                    TextSendMessage(text=event.message.text)
                )
        return HttpResponse()
    else:
        return HttpResponseBadRequest()