import boto3
import json
import os

TABLE_NAME = os.environ['TABLE_NAME']
ddb = boto3.client('dynamodb')


def onConnect(event, context):
    # TODO: send full list of connected clients here
    connectionId = event['requestContext']['connectionId']
    ddb.put_item(TableName=TABLE_NAME, Item={'connectionId':{'S':connectionId}})
    print('[INFO]: New client connected. Adding to database ' + connectionId)
    return {
        "statusCode": 200,
        "body": 'ok'
    }


def onDisconnect(event, context):
    connectionId = event['requestContext']['connectionId']
    ddb.delete_item(TableName=TABLE_NAME, Key={'connectionId':{'S':connectionId}})
    print('[INFO]: Client disconnected. Removing from database ' + connectionId)
    return {
        "statusCode": 200,
        "body": 'ok'
    }


def updateLocation(event, context):
    endpoint = 'https://' + event['requestContext']['domainName'] + '/' + event['requestContext']['stage']
    apigw = boto3.client('apigatewaymanagementapi', endpoint_url=endpoint)
    
    message = json.loads(event['body'])
    body = {
        'action': 'updateLocation',
        'playerId': message['playerId'],
        'lat': message['lat'],
        'lng': message['lng']
    }

    dynamodb = boto3.resource('dynamodb')
    table = dynamodb.Table(TABLE_NAME)
    response = table.scan()

    for client in response['Items']:
        print('[INFO]: Relaying message to client ' + client['connectionId'])
        response = apigw.post_to_connection(Data=json.dumps(body), ConnectionId=client['connectionId'])
        if (response['ResponseMetadata']['HTTPStatusCode'] == 401):
            print('[INFO]: Found stale client. Removing from database ' + client['connectionId'])
            ddb.delete_item(TableName=TABLE_NAME, Key={'connectionId':{'S':client['connectionId']}})

    return {
        "statusCode": 200,
        "body": json.dumps(body)
    }


