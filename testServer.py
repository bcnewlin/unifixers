#!/usr/bin/env python
"""
Client which receives the requests

"""
from flask import Flask, request
import logging
import argparse
import json

APP = Flask(__name__)

# creating flask route for type argument
@APP.route('/abc123', methods=['POST'])
def main_handler():
    """
    main routing for requests
    """
    if request.method == 'POST':
        return process_message(request.get_json())

def process_message(msg):
    """
    processes the messages by combining and appending the kind code
    """

    print "Received message:"
    print json.dumps(msg)

    return 'OK'

if __name__ == "__main__":

    # By default, we disable threading for "debugging" purposes.
    # This will cause the app to block requests, which means that you miss out on some points,
    # and fail ALB healthchecks, but whatever I know I'm getting fired on Friday.
    # APP.run(host="0.0.0.0", port="80")

    # Use this to enable threading:
    APP.run(host="0.0.0.0", port="8080", threaded=True)
