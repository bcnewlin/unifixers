#!/usr/bin/env python
"""
Client which receives the requests

Args:
    API Token
    API Base (https://...)

"""
from flask import Flask, request
import logging
import argparse
import urllib2
import boto3
from boto3.dynamodb.conditions import Key, Attr
import os

logging.basicConfig(level=logging.DEBUG)

# parsing arguments
PARSER = argparse.ArgumentParser(description='Client message processor')
PARSER.add_argument('API_token', help="the individual API token given to your team")
PARSER.add_argument('API_base', help="the base URL for the game API")

ARGS = PARSER.parse_args()

# defining global vars
dynamodb = boto3.resource('dynamodb', region_name='eu-central-1')
completeTable = dynamodb.Table('completeMessages')
activeTable = dynamodb.Table('activeMessages')
API_BASE = ARGS.API_base

APP = Flask(__name__)

# creating flask route for type argument
@APP.route('/', methods=['GET', 'POST'])
def main_handler():
    """
    main routing for requests
    """

    if request.method == 'POST':
        return process_message(request.get_json())
    else:
        return 'OK'

def process_message(msg):
    """
    processes the messages by combining and appending the kind code
    """

    try:
        result = completeTable.get_item(Key={
            'Id':msg['Id']
            })
        if 'Item' in result:
            print 'Message {} exists in completed'.format(msg['Id'])
            return 'OK'
    except:
        completeTable = dynamodb.create_table(
            TableName='completeMessages',
            KeySchema=[
                {
                    'AttributeName': 'Id',
                    'KeyType': 'HASH'
                }
            ],
            AttributeDefinitions=[
                {
                    'AttributeName': 'Id',
                    'AttributeType': 'S'
                },
                {
                    'AttributeName': 'Data',
                    'AttributeType': 'S'
                },
            ],
            ProvisionedThroughput={
                'ReadCapacityUnits': 5,
                'WriteCapacityUnits': 5
            }
        )


    # Try to get the parts of the message from the MESSAGES dictionary.
    # If it's not there, create one that has None in both parts
    try:
        result = activeTable.get_item(Key={
            'Id':msg['Id'],
            'PartNumber':msg['PartNumber']
            })
        if 'Item' not in result:
            print 'Message {} does not exist in active'.format(msg['Id'])
            activeTable.put_item(Item=msg)
    except:
        activeTable = dynamodb.create_table(
            TableName='activeMessages',
            KeySchema=[
                {
                    'AttributeName': 'Id',
                    'KeyType': 'HASH'
                },
                {
                    'AttributeName': 'PartNumber',
                    'KeyType': 'RANGE'
                },
            ],
            AttributeDefinitions=[
                {
                    'AttributeName': 'Id',
                    'AttributeType': 'S'
                },
                {
                    'AttributeName': 'PartNumber',
                    'AttributeType': 'N'
                },
                {
                    'AttributeName': 'TotalParts',
                    'AttributeType': 'N'
                },
                {
                    'AttributeName': 'Data',
                    'AttributeType': 's'
                }
            ],
            ProvisionedThroughput={
                'ReadCapacityUnits': 5,
                'WriteCapacityUnits': 5
            }
        )
        activeTable.put_item(Item=msg)

    results = activeTable.query(KeyConditionExpression=Key('Id').eq(msg['Id']))
    if results:
        all_parts = sorted(results['Items'], key=lambda t: t['PartNumber'])
        if len(all_parts) == all_parts[0]['TotalParts']:
            send_message(msg['Id'], all_parts)

    return 'OK'

def send_message(msg_id, all_parts):
    result = ''
    for part in all_parts:
        result = "{}{}".format(result, part['Data'])
        activeTable.delete_item(
            Key={
                'Id': part['Id'],
                'PartNumber': part['PartNumber']
            })

    # app.logger.debug("got a complete message for %s" % msg_id)
    print "all parts found"

    # sending the response to the score calculator
    # format:
    #   url -> api_base/jFgwN4GvTB1D2QiQsQ8GHwQUbbIJBS6r7ko9RVthXCJqAiobMsLRmsuwZRQTlOEW
    #   headers -> x-gameday-token = API_token
    #   data -> EaXA2G8cVTj1LGuRgv8ZhaGMLpJN2IKBwC5eYzAPNlJwkN4Qu1DIaI3H1zyUdf1H5NITR
    APP.logger.debug("ID: %s" % msg_id)
    APP.logger.debug("RESULT: %s" % result)
    url = API_BASE + '/' + msg_id
    print url
    print result
    req = urllib2.Request(url, data=result, headers={'x-gameday-token':ARGS.API_token})
    resp = urllib2.urlopen(req)
    print resp
    resp.close()

    completeTable.put_item(Item={
        'Id': msg_id,
        'Data': result
        })

    return 'OK'

if __name__ == "__main__":

    # By default, we disable threading for "debugging" purposes.
    # This will cause the app to block requests, which means that you miss out on some points,
    # and fail ALB healthchecks, but whatever I know I'm getting fired on Friday.
    # APP.run(host="0.0.0.0", port="80")

    print ""
    # Use this to enable threading:
    APP.run(host="0.0.0.0", port="80", threaded=True)
