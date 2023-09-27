"""
Defines a function (`handler`) to return a REST API endpoint's HTTP status code
and HTTP headers.
"""
import json


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

    user = event['requestContext']['identity']['user']
    path = event['path']

    return {
        'statusCode': 200,
        'headers': {
            'Content-Type': 'text/plain',
        },
        'body': f'Hello, {user}! You have hit {path}\n',
    }
