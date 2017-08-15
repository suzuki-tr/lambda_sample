#https://pypi.python.org/pypi/line-bot-sdk/1.3.0
#pip install line-bot-sdk -t .
#pip install pillow -t . #PIL

# import library
from linebot import LineBotApi
from linebot.models import TextSendMessage,ImageSendMessage
from linebot.exceptions import LineBotApiError
from linebot.models.responses import MessageContent
import boto3
import json
import io
import PIL.Image as Image

# static params
channelaccesstoken="dummy"
s3_client = boto3.client('s3')
s3_resource = boto3.resource('s3')
rekognition = boto3.client('rekognition')


##################
# Methods with line-bot-sdk
def reply_txtmsg(replytoken,text):
    line_bot_api = LineBotApi(channelaccesstoken)
    try:
        line_bot_api.reply_message(replytoken, TextSendMessage(text))
    except LineBotApiError as e:
        print(e)

def reply_imgmsg(replytoken,imgurl):
    line_bot_api = LineBotApi(channelaccesstoken)
    try:
        line_bot_api.reply_message(replytoken, ImageSendMessage(imgurl,imgurl))
    except LineBotApiError as e:
        print(e)

def push_txtmsg(userid,text):
    line_bot_api = LineBotApi(channelaccesstoken)
    try:
        line_bot_api.push_message(userid, TextSendMessage(text))
    except LineBotApiError as e:
        print(e)

def push_imgmsg(userid,imgurl):
    line_bot_api = LineBotApi(channelaccesstoken)
    try:
        line_bot_api.push_message(userid, ImageSendMessage(imgurl,imgurl))
    except LineBotApiError as e:
        print(e)

def get_image_content(imageid):
    line_bot_api = LineBotApi(channelaccesstoken)
    message_content = line_bot_api.get_message_content(imageid)
    return message_content.content

def save_image(imageid,path):
    line_bot_api = LineBotApi(channelaccesstoken)
    message_content = line_bot_api.get_message_content(imageid)
    print ('message_content:{}'.format(type(message_content)))
    with open(path, mode='wb') as fd:
        for chunk in message_content.iter_content():
            fd.write(chunk)


#######################
# Methods with AWS S3
def save_fileobj_s3(data,bucket,key):
    targetbucket = s3_resource.Bucket(bucket)
    targetobj = targetbucket.Object(key)
    targetobj.upload_fileobj(data)

def save_file_s3(datafile,bucket,key):
    targetbucket = s3_resource.Bucket(bucket)
    targetobj = targetbucket.Object(key)
    targetobj.upload_fileobj(datafile)

# get presigned url of s3 object
def get_presigned_url(bucket,key):
    url = s3_client.generate_presigned_url(
        ClientMethod='get_object',
        Params={
            'Bucket': bucket,
            'Key': key
        }
    )
    return url

#################################
# Methods with AWS Rekognition
def detect_labels(bucket, key):
    response = rekognition.detect_labels(Image={"S3Object": {"Bucket": bucket, "Name": key}})
    return response

##################
# Methods with PIL
def resize_image(image_path, resized_path):
    print ('{}\n{}'.format(image_path, resized_path))
    with Image.open(image_path) as image:
        width = 320 #static
        height = 320*image.size[1]/image.size[0]
        image.thumbnail((width,height))
        image.save(resized_path, format='JPEG')

def lambda_handler(event, context):
    print('start of lambda_handler')

    # 'event' is json object
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
        # reply message copy of received
        reply_txtmsg(replytoken,receivedmessage)

    elif messagetype == 'image':
        print('Received Message:' + str(json.loads(event["body"])["events"][0]["message"]))

        #1). get image id
        imageid = json.loads(event["body"])["events"][0]["message"]["id"]

        #2). get image content
        data = get_image_content(imageid) #binary data <type 'str'>
        datastream = io.BytesIO(data)

        #3). create thumnail
        outputbuf = io.BytesIO()
        resize_image(datastream, outputbuf)

        #4). save to s3
        bucket = 'uswestbucket-suzuki'
        key = 's3test/' + imageid + '.jpg'
        outputbuf.seek(0)
        save_file_s3(outputbuf,bucket,key)

        #5). get Rekognition result
        detect_result = detect_labels(bucket, key)
	print (detect_result)
        results = detect_result["Labels"]
        msg = "{}:{}\n{}:{}\n{}:{}".format(results[0]["Name"],results[0]["Confidence"],results[1]["Name"],results[1]["Confidence"],results[2]["Name"],results[2]["Confidence"])
        if msg == "":
            msg = "no result"

        reply_txtmsg(replytoken,msg)

        '''
        #6). reply line message
        imgurl = get_presigned_url(bucket,key)
        print (imgurl)
        reply_imgmsg(replytoken, imgurl)
        '''

    print('end of lambda_handler')
