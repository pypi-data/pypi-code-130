import os
from aws_pcluster_helpers.models.sinfo import SInfoTable, SinfoRow
from aws_pcluster_helpers.models import nextflow
from rich.console import Console
from rich.table import Table
import sys
from prefect import Flow, task
from prefect.tasks.shell import ShellTask
import time
import tempfile
import json

from aws_pcluster_bootstrap_helpers.utils.logging import setup_logger

logger = setup_logger("build-ami")

shell_task = ShellTask(log_stderr=True, log_stdout=True, stream_output=True)

BUILD_IN_PROGRESS = "BUILD_IN_PROGRESS"
BUILD_FAILED = "BUILD_FAILED"
BUILD_COMPLETE = "BUILD_COMPLETE"
DELETE_IN_PROGRESS = "DELETE_IN_PROGRESS"
DELETE_FAILED = "DELETE_FAILED"
DELETE_COMPLETE = "DELETE_COMPLETE"


def read_json(content, file):
    f = open(file)
    try:
        data = json.load(f)
    except Exception as e:
        logger.warn(f'Error reading in pcluster build file: {file}: {e}')
        raise Exception(e)

    del data['imageConfiguration']['url']
    image_status = data['imageBuildStatus']
    logger.info(f'Pcluster build status: {image_status}')
    if image_status == 'BUILD_FAILED':
        raise Exception(f'Image build failed: {image_status}')
    elif image_status == 'BUILD_IN_PROGRESS':
        return True
    elif image_status == 'BUILD_COMPLETE':
        return False
    else:
        raise Exception(f'Image status not compatible with bootstrap: {image_status}')


@task
def build_in_progress(image_id: str, region="us-east-1"):
    build_in_process = True
    n = 1
    while build_in_process:
        with tempfile.NamedTemporaryFile(suffix=".json") as tmpfile:
            logger.info(f'Pcluster: {image_id}, Region: {region}, N: {1} Data file: {tmpfile.name}')
            contents = shell_task.run(
                command=f'pcluster describe-image --image-id {image_id} --region {region} > {tmpfile.name}'
            )
            build_in_process = read_json(contents, tmpfile.name)
        n = n + 1
        # sleep for 10 minutes
        if build_in_process:
            time.sleep(600)


@task
def build_complete(image_id: str, output_file: str, region="us-east-1"):
    contents = shell_task.run(
        command=f'pcluster describe-image --image-id {image_id} --region {region} > {output_file}'
    )
    build_in_process = read_json(contents, output_file)


def main(image_id: str, output_file: str, region: str = "us-east-1"):
    with Flow("pcluster-build-ami-flow") as flow:
        build_in_progress(image_id=image_id, region=region)
        build_complete(image_id=image_id, region=region, output_file=output_file)
    flow_state = flow.run()
    return flow_state


if __name__ == "__main__":
    main(
        image_id=os.environ.get('PCLUSTER_BUILD_AMI_ID'),
        output_file=os.environ.get('PCLUSTER_BUILD_AMI_FILE'),
        region=os.environ.get("AWS_DEFAULT_REGION")
    )
