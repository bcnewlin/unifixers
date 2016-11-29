#lambda-s3-to-http.py
from __future__ import print_function

import json
import urllib
import boto3
import urllib2
import os

print('Loading function')

s3 = boto3.client('s3')


def lambda_handler(event, context):
    #print("Received event: " + json.dumps(event, indent=2))

    try:
        # Get the object from the event and show its content type
        bucket = event['Records'][0]['s3']['bucket']['name']
        key = urllib.unquote_plus(event['Records'][0]['s3']['object']['key'].encode('utf8'))
        print("BUCKET: " + bucket)
        print("KEY: " + key)
        response = s3.get_object(Bucket=bucket, Key=key)
        print("CONTENT TYPE: " + response['ContentType'])
        message_data = response['Body'].read()
        print("data: " + message_data)
        url = os.environ['endpoint']
        # print("ENDPOINT: " + os.environ['endpoint'])
        
        try:
            req = urllib2.Request(url, data=message_data)
            resp = urllib2.urlopen(req)
            resp.close()
            return message_data

        except urllib2.HTTPError as e:
            print(e.code)
            print(e.read())
            return "ERROR"

        
    except Exception as e:
        print(e)
        print('Error getting object {} from bucket {}. Make sure they exist and your bucket is in the same region as this function.'.format(key, bucket))
        raise e
