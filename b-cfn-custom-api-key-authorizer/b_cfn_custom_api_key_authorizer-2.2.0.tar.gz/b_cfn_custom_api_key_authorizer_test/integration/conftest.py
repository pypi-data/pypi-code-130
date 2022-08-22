import os

from b_aws_cdk_parallel.deployment_executor import DeploymentExecutor
from b_aws_cdk_parallel.deployment_type import DeploymentType
from b_aws_testing_framework.credentials import Credentials
from b_aws_testing_framework.tools.cdk_testing.cdk_tool_config import CdkToolConfig
from b_aws_testing_framework.tools.cdk_testing.testing_manager import TestingManager

GLOBAL_PREFIX = os.environ.get('GLOBAL_PREFIX')
DO_NOT_CREATE_INFRASTRUCTURE = int(os.environ.get('DO_NOT_CREATE_INFRASTRUCTURE', 0))
DO_NOT_DESTROY_INFRASTRUCTURE = int(os.environ.get('DO_NOT_DESTROY_INFRASTRUCTURE', 0))

CDK_PATH = f'{os.path.dirname(os.path.abspath(__file__))}'
MANAGER = TestingManager(Credentials(), CdkToolConfig(CDK_PATH, destroy_before_preparing=False))
if GLOBAL_PREFIX: MANAGER.set_global_prefix(f'B{GLOBAL_PREFIX[:10]}')

# Import all fixtures.
# noinspection PyUnresolvedReferences
from .fixtures import *


def pytest_sessionstart(session):
    inf_create()


def pytest_sessionfinish(session, exitstatus):
    inf_destroy()


def inf_create():
    if DO_NOT_CREATE_INFRASTRUCTURE == 1:
        return

    def wrapper(cdk_config: CdkToolConfig):
        DeploymentExecutor(
            type=DeploymentType.DEPLOY,
            path=cdk_config.cdk_app_path,
            env=cdk_config.deployment_process_environment,
        ).run()

    MANAGER.prepare_infrastructure(wrapper)


def inf_destroy():
    if DO_NOT_DESTROY_INFRASTRUCTURE == 1:
        return

    def wrapper(cdk_config: CdkToolConfig):
        DeploymentExecutor(
            type=DeploymentType.DESTROY,
            path=cdk_config.cdk_app_path,
            env=cdk_config.deployment_process_environment,
        ).run()

    MANAGER.destroy_infrastructure(wrapper)
