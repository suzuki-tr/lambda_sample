import json
from decimal import Decimal
import requests
import urllib
import boto3

s3 = boto3.client('s3')
rekognition = boto3.client('rekognition')

LINE_NOTIFY_TOKEN = 'dummy'
#https://notify-bot.line.me/ja
# select user or group to add linenotify.

def send_line_message(message,LINE_NOTIFY_TOKEN):
    LINE_NOTIFY_URL = 'https://notify-api.line.me/api/notify'
    headers = { 'Authorization' : 'Bearer %s' % LINE_NOTIFY_TOKEN }
    payload = {"message" :  message}
    r = requests.post(LINE_NOTIFY_URL ,headers = headers ,params=payload)

def send_line_image(message,image_binary,LINE_NOTIFY_TOKEN):
    LINE_NOTIFY_URL = 'https://notify-api.line.me/api/notify'
    headers = { 'Authorization' : 'Bearer %s' % LINE_NOTIFY_TOKEN }
    payload = {"message" :  message}
    files = {"imageFile": image_binary} #JPEG
    r = requests.post(LINE_NOTIFY_URL ,headers = headers ,params=payload, files=files)

def check_s3object(bucket, key):
    response = s3.get_object(Bucket=bucket, Key=key)
    return str(response)

def detect_faces(bucket, key):
    response = rekognition.detect_faces(Image={"S3Object": {"Bucket": bucket, "Name": key}})
    return response

def detect_labels(bucket, key):
    response = rekognition.detect_labels(Image={"S3Object": {"Bucket": bucket, "Name": key}})
    return response


def lambda_handler(event, context):
    #print("Received event: " + json.dumps(event, indent=2))

    # Get the object from the event and show its content type
    bucket = event['Records'][0]['s3']['bucket']['name']
    key = urllib.unquote_plus(event['Records'][0]['s3']['object']['key'].encode('utf8'))
    try:
        response = s3.get_object(Bucket=bucket, Key=key)
        print("CONTENT TYPE: " + response['ContentType'])

        detect_result = detect_labels(bucket, key)
	print (detect_result)
    	#send_line_image(detect_result["Labels"][0]["Name"],response['Body'],LINE_NOTIFY_TOKEN)
        return detect_result["Labels"][0]["Name"]
    except Exception as e:
        print(e)
        print('Error getting object {} from bucket {}. Make sure they exist and your bucket is in the same region as this function.'.format(key, bucket))
        raise e
