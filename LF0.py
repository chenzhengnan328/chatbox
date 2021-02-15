import json
import boto3
def lambda_handler(event, context):
    # TODO implement
    client = boto3.client('lex-runtime')
    user_message = event['messages'][0]['unstructured']['text']
    backup = "please try again"
    
    if user_message is None:
        return {
            'statusCode': 200,
            'body': json.dumps(backup)
        }
    
    response = client.post_text(botName='RestaurantHelper',
                                botAlias='BETA',
                                userId="10",
                                inputText=user_message)

    response =  {   
        'headers': {
            'Access-Control-Allow-Headers': 'Content-Type',
            'Access-Control-Allow-Origin': '*',
            'Access-Control-Allow-Methods': 'OPTIONS,POST,GET'
        },
        'messages':[
            {
            'type': 'unstructured',
            'unstructured': {
               'text': response['message']
                },
            },
        ],
        
        'statusCode': 200,
        'body':"hello from lambda",
    }
    return response