import json
import math
import dateutil.parser
import datetime
import time
import os
import logging

logger = logging.getLogger()
logger.setLevel(logging.DEBUG)


def greeting(intent_request):
    response = {
        'dialogAction': {
            'type': 'Close',
            'fulfillmentState':'Fulfilled',
            'message': {'contentType': 'PlainText',
                        'content':'Hi there, how can I help?'}
        }
    }
    return response
    

def dispatch(intent_request):
    intent_name = intent_request['currentIntent']['name']
    if intent_name == "GreetingIntent":
        return greeting(intent_request)

def lambda_handler(event, context):
    """
    Route the incoming request based on intent.
    The JSON body of the request is provided in the event slot.
    """
    # By default, treat the user request as coming from the America/New_York time zone.
    os.environ['TZ'] = 'America/New_York'
    time.tzset()
    #logger.debug('event.bot.name={}'.format(event['bot']['name']))

    return dispatch(event)