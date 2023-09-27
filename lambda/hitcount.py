"""
Defines a function (`handler`) to serve as an AWS Lambda handler for a REST API
hit counter.

Lambda handler code for our hit counter
"""
import json
import os

import boto3


# SECTION: CONSTANTS ======================================================== #


DDB = boto3.resource('dynamodb')
TABLE = DDB.Table(os.environ['HITS_TABLE_NAME'])
LAMBDA = boto3.client('lambda')


# SECTION: FUNCTIONS ======================================================== #


def handler(event, context):
    """
    Returns a REST API endpoint's HTTP status code and HTTP headers.

    Parameters
    ----------
    `event` : `dict`
        A JSON-formatted document that contains data for a Lambda function to
        process.
    `context` : `Any`
        An object passed by AWS Lambda at runtime. Provide information about
        the invocation, function, and runtime environment.
    """

    print(f'request: {json.dumps(event)}')

    path = event['path']

    TABLE.update_item(
        Key={'path': path},
        UpdateExpression='ADD hits :incr',
        ExpressionAttributeValues={':incr': 1},
    )

    resp = LAMBDA.invoke(
        FunctionName=os.environ['DOWNSTREAM_FUNCTION_NAME'],
        Payload=json.dumps(event),
    )

    body = resp['Payload'].read()

    print(f'downstream response: {body}')

    return json.loads(body)
