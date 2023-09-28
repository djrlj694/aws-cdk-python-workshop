"""
Defines a class (`CdkWorkshopStack`) modeling a custom AWS CDK stack for
containing a Continuous Deployment (CD) pipeline, separate from the actual
“production” AWS CDK application represented by this software project
"""
from aws_cdk import aws_codecommit as codecommit
from aws_cdk import pipelines as pipelines
from aws_cdk import Stack
from constructs import Construct

from cdk_workshop.pipeline_stage import WorkshopPipelineStage


# SECTION: CLASSES ========================================================== #


class WorkshopPipelineStack(Stack):
    """
    A class modeling an AWS CDK pipeline stack.
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

        # Create AWS CodeCommit repository.
        repo = codecommit.Repository(
            self, 'WorkshopRepo',
            repository_name='WorkshopRepo',
        )

        # Initialize AWS CDK pipeline.
        pipeline = pipelines.CodePipeline(
            self, 'Pipeline',
            synth=pipelines.ShellStep(
                'Synth',
                input=pipelines.CodePipelineSource.code_commit(repo, 'main'),
                commands=[
                    'npm install -g aws-cdk',           # `cdk` CLI
                    'pip install -r requirements.txt',  # Python packages
                    'cdk synth',
                ],
            ),
        )

        # PIPELINE CODE HERE...

        deploy = WorkshopPipelineStage(self, 'Deploy')

        deploy_stage = pipeline.add_stage(deploy)
        deploy_stage.add_post(
            pipelines.ShellStep(
                'TestViewerEndpoint',
                env_from_cfn_outputs={
                    'ENDPOINT_URL': deploy.hc_viewer_url,
                },
                commands=['curl -Ssf $ENDPOINT_URL'],
            ),
        )
        deploy_stage.add_post(
            pipelines.ShellStep(
                'TestAPIGatewayEndpoint',
                env_from_cfn_outputs={
                    'ENDPOINT_URL': deploy.hc_endpoint,
                },
                commands=[
                    'curl -Ssf $ENDPOINT_URL',
                    'curl -Ssf $ENDPOINT_URL/hello',
                    'curl -Ssf $ENDPOINT_URL/test',
                ],
            ),
        )
