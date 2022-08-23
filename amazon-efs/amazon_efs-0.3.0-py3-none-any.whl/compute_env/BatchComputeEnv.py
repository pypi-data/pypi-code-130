import uuid
import json
import time
import boto3
import logging
import os

from .AbstractComputeEnv import AbstractComputeEnv
from ..common.EfsUtils import EfsUtils
from ..common.general import convert_tag_obj_to_tag_arr


class BatchComputeEnv(AbstractComputeEnv):
    __LOCAL_MOUNT_PATH = '/mnt/fs'
    __BATCH_JOB_POLL_INTERVAL_IN_SECS = 60

    def __init__(self, file_system_id, options=None, logger=None):
        if options.get('batch_queue') is None:
            raise Exception('A batch queue is required')

        run_id = str(uuid.uuid4()).replace('-', '')

        options.get('job_name', f'CleanEFS_{run_id}')

        self.__state = {
            'job_name': options.get('job_name', f'CleanEFS_{run_id}'),
            'job_definition_name': options.get('job_definition_name', f'CleanEFS_{run_id}'),
            'batch_queue': options['batch_queue']
        }

        if options is not None and options.get('region') is not None:
            region = options['region']
            self.clients = {
                'efs': boto3.client('efs', region_name=region),
                'ec2': boto3.client('ec2', region_name=region),
                'batch': boto3.client('batch', region_name=region),
                's3': boto3.client('s3', region_name=region),
                'iam': boto3.client('iam', region_name=region),
            }
            self.__region = region
        else:
            self.clients = {
                'efs': boto3.client('efs'),
                'ec2': boto3.client('ec2'),
                'batch': boto3.client('batch'),
                's3': boto3.client('s3'),
                'iam': boto3.client('iam'),
            }
            self.__region = self.clients['s3'].meta.region_name
        self.__file_system_id = file_system_id

        self.__logger = logger if logger is not None else logging.getLogger()
        if logger is None:
            logging.basicConfig(level=logging.INFO, format='%(asctime)s: %(levelname)s: %(message)s')

        self.__tags = options.get('tags', {
            'app': 'amazon-efs'
        })

        if options is not None and options.get('state') is not None:
            self.__state = options['state']

        self.__efs_utils = EfsUtils(self.__file_system_id, self.__region, self.__tags)

    def init(self) -> dict:
        self.__create_batch_role()
        efs_utils = EfsUtils(self.__file_system_id, self.__region, convert_tag_obj_to_tag_arr(self.__tags))
        self.__state['access_point_arn'] = efs_utils.create_access_point()
        self.__create_job_definition()
        return self.__state

    def upload(self, filename: str, target_filename: str = None) -> None:
        raise Exception('A method is not is not implemented')

    def download(self, input_filename: str, output_filename: str) -> None:
        raise Exception('A method is not is not implemented')

    def delete(self, filename: str) -> None:
        if filename.endswith('*'):
            head, tail = os.path.split(filename)
            filename = head
        commands = ['rm', '-fr', f'{self.__LOCAL_MOUNT_PATH}/{filename}']
        response = self.__run_job(commands)

        job_id = response['jobArn']

        self.__logger.info(f'Batch job ARN: {job_id}')

        response = self.clients['batch'].describe_jobs(jobs=[job_id])

        job = response['jobs'][0]

        status = job['status'] # 'SUBMITTED'|'PENDING'|'RUNNABLE'|'STARTING'|'RUNNING'|'SUCCEEDED'|'FAILED'

        while status != 'SUCCEEDED' and status != 'FAILED':
            time.sleep(self.__BATCH_JOB_POLL_INTERVAL_IN_SECS)
            self.__logger.info(f'Batch job status: {status}')
            response = self.clients['batch'].describe_jobs(jobs=[job_id])
            job = response['jobs'][0]
            status = job['status']

        stream_name = job['container']['logStreamName']
        self.__logger.info(f'Batch job stream name: {stream_name}')

        self.__logger.info(f'Batch job status: {status}')

        if status == 'FAILED':
            raise Exception(response)

    def list_files(self, path: str = None) -> list[str]:
        raise Exception('A method is not is not implemented')

    def destroy(self) -> None:
        self.clients['batch'].deregister_job_definition(
            jobDefinition=self.__state['job_definition_name']
        )

        if self.__state['job_definition_name'] is not None:
            try:
                logging.info('Destroying the job definition')
                self.clients['batch'].deregister_job_definition(
                    jobDefinition=self.__state['job_definition_name']
                )
                logging.info(f'The {self.__state["job_definition_name"]} job definition has been deleted')
            except Exception as e:
                logging.warning(f'An error occurred during Destroying the job definition: {str(e)}')
        else:
            logging.warning('job_definition_name is missing')

        if self.__state['access_point_arn'] is not None:
            try:
                logging.info('Destroying the Access Point')
                access_point_id = self.__state['access_point_arn'].split('/')[-1]
                self.clients['efs'].delete_access_point(AccessPointId=access_point_id)
                status = self.__efs_utils.get_access_point_status(access_point_id)
                while status != 'deleted':
                    logging.info(f'The {access_point_id} Access Point status: {status}')
                    time.sleep(5)
                    status = self.__efs_utils.get_access_point_status(access_point_id)
                logging.info(f'The {access_point_id} Access Point status: {status}')
            except Exception as e:
                logging.warning(f'An error occurred during Destroying the Access Point: {str(e)}')
        else:
            logging.warning('access_point_arn is missing')

        if self.__state['batch_policy'] is not None:
            try:
                logging.info('Destroying the Batch Policy')
                self.clients['iam'].delete_role_policy(RoleName=self.__state['batch_role_arn'].split('/')[-1],
                                                       PolicyName=self.__state['batch_policy'])
                logging.info(f"The {self.__state['batch_policy']} batch policy has been deleted")
            except Exception as e:
                logging.warning(f'An error occurred during Destroying the Batch Policy: {str(e)}')
        else:
            logging.warning('batch_policy is missing')

        if self.__state['batch_role_arn'] is not None:
            try:
                logging.info('Destroying the Batch Role')
                batch_role_name = self.__state['batch_role_arn'].split('/')[-1]
                self.clients['iam'].delete_role(RoleName=batch_role_name)
                logging.info(f'The {batch_role_name} batch role has been deleted')
            except Exception as e:
                logging.warning(f'An error occurred during Destroying the Batch Role: {str(e)}')
        else:
            logging.warning('batch_role_arn is missing')

    def __create_batch_role(self):
        assume_role_policy_document = json.dumps({
            "Version": "2012-10-17",
            "Statement": [
                {
                    "Effect": "Allow",
                    "Principal": {
                        "Service": "ecs-tasks.amazonaws.com"
                    },
                    "Action": "sts:AssumeRole"
                }
            ]
        })

        role_name = f'BatchRole{str(time.time()).replace(".", "")}'

        create_role_response = self.clients['iam'].create_role(
            RoleName=role_name,
            AssumeRolePolicyDocument=assume_role_policy_document,
            Tags=convert_tag_obj_to_tag_arr(self.__tags)
        )

        self.__state['batch_role_arn'] = create_role_response['Role']['Arn']

        policy_name = f'EfsLambdaPolicy{str(time.time())}'

        self.clients['iam'].put_role_policy(
            PolicyDocument='{"Version":"2012-10-17","Statement":{"Effect":"Allow","Action":"*","Resource":"*"}}',
            PolicyName=policy_name,
            RoleName=role_name,
        )

        self.__state['batch_policy'] = policy_name

        # Sleep to make IAM role available
        time.sleep(15)

    def __create_job_definition(self):
        batch_role_arn = self.__state['batch_role_arn']
        access_point_id = self.__state['access_point_arn'].split('/')[-1]

        response = self.clients['batch'].register_job_definition(
            jobDefinitionName=self.__state['job_definition_name'],
            type='container',
            containerProperties={
                'image': 'ubuntu',
                'vcpus': 1,
                'memory': 2000,
                # 'command': [
                #    'echo hello',
                # ],
                'jobRoleArn': batch_role_arn,
                'executionRoleArn': batch_role_arn,
                'volumes': [
                    {
                        'name': 'efs',
                        'efsVolumeConfiguration': {
                            'fileSystemId': self.__file_system_id,
                            'rootDirectory': '/',
                            'transitEncryption': 'ENABLED',
                            'authorizationConfig': {
                                'accessPointId': access_point_id,
                                'iam': 'ENABLED'
                            }
                        }
                    },
                ],
                'environment': [
                    {
                        'name': 'string',
                        'value': 'string'
                    },
                ],
                'mountPoints': [
                    {
                        'containerPath': self.__LOCAL_MOUNT_PATH,
                        'readOnly': False,
                        'sourceVolume': 'efs'
                    },
                ],
                'logConfiguration': {
                    'logDriver': 'awslogs',
                },
                # 'networkConfiguration': {
                #    'assignPublicIp': 'ENABLED' | 'DISABLED'
                # },
            },
            propagateTags=True,
            tags=self.__tags,
            platformCapabilities=['EC2']
        )

    def __run_job(self, commands: list[str]):
        job_name = self.__state['job_name']
        job_queue = self.__state['batch_queue']
        job_definition = self.__state['job_definition_name']

        response2 = self.clients['batch'].submit_job(
            jobName=job_name,
            jobQueue=job_queue,
            jobDefinition=job_definition,
            containerOverrides={
                'command': commands,
                'environment': [
                    {
                        'name': 'string',
                        'value': 'string'
                    },
                ],
            },
            propagateTags=True,
            tags=self.__tags
        )

        return response2
