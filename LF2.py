import json
import argparse
import pprint
from botocore.vendored import requests
import urllib
import sys
import datetime
import boto3
import requests
from requests_aws4auth import AWS4Auth

from boto3.dynamodb.conditions import Key, Attr
from ast import literal_eval

def retrieve_from_dynamodb(ids):
    """
    Given a list of ids, retrieve the restuarant information of those ids
    """
    resource = boto3.resource('dynamodb')
    table = resource.Table("yelp-restaurants")
    restuarnt_information = []
    for business in ids:
        responseData = table.query(KeyConditionExpression=Key('Business_ID').eq(business))
        restuarnt_information.append(responseData)
    return restuarnt_information



def get_restaurant_ids(lst):
    """
    return the restaurant ids having the 
    same cuisine as desired 
    """
    data = json.loads(lst)
    hits = data["hits"]["hits"]
    id_list = []
    for result in hits:
        _id = result["_source"]["RestaurantID"]
        id_list.append(_id)
    return id_list


def get_message(restaurant_information):
    message = ''
    i = 1
    for info in restaurant_information[:2]:
        data = info["Items"][0]
        ad = data["Address"]
        n = data["Name"]
        message += "{}.{} located at {}\n".format(i, n, ad)
        i += 1
    return message




def send_sns_message(message, client, phone_number):
    """
    sends a message to a phone number
    message: string
    client: boto3 client for sns
    phone_number: should be E.164 format as shown in default
    """
    if not phone_number.startswith('+'):
        phone_number = '+1'+phone_number
    client.publish(Message=message, PhoneNumber=phone_number)
    
    
    
    
def lambda_handler(event, context):
    # TODO implement
    sqs = boto3.client('sqs')
    sqs_url = 'https://sqs.us-west-2.amazonaws.com/786236946359/chatbox-message'
    

    data = event['Records'][0]['messageAttributes'];
    receipt_handle = event['Records'][0]['receiptHandle'];
    location = data['location']['stringValue']
    party_people = data['NumberPeople']['stringValue']
    cuisine = data['cuisine']['stringValue']
    timestamp = data['time']['stringValue']
    phone_number = data['PhoneNumber']['stringValue']
    Dining_Date = data['date']['stringValue']
    
    
    headers = { "Content-Type": "application/json" }
    url = 'https://search-restaurants-ztv76gvwrmqfszdm56bl6hkkqa.us-west-2.es.amazonaws.com/restaurants/_search?q=' + cuisine
    r = requests.get(url, auth=("jiayuanguo", "201006004@aAa"), headers=headers).content
    
    #collect restaurant ID
    restaurant_id = get_restaurant_ids(r)
    
    #restaurant information list
    restaurant_info = retrieve_from_dynamodb(restaurant_id)
    
    #get message
    message = f'Hello! Here are my {cuisine} restaurant suggestions for {party_people} at {Dining_Date} {timestamp} \n'
    message += get_message(restaurant_info)
    
    print("sending the message is:",message)
    
    client = boto3.client('sns')
    #send_sns_message(message, client, phone_number)
    return {
        'statusCode': 200,
        'body': json.dumps('Hello from Lambda!')
        }