"""
Defines a class (`HitCounter`) modeling a REST API hit counter.
"""
from aws_cdk import aws_dynamodb as ddb
from aws_cdk import aws_lambda as _lambda
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
        """
        super().__init__(scope, construct_id, **kwargs)

        # Instantiate AWS DynamoDB table.
        self._table = ddb.Table(
            self, 'Hits',
            partition_key={'name': 'path', 'type': ddb.AttributeType.STRING},
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
