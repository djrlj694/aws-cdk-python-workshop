"""
Defines a class (`HitCounter`) modeling a REST API hit counter.
"""
from aws_cdk import aws_dynamodb as ddb
from aws_cdk import aws_lambda as _lambda
from aws_cdk import RemovalPolicy
from constructs import Construct


# SECTION: CLASSES ========================================================== #


class HitCounter(Construct):
    """
    A class modeling a REST API hit counter construct.
    """

    @property
    def handler(self):
        return self._handler

    @property
    def table(self):
        return self._table

    def __init__(
        self,
        scope: Construct,
        construct_id: str,
        downstream: _lambda.IFunction,
        read_capacity: int = 5,
        **kwargs,
    ) -> None:
        """
        The class constructor.

        Parameters
        ----------
        `scope` : `Construct`
            The stack's parent, usually an App or a Stage, but could be any
            construct.
        `construct_id` : `str`
            The stack's construct ID.
        `downstream` : `_lambda.IFunction`
            An AWS Lambda function.
        `read_capacity` : `int`, optional
            The AWS DynamoDB table's read capacity, by default 5.

        Raises
        ------
        ValueError
            The AWS DynamoDB table's read capacity is not within the allowed
            range.
        """
        if read_capacity < 5 or read_capacity > 20:
            raise ValueError(
                '"read_capacity" must be greater than 5 or less than 20',
            )

        super().__init__(scope, construct_id, **kwargs)

        # Instantiate AWS DynamoDB table.
        self._table = ddb.Table(
            self, 'Hits',
            partition_key={'name': 'path', 'type': ddb.AttributeType.STRING},
            encryption=ddb.TableEncryption.AWS_MANAGED,
            read_capacity=read_capacity,
            removal_policy=RemovalPolicy.DESTROY,
        )

        # Instantiate AWS Lambda function.
        self._handler = _lambda.Function(
            self, 'HitCountHandler',
            runtime=_lambda.Runtime.PYTHON_3_7,
            handler='hitcount.handler',
            code=_lambda.Code.from_asset('lambda'),
            environment={
                'DOWNSTREAM_FUNCTION_NAME': downstream.function_name,
                'HITS_TABLE_NAME': self._table.table_name,
            },
        )

        # Allow AWS Lambda function to read/write AWS DynamoDB table.
        self._table.grant_read_write_data(self._handler)

        # Allow hit counter to invoke downstream AWS Lambda function.
        downstream.grant_invoke(self._handler)
