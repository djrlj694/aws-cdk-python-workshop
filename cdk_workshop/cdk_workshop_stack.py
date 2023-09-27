"""
Defines a class (`CdkWorkshopStack`) modeling a custom AWS CDK stack for use in
the CDK application represented by this software project.
"""
# from aws_cdk import aws_iam as iam
from aws_cdk import aws_apigateway as apigw
from aws_cdk import aws_lambda as _lambda
from aws_cdk import aws_sns as sns
from aws_cdk import aws_sns_subscriptions as subs
from aws_cdk import aws_sqs as sqs
from aws_cdk import Duration
from aws_cdk import Stack
from constructs import Construct

from .hitcounter import HitCounter


# SECTION: CLASSES ========================================================== #


class CdkWorkshopStack(Stack):
    """
    A class modeling an AWS CDK stack.
    """

    def __init__(self, scope: Construct, construct_id: str, **kwargs) -> None:
        """
        The class constructor.

        Parameters
        ----------
        `scope` : `Construct`
            The stack's parent, usually an App or a Stage, but could be any
            construct.
        `construct_id` : `str`
            The stack's construct ID.
        """

        super().__init__(scope, construct_id, **kwargs)

        queue = sqs.Queue(
            self,
            'CdkWorkshopQueue',
            visibility_timeout=Duration.seconds(300),
        )

        topic = sns.Topic(
            self,
            'CdkWorkshopTopic',
        )

        topic.add_subscription(subs.SqsSubscription(queue))

        # Define AWS Lambda resource.
        my_lambda = _lambda.Function(
            self,
            'HelloHandler',
            runtime=_lambda.Runtime.PYTHON_3_7,
            code=_lambda.Code.from_asset('lambda'),
            handler='hello.handler',
        )

        # Instantiate REST API hit counter construct.
        hello_with_counter = HitCounter(
            self, 'HelloHitCounter',
            downstream=my_lambda,
        )

        # Add LambdaRestApi construct to AWS CDK stack.
        apigw.LambdaRestApi(
            self, 'Endpoint',
            handler=hello_with_counter.handler,
        )
