#https://pypi.python.org/pypi/line-bot-sdk/1.3.0
#pip install line-bot-sdk -t .
#compress all files to tar.gz
#upload to lambda

from linebot import LineBotApi
from linebot.models import TextSendMessage
from linebot.exceptions import LineBotApiError
from linebot.models.responses import MessageContent
import json

reply_url = "https://api.line.me/v2/bot/message/reply"
push_url = "https://api.line.me/v2/bot/message/push"
channelaccesstoken="dummy"
userid = "dummy"

def reply_msg(replytoken,text):
    line_bot_api = LineBotApi(channelaccesstoken)
    try:
        line_bot_api.reply_message(replytoken, TextSendMessage(text))
    except LineBotApiError as e:
        print(e)

def push_msg(userid,text):
    line_bot_api = LineBotApi(channelaccesstoken)
    try:
        line_bot_api.push_message(userid, TextSendMessage(text))
    except LineBotApiError as e:
        print(e)

def get_image(imageid):
    line_bot_api = LineBotApi(channelaccesstoken)
    return line_bot_api.get_message_content(imageid)


def lambda_handler(event, context):
    # event is json type
    print('EVENT DUMPS :' + json.dumps(event, sort_keys=True, indent=4))
    # event["body"] is string
    # json.loads(event["body"]) is dictional type
    # json.loads(event["body"])["events"] is list type
    # json.loads(event["body"])["events"][0] is dict type
    replytoken = json.loads(event["body"])["events"][0]["replyToken"]

    # process of each event type
    messagetype = json.loads(event["body"])["events"][0]["message"]["type"]
    if messagetype == 'text':
        receivedmessage = json.loads(event["body"])["events"][0]["message"]["text"]
        print('Received Message:' + receivedmessage)
        reply_msg(replytoken,receivedmessage)

    elif messagetype == 'image':
        imageid = json.loads(event["body"])["events"][0]["message"]["id"]
        img = get_image(imageid)
        img.content
        reply_msg(replytoken,"imageid:" + str(imageid))

