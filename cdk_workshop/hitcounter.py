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

        table = ddb.Table(
            self, 'Hits',
            partition_key={'name': 'path', 'type': ddb.AttributeType.STRING},
        )

        self._handler = _lambda.Function(
            self, 'HitCountHandler',
            runtime=_lambda.Runtime.PYTHON_3_7,
            handler='hitcount.handler',
            code=_lambda.Code.from_asset('lambda'),
            environment={
                'DOWNSTREAM_FUNCTION_NAME': downstream.function_name,
                'HITS_TABLE_NAME': table.table_name,
            },
        )
