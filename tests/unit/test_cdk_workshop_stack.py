"""
Tests the creation of AWS CDK services.
"""
import aws_cdk as core
import aws_cdk.assertions as assertions
from aws_cdk import aws_lambda as _lambda
from aws_cdk import Stack

from cdk_workshop.cdk_workshop_stack import CdkWorkshopStack
from cdk_workshop.hitcounter import HitCounter


# SECTION: TESTS ============================================================ #


def test_dynamodb_table_created():
    """
    Tests if a synthesized AWS CDK stack includes an AWS DynamoDB table.
    """
    stack = Stack()

    HitCounter(
        stack, 'HitCounter',
        downstream=_lambda.Function(
            stack, 'TestFunction',
            runtime=_lambda.Runtime.PYTHON_3_7,
            handler='hello.handler',
            code=_lambda.Code.from_asset('lambda'),
        ),
    )

    template = assertions.Template.from_stack(stack)
    template.resource_count_is('AWS::DynamoDB::Table', 1)


def test_dynamodb_with_encryption():
    """
    Tests if an encrypted AWS DynamoDB table is encrypted.
    """
    stack = Stack()

    HitCounter(
        stack, 'HitCounter',
        downstream=_lambda.Function(
            stack, 'TestFunction',
            runtime=_lambda.Runtime.PYTHON_3_7,
            handler='hello.handler',
            code=_lambda.Code.from_asset('lambda'),
        ),
    )

    template = assertions.Template.from_stack(stack)
    template.has_resource_properties(
        'AWS::DynamoDB::Table', {
            'SSESpecification': {
                'SSEEnabled': True,
            },
        },
    )


def test_lambda_has_env_vars():
    """
    Tests if AWS Lambda function has 2 environment variables defined:
    1. DOWNSTREAM_FUNCTION_NAME
    2. HITS_TABLE_NAME
    """
    stack = Stack()

    HitCounter(
        stack, 'HitCounter',
        downstream=_lambda.Function(
            stack, 'TestFunction',
            runtime=_lambda.Runtime.PYTHON_3_7,
            handler='hello.handler',
            code=_lambda.Code.from_asset('lambda'),
        ),
    )

    template = assertions.Template.from_stack(stack)
    env_capture = assertions.Capture()

    template.has_resource_properties(
        'AWS::Lambda::Function',
        {
            'Handler': 'hitcount.handler',
            'Environment': env_capture,
        },
    )

    # TODO: Replace strings 'TestFunctionXXXXX' & 'HitCounterHitsXXXXXX'.
    assert env_capture.as_object() == {
        'Variables': {
            'DOWNSTREAM_FUNCTION_NAME': {'Ref': 'TestFunctionXXXXX'},
            'HITS_TABLE_NAME': {'Ref': 'HitCounterHitsXXXXXX'},
        },
    }


def test_sqs_queue_created():
    """
    Tests creating an AWS SQS queue.
    """

    app = core.App()
    stack = CdkWorkshopStack(app, 'cdk-workshop')
    template = assertions.Template.from_stack(stack)

    template.has_resource_properties(
        'AWS::SQS::Queue',
        {
            'VisibilityTimeout': 300,
        },
    )


def test_sns_topic_created():
    """
    Tests creating an AWS SNS topic.
    """

    app = core.App()
    stack = CdkWorkshopStack(app, 'cdk-workshop')
    template = assertions.Template.from_stack(stack)

    template.resource_count_is('AWS::SNS::Topic', 1)
