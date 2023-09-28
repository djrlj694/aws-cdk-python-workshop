"""
Defines a class (`WorkshopPipelineStage`) modeling an AWS CDK pipeline's stage.
"""
from aws_cdk import Stage
from constructs import Construct

from .cdk_workshop_stack import CdkWorkshopStack


# SECTION: CLASSES ========================================================== #


class WorkshopPipelineStage(Stage):
    """
    A class modeling an AWS CDK pipeline's stage.
    """

    @property
    def hc_endpoint(self):
        return self._hc_endpoint

    @property
    def hc_viewer_url(self):
        return self._hc_viewer_url

    def __init__(self, scope: Construct, construct_id: str, **kwargs) -> None:
        """
        The class constructor.

        Parameters
        ----------
        `scope` : `Construct`
            The stage's parent, usually an App or a Stage, but could be any
            construct.
        `construct_id` : `str`
            The stage's construct ID.
        """
        super().__init__(scope, construct_id, **kwargs)

        service = CdkWorkshopStack(self, 'WebService')

        self._hc_endpoint = service.hc_endpoint
        self._hc_viewer_url = service.hc_viewer_url
