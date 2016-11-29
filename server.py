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
import boto
from boto.dynamodb2.table import Table
from boto.dynamodb2.fields import HashKey
from collections import OrderedDict

# logging.basicConfig(level=logging.DEBUG)

# parsing arguments
PARSER = argparse.ArgumentParser(description='Client message processor')
PARSER.add_argument('API_token', help="the individual API token given to your team")
PARSER.add_argument('API_base', help="the base URL for the game API")

ARGS = PARSER.parse_args()

# defining global vars
activeTable = Table('activeMessages') # A dictionary that contains message parts
completeTable = Table('completeMessages')
API_BASE = ARGS.API_base
# 'https://csm45mnow5.execute-api.us-west-2.amazonaws.com/dev'

APP = Flask(__name__)

# creating flask route for type argument
@APP.route('/', methods=['POST'])
def main_handler():
    """
    main routing for requests
    """

    return process_message(request.get_json())

def process_message(msg):
    """
    processes the messages by combining and appending the kind code
    """

    completed = completeTable.get_item(Id=msg['Id'])
    if completed:
        return 'OK'

    # Try to get the parts of the message from the MESSAGES dictionary.
    # If it's not there, create one that has None in both parts
    part = activeTable.get_item(Id=msg['Id'], partNumber=msg['PartNumber'])
    if part:
        return 'OK'

    activeTable.put_item(data=msg)

    # store this part of the message in the correct part of the list
    parts[part_number] = data

    results = activeTable.query_2(Id__eq=msg['Id'])
    if results:
        all_parts = list(results)
        if len(all_parts) == all_parts[0]['TotalParts']:
            send_message(msg['Id'], all_parts)

    return 'OK'

def send_message(msg_id, all_parts):

    orderedParts = OrderedDict(sorted(all_parts.items(), key=lambda t: t['PartNumber']))

    result = ''
    for part in orderedParts:
        result = "{}{}".format(data, part['Data'])
        part.delete()

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
    resp.close()
    print response

    completeTable.put_item(data={
        'Id': msg_id,
        'Data': result
        })

    return 'OK'

if __name__ == "__main__":

    # By default, we disable threading for "debugging" purposes.
    # This will cause the app to block requests, which means that you miss out on some points,
    # and fail ALB healthchecks, but whatever I know I'm getting fired on Friday.
    # APP.run(host="0.0.0.0", port="80")

    # Use this to enable threading:
    APP.run(host="0.0.0.0", port="5000", threaded=True)
