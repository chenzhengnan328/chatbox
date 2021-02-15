import json
import math
import dateutil.parser
import datetime
import time
import os
import logging
import boto3
from botocore.vendored import requests

logger = logging.getLogger()
logger.setLevel(logging.DEBUG)

def get_slots(intent_request):
    return intent_request['currentIntent']['slots']
    
def elicit_slot(session_attributes, intent_name, slots, slot_to_elicit, message):
    return {
        'sessionAttributes': session_attributes,
        'dialogAction': {
            'type': 'ElicitSlot',
            'intentName': intent_name,
            'slots': slots,
            'slotToElicit': slot_to_elicit,
            'message': message
        }
    }
    
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

def delegate(session_attributes, slots):
    return {
        'sessionAttributes': session_attributes,
        'dialogAction': {
            'type': 'Delegate',
            'slots': slots
        }
    } 
    
def close(session_attributes, fulfillment_state, message):
    response = {
        'sessionAttributes': session_attributes,
        'dialogAction': {
            'type': 'Close',
            'fulfillmentState': fulfillment_state,
            'message': message
        }
    }

    return response
    
def thank_you(intent_request):
    response = {
        'dialogAction': {
            'type': 'Close',
            'fulfillmentState':'Fulfilled',
            'message': {'contentType': 'PlainText',
                        'content':'Thanks for using us, hope you have a nice day!'}
        }
    }
    return response 
    
def build_validation_result(is_valid, violated_slot, message_content):
    if message_content is None:
        return {
            "isValid": is_valid,
            "violatedSlot": violated_slot,
        }

    return {
        'isValid': is_valid,
        'violatedSlot': violated_slot,
        'message': {'contentType': 'PlainText', 'content': message_content}
    }
"-------------------------------------------------------------------------------------------------"
def parse_int(n):
    try:
        return int(n)
    except ValueError:
        return float('nan')
        
def isvalid_date(date):
    try:
        dateutil.parser.parse(date)
        return True
    except ValueError:
        return False 

    
def validate_order(Number_of_people, date, time, Phone_Number, cuisine, location ):
    locations = ['brooklyn', 'new york', 'manhattan']

    if location is not None and location.lower() not in locations:
        
        return build_validation_result(False,
                                    'Location',
                                    'Please enter correct location, we currently offer new york, brooklyn, and manhattan')
                                    
    
    cuisines = ['korean', 'japanese','chinese', 'american', 'indian']
    if cuisine is not None and cuisine.lower() not in cuisines:
        return build_validation_result(False,
                                       'Food',
                                       'Please enter correct Cuisine, we offer korean, japanese, chinese, american, indian')
    
    if Number_of_people is not None: 
        if not Number_of_people.isdigit():
            return build_validation_result(False,
                                           'NumberofPeople',
                                           'The number is not valid, please try again.')
        
        if int(Number_of_people) > 10:
            return build_validation_result(False,
                                           'NumberofPeople',
                                           'Sorry, please enter a number smaller than 10.')
    
    if date is not None:
        if not isvalid_date(date):
            return build_validation_result(False,
                                           'DinningDate',
                                           'It is not a valid date, please try again.')
        elif datetime.datetime.strptime(date, '%Y-%m-%d').date() < datetime.date.today():
            return build_validation_result(False,
                                           'DinningDate',
                                           'It is not a valid date, please try again.')

    if time is not None:
        if len(time) != 5:
            return build_validation_result(False, 'DinningTime', 'Not valid time, Try Again.')

        hour, minute = time.split(':')
        hour = parse_int(hour)
        minute = parse_int(minute)
        if math.isnan(hour) or math.isnan(minute):
            return build_validation_result(False, 'DinningTime', 'Not valid time, Try Again.')

        if hour < 8 or hour > 21:
            return build_validation_result(False, 
                                          'DinningTime', 
                                          'Our business hours are from 8 a m. to 9 p m. Can you specify a time during this range?')
                                          
    if date is not None:
        if not isvalid_date(date):
            return build_validation_result(False, 'DinningDate', 'I did not understand that, what date would you like to add?')
    
    return build_validation_result(True, None, None)

def recommandation(intent_request):

    source = intent_request['invocationSource']
    Number_of_people = get_slots(intent_request)["NumberofPeople"]
    date = get_slots(intent_request)["DinningDate"]
    phonenumber = get_slots(intent_request)["PhoneNumber"]
    cuisine = get_slots(intent_request)["Food"]
    location = get_slots(intent_request)["Location"]
    time = get_slots(intent_request)["DinningTime"]
    

    if source == 'DialogCodeHook':
        # Perform basic validation on the supplied input slots.
        # Use the elicitSlot dialog action to re-prompt for the first violation detected.
        slots = get_slots(intent_request)

        validation_result = validate_order(Number_of_people, date, time, phonenumber, cuisine, location )
        if not validation_result['isValid']:
            slots[validation_result['violatedSlot']] = None
            return elicit_slot(intent_request['sessionAttributes'],
                            intent_request['currentIntent']['name'],
                            slots,
                            validation_result['violatedSlot'],
                            validation_result['message'])
                            
        output_session_attributes = intent_request['sessionAttributes'] if intent_request['sessionAttributes'] is not None else {}                    
        return delegate(output_session_attributes, get_slots(intent_request))
    
    "send SQS code ______________________________________________________________________________"
    
    sqs = boto3.client('sqs')
    queueurl = "https://sqs.us-west-2.amazonaws.com/786236946359/chatbox-message"
    messageattributes = {
            'location': {
                'DataType': 'String',
                'StringValue':location
            },
            'cuisine': {
                'DataType': 'String',
                'StringValue':cuisine
            },
            'date': {
                'DataType': 'String',
                'StringValue':date
            },
            'NumberPeople': {
                'DataType': 'String',
                'StringValue':Number_of_people
            },
            'time': {
                'DataType': 'String',
                'StringValue':time
            },
            'PhoneNumber': {
                'DataType': 'String',
                'StringValue':phonenumber
            }            
        }
 
    messagebody=("recommandation for restaurant")
    
    sqsresponse = sqs.send_message(
        QueueUrl = queueurl,
        DelaySeconds = 5,
        MessageAttributes = messageattributes,
        MessageBody = messagebody
        )
        
    print('message ID:', sqsresponse['MessageId'])
    
    return close(intent_request['sessionAttributes'],
                 'Fulfilled',
                 {'contentType': 'PlainText',
                  'content': 'Thanks, You will receive the recommendations on the provided phone number shortly'})
                  

    
def dispatch(intent_request):
    intent_name = intent_request['currentIntent']['name']
    if intent_name == "GreetingIntent":
        return greeting(intent_request)
    elif intent_name == "ThankYouIntent":
        return thank_you(intent_request)
    elif intent_name == "DiningSuggestionsIntent":
        return recommandation(intent_request)
        
    raise Exception('Intent with name ' + intent_name + ' not supported')
    
def lambda_handler(event, context):

    os.environ['TZ'] = 'America/New_York'
    time.tzset()


    return dispatch(event)