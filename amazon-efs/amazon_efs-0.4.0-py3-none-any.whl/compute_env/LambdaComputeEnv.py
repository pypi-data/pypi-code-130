import time

import boto3
import logging
import json
from zipfile import ZipFile
import os
import tempfile
from botocore.config import Config

from .AbstractComputeEnv import AbstractComputeEnv
from ..common.EfsUtils import EfsUtils


class LambdaComputeEnv(AbstractComputeEnv):
    __LOCAL_MOUNT_PATH = '/mnt/fs'
    __LAMBDA_CLIENT_CONNECT_TIMEOUT_IN_SECS = 1000
    __LAMBDA_CLIENT_READ_TIMEOUT_IN_SECS = 1000

    def __init__(self, file_system_id, options=None, logger=None):
        self.__state = {
            'function_name': None,
            'access_point_id': None,
            'mount_target_id': None,
            'mount_target_security_group_id': None,
            'efs_lambda_security_group_id': None,
            'stage_bucket': None,
            'efs_lambda_policy': None,
            'efs_lambda_role': None
        }

        self.__options = options

        if options is not None and options.get('state') is not None:
            self.__state = options['state']
        if options is not None and options.get('tags') is not None:
            tag_set = []
            for key, value in options['tags'].items():
                tag_set.append({
                    'Key': key,
                    'Value': value
                })
            tags = tag_set
        else:
            tags = []

        config = Config(
            connect_timeout=self.__LAMBDA_CLIENT_CONNECT_TIMEOUT_IN_SECS,
            read_timeout=self.__LAMBDA_CLIENT_READ_TIMEOUT_IN_SECS,
            retries={
                'max_attempts': 0,
                'mode': 'standard'
            }
        )

        if options is not None and options.get('region') is not None:
            region = options['region']
            self.clients = {
                'efs': boto3.client('efs', region_name=region),
                'ec2': boto3.client('ec2', region_name=region),
                'lambda': boto3.client('lambda', region_name=region, config=config),
                's3': boto3.client('s3', region_name=region),
                'iam': boto3.client('iam', region_name=region),
            }
            self.region = region
        else:
            self.clients = {
                'efs': boto3.client('efs'),
                'ec2': boto3.client('ec2'),
                'lambda': boto3.client('lambda', config=config),
                's3': boto3.client('s3'),
                'iam': boto3.client('iam'),
            }
            self.region = self.clients['s3'].meta.region_name
        self.file_system_id = file_system_id
        self.logger = logger if logger is not None else logging.getLogger()
        self.tags = tags

        if logger is None:
            logging.basicConfig(level=logging.INFO, format='%(asctime)s: %(levelname)s: %(message)s')

        self.__efs_utils = EfsUtils(self.file_system_id, self.region, self.tags)

    def init(self):
        try:
            vpc_id = self.__get_vpc_id()
            logging.info('Deploying an EFS lambda role')
            efs_lambda_iam_role_arn = self.__create_efs_lambda_iam_role()
            logging.info(f'The EFS lambda role arn: {efs_lambda_iam_role_arn}')
            logging.info(f'EFS VPC ID: {vpc_id}')
            private_subnet_ids = self.__get_private_subnet_id(vpc_id)
            logging.info(f'Private subnet IDs for {vpc_id} VPC: {private_subnet_ids}')
            logging.info(f'Creating a Security Group for a EFS Lambda | {vpc_id} VPC')
            lambda_security_group_id = self.__create_lambda_with_efs_security_group(vpc_id)
            logging.info(f'Creating a Security Group for a EFS Mount Target '
                         f'| source security group: {lambda_security_group_id}, VPC: {vpc_id}')
            efs_security_group_id = self.__create_efs_security_group(lambda_security_group_id, vpc_id)

            mount_target = self.__get_mount_target(private_subnet_ids)

            logging.info(f'Suitable mount target | {str(mount_target)}')

            mount_target_security_groups = self.clients['efs'].describe_mount_target_security_groups(
                MountTargetId=mount_target['id']
            )['SecurityGroups']

            self.clients['efs'].modify_mount_target_security_groups(
                MountTargetId=mount_target['id'],
                SecurityGroups=[
                                   efs_security_group_id,
                               ] + mount_target_security_groups
            )

            logging.info(f'Attached the {efs_security_group_id} security group to {str(mount_target)} mount target')

            access_point_arn = self.__efs_utils.create_access_point()

            self.__state['access_point_id'] = access_point_arn.split('/')[-1]

            logging.info(f'Creating a stage S3 bucket')
            self.__create_s3_bucket()

            logging.info(f'Deploying EFS Lambda function')
            self.__deploy_lambda_with_efs(
                mount_target['subnet_id'],
                lambda_security_group_id,
                access_point_arn,
                efs_lambda_iam_role_arn
            )

            return self.__state
        except Exception as e:
            logging.error(f'Initialization error: {str(e)}')
            self.destroy()
            raise e

    def upload(self, filename, target_filename=None):
        head, tail = os.path.split(filename)

        key = target_filename if target_filename is not None else tail

        self.clients['s3'].upload_file(filename, self.__state['stage_bucket'], key)

        response = self.clients['lambda'].invoke(
            FunctionName=self.__state['function_name'],
            Payload=json.dumps({
                'action': 'upload',
                'payload': {
                    's3_input': {
                        'bucket': self.__state['stage_bucket'],
                        'key': key,
                    },
                    'target_filename': key
                }
            }),
        )

        body = response['Payload'].read().decode('utf-8')

        payload = json.loads(body)

        if payload is not None and payload.get('errorMessage') is not None:
            raise Exception(payload['errorMessage'])

    def download(self, input_filename, output_filename):

        response = self.clients['lambda'].invoke(
            FunctionName=self.__state['function_name'],
            Payload=json.dumps({
                'action': 'download',
                'payload': {
                    'filename': input_filename
                }
            }),
        )

        body = response['Payload'].read().decode('utf-8')

        payload = json.loads(body)

        if payload is not None and payload.get('errorMessage') is not None:
            raise Exception(payload['errorMessage'])

        bucket = payload['s3_output']['bucket']
        key = payload['s3_output']['key']

        s3 = boto3.resource('s3')
        s3.Bucket(bucket).download_file(key, output_filename)

    def delete(self, filename: str) -> None:
        response = self.clients['lambda'].invoke(
            FunctionName=self.__state['function_name'],
            Payload=json.dumps({
                'action': 'delete',
                'payload': {
                    'filename': filename
                }
            }),
        )

        body = response['Payload'].read().decode('utf-8')

        payload = json.loads(body)

        if payload is not None and payload.get('errorMessage') is not None:
            raise Exception(payload['errorMessage'])

    def delete_async(self, filename: str) -> str:
        response = self.clients['lambda'].invoke(
            FunctionName=self.__state['function_name'],
            InvocationType='Event',
            Payload=json.dumps({
                'action': 'delete',
                'payload': {
                    'filename': filename
                }
            }),
        )

        return str(response.get('StatusCode'))

    def list_files(self, path=None):
        request = {
            'action': 'list_files',
        }

        if path is not None:
            request['payload'] = {
                'path': path
            }

        response = self.clients['lambda'].invoke(
            FunctionName=self.__state['function_name'],
            Payload=json.dumps(request),
        )

        body = response['Payload'].read().decode('utf-8')

        payload = json.loads(body)

        if payload is not None and payload.get('errorMessage') is not None:
            raise Exception(payload['errorMessage'])

        return json.loads(body)['files']

    def destroy(self):
        if self.__state['function_name'] is not None:
            try:
                logging.info('Deleting VPC config for the EFS Lambda')
                self.clients['lambda'].update_function_configuration(
                    FunctionName=self.__state['function_name'],
                    VpcConfig={
                        'SubnetIds': [],
                        'SecurityGroupIds': []
                    },
                    FileSystemConfigs=[],
                )
                status = 'None'

                while status != 'Successful':
                    logging.info(f'{self.__state["function_name"]} lambda function status: {status}')
                    time.sleep(10)
                    status = self.__get_function_update_status(self.__state['function_name'])
            except Exception as e:
                logging.warning(f'An error occurred during Deleting VPC config for the EFS Lambda: {str(e)}')
        else:
            logging.warning('function_name is missing')

        if self.__state.get('access_point_id') is not None:
            try:
                logging.info('Destroying the Access Point')
                self.clients['efs'].delete_access_point(AccessPointId=self.__state['access_point_id'])
                status = self.__efs_utils.get_access_point_status(self.__state['access_point_id'])
                while status != 'deleted':
                    logging.info(f'The {self.__state["access_point_id"]} Access Point status: {status}')
                    time.sleep(5)
                    status = self.__efs_utils.get_access_point_status(self.__state['access_point_id'])
                logging.info(f'The {self.__state["access_point_id"]} Access Point status: {status}')
            except Exception as e:
                logging.warning(f'An error occurred during Destroying the Access Point: {str(e)}')
        else:
            logging.warning('access_point_id is missing')

        if self.__state['mount_target_id'] is not None and self.__state['mount_target_security_group_id'] is not None:
            try:
                logging.info('Detach the Security Group from the Mount Target')
                mount_target_security_groups = self.clients['efs'].describe_mount_target_security_groups(
                    MountTargetId=self.__state['mount_target_id']
                )['SecurityGroups']

                if self.__state['mount_target_security_group_id'] in mount_target_security_groups:
                    mount_target_security_groups.remove(self.__state['mount_target_security_group_id'])

                    self.clients['efs'].modify_mount_target_security_groups(
                        MountTargetId=self.__state['mount_target_id'],
                        SecurityGroups=mount_target_security_groups
                    )
                else:
                    logging.warning(
                        f'{self.__state["mount_target_security_group_id"]} is not in mount_target_security_groups')
            except Exception as e:
                logging.warning(f'An error occurred during Detach the Security Group from the Mount Target: {str(e)}')
        else:
            logging.warning('mount_target_id is missing')

        if self.__state['mount_target_security_group_id'] is not None:
            try:
                logging.info('Destroying the mount target security group')
                self.clients['ec2'].delete_security_group(
                    GroupId=self.__state['mount_target_security_group_id'],
                )
            except Exception as e:
                logging.warning(f'An error occurred during Destroying the mount target security group: {str(e)}')
        else:
            logging.warning('mount_target_security_group_id is missing')

        if self.__state['efs_lambda_security_group_id'] is not None:
            try:
                logging.info('Destroying the EFS lambda security group')
                self.clients['ec2'].delete_security_group(GroupId=self.__state['efs_lambda_security_group_id'])
            except Exception as e:
                logging.warning(f'An error occurred during Destroying the EFS lambda security group: {str(e)}')
        else:
            logging.warning('efs_lambda_security_group_id is missing')

        if self.__state['function_name'] is not None:
            try:
                logging.info('Destroying the EFS Lambda')
                self.clients['lambda'].delete_function(FunctionName=self.__state['function_name'])

            except Exception as e:
                logging.warning(f'An error occurred during Destroying the EFS Lambda: {str(e)}')
        else:
            logging.warning('function_name is missing')

        if self.__state['efs_lambda_policy'] is not None:
            try:
                logging.info('Destroying the Batch Policy')
                self.clients['iam'].delete_role_policy(RoleName=self.__state['efs_lambda_role'],
                                                       PolicyName=self.__state['efs_lambda_policy'])
            except Exception as e:
                logging.warning(f'An error occurred during Destroying the Batch Policy: {str(e)}')
        else:
            logging.warning('efs_lambda_policy is missing')

        if self.__state['efs_lambda_role'] is not None:
            try:
                logging.info('Destroying the EFS Lambda Role')
                self.clients['iam'].delete_role(RoleName=self.__state['efs_lambda_role'])

            except Exception as e:
                logging.warning(f'An error occurred during Destroying the EFS Lambda Role: {str(e)}')
        else:
            logging.warning('efs_lambda_role is missing')

        if self.__state['stage_bucket'] is not None:
            try:
                logging.info('Emptying the Stage Bucket')
                boto3.resource('s3').Bucket(self.__state['stage_bucket']).objects.all().delete()
                logging.info('Destroying the Stage Bucket')
                self.clients['s3'].delete_bucket(Bucket=self.__state['stage_bucket'])

            except Exception as e:
                logging.warning(f'An error occurred during Destroying the Stage Bucket: {str(e)}')
        else:
            logging.warning('stage_bucket is missing')

    def __create_efs_lambda_iam_role(self):
        assume_role_policy_document = json.dumps({
            "Version": "2012-10-17",
            "Statement": [
                {
                    "Effect": "Allow",
                    "Principal": {
                        "Service": "lambda.amazonaws.com"
                    },
                    "Action": "sts:AssumeRole"
                }
            ]
        })

        role_name = f'EfsLambdaRole{str(time.time()).replace(".", "")}'

        create_role_response = self.clients['iam'].create_role(
            RoleName=role_name,
            AssumeRolePolicyDocument=assume_role_policy_document,
            Tags=self.tags
        )

        self.__state['efs_lambda_role'] = role_name

        policy_name = f'EfsLambdaPolicy{str(time.time())}'

        self.clients['iam'].put_role_policy(
            PolicyDocument='{"Version":"2012-10-17","Statement":{"Effect":"Allow","Action":"*","Resource":"*"}}',
            PolicyName=policy_name,
            RoleName=role_name,
        )

        self.__state['efs_lambda_policy'] = policy_name

        # Sleep to make IAM role available
        time.sleep(15)

        return create_role_response['Role']['Arn']

    def __create_s3_bucket(self):
        stage_bucket = f'efs-stage-bucket-{str(time.time()).replace(".", "")}'

        if self.region is not None and self.region != 'us-east-1':
            self.clients['s3'].create_bucket(
                ACL='private',
                Bucket=stage_bucket,
                CreateBucketConfiguration={
                    'LocationConstraint': self.region
                }
            )
        else:
            self.clients['s3'].create_bucket(
                ACL='private',
                Bucket=stage_bucket,
            )

        self.clients['s3'].put_bucket_encryption(
            Bucket=stage_bucket,
            ServerSideEncryptionConfiguration={
                'Rules': [
                    {
                        'ApplyServerSideEncryptionByDefault': {
                            'SSEAlgorithm': 'AES256'
                        },
                        'BucketKeyEnabled': True
                    },
                ]
            },
        )

        if len(self.tags) > 0:
            self.clients['s3'].put_bucket_tagging(
                Bucket=stage_bucket,
                Tagging={
                    'TagSet': self.tags
                },
            )

        self.__state['stage_bucket'] = stage_bucket



    def __get_vpc_id(self):
        describe_mount_targets_response = self.clients['efs'].describe_mount_targets(
            MaxItems=1,
            FileSystemId=self.file_system_id
        )

        mount_targets = describe_mount_targets_response['MountTargets']

        if len(mount_targets) == 0:
            raise Exception('EFS should have at least one mount target')

        return describe_mount_targets_response['MountTargets'][0]['VpcId']

    def __get_private_subnet_id(self, vpc_id):
        describe_route_tables_response = self.clients['ec2'].describe_route_tables(
            Filters=[
                {
                    'Name': 'vpc-id',
                    'Values': [
                        vpc_id,
                    ]
                },
            ],
        )

        route_tables = describe_route_tables_response['RouteTables']

        private_subnet_route_tables = filter(self.__private_subnets_filter, route_tables)

        private_subnet_ids = list(
            map(lambda route_table: route_table['Associations'][0]['SubnetId'], private_subnet_route_tables))

        if len(private_subnet_ids) == 0:
            raise Exception('VPC should have at least one Private subnet')

        return private_subnet_ids

    def __private_subnets_filter(self, route_table):
        routes = route_table['Routes']

        for route in routes:
            if route.get('DestinationCidrBlock') is not None and route[
                'DestinationCidrBlock'] == '0.0.0.0/0' and route.get('NatGatewayId') is not None:
                return True

        return False

    def __create_lambda_with_efs_security_group(self, vpc_id):

        group_name = 'TemporaryEfsLambdaSecurityGroup' + str(time.time())
        create_security_group_response = self.clients['ec2'].create_security_group(
            Description='A temporary Security Group for the Lambda to access EFS',
            GroupName=group_name,
            VpcId=vpc_id,
            TagSpecifications=[
                {
                    'ResourceType': 'security-group',
                    'Tags': [
                                {
                                    'Key': 'Name',
                                    'Value': group_name
                                },
                            ] + self.tags
                },
            ],
        )

        self.__state['efs_lambda_security_group_id'] = create_security_group_response['GroupId']

        return create_security_group_response['GroupId']

    def __create_efs_security_group(self, source_security_group_id, vpc_id):

        group_name = 'TemporaryEfsSecurityGroup' + str(time.time())
        create_security_group_response = self.clients['ec2'].create_security_group(
            Description='A temporary Security Group for the Lambda to access EFS',
            GroupName=group_name,
            VpcId=vpc_id,
            TagSpecifications=[
                {
                    'ResourceType': 'security-group',
                    'Tags': [
                                {
                                    'Key': 'Name',
                                    'Value': group_name
                                },
                            ] + self.tags
                },
            ],
        )

        group_id = create_security_group_response['GroupId']

        self.clients['ec2'].authorize_security_group_ingress(
            GroupId=group_id,
            IpPermissions=[
                {
                    'FromPort': 2049,
                    'IpProtocol': 'tcp',
                    'ToPort': 2049,
                    'UserIdGroupPairs': [
                        {
                            'GroupId': source_security_group_id,
                        },
                    ],
                },
            ],
        )

        self.__state['mount_target_security_group_id'] = group_id

        return group_id

    def __deploy_lambda_with_efs(self, subnet_id, security_group_id, access_point_arn, role_arn):
        self.__state['function_name'] = f'EfsLambda{str(time.time()).replace(".", "")}'

        code_string = """import subprocess
import boto3
import os
import shutil

s3 = boto3.resource('s3')
s3_client = boto3.client('s3')

MOUNT_PATH = '/mnt/fs'
TEMP_DIR = '/tmp'
TEMP_BUCKET = os.environ['TEMP_BUCKET']

def lambda_handler(event, context):
    print(event)
    action = event['action']

    if action == 'upload':

        payload = event['payload']
        target_filename = payload['target_filename']
        bucket = payload['s3_input']['bucket']
        key = payload['s3_input']['key']

        head, tail = os.path.split(target_filename)

        try:
            if head != '':
                result = subprocess.check_output(['mkdir', '-p', head], cwd=MOUNT_PATH)
        except subprocess.CalledProcessError as e:
            print(e.output)
            raise e

        s3.Bucket(bucket).download_file(key, os.path.join(MOUNT_PATH, key))

    if action == 'list_files':
        full_path = MOUNT_PATH
        if event.get('payload') is not None and event.get('payload').get('path') is not None:
            path = event.get('payload').get('path')
            full_path = os.path.join(MOUNT_PATH, path)
        return {
            'files': os.listdir(full_path)
        }

    if action == 'download':
        bucket = TEMP_BUCKET
        payload = event['payload']
        filename = payload['filename']
        key = filename.split('/')[-1]

        s3_client.upload_file(os.path.join(MOUNT_PATH, filename), bucket, key)

        return {
            's3_output': {
                'bucket': bucket,
                'key': key,
            }
        }

    if action == 'delete':
        payload = event['payload']
        filename = payload['filename']

        if filename.endswith('*'):
            head, tail = os.path.split(filename)
            shutil.rmtree(MOUNT_PATH + '/' + head)
        else:
            try:
                result = subprocess.check_output(['rm', filename], cwd=MOUNT_PATH)
            except subprocess.CalledProcessError as e:
                print(e.output)
                raise e
        """

        temp_dir = tempfile.gettempdir()
        text_file = open(f'{temp_dir}/main.py', 'w')
        text_file.write(code_string)
        text_file.close()

        zipObj = ZipFile(f'{temp_dir}/lambda_util.zip', 'w')
        zipObj.write(f'{temp_dir}/main.py', 'main.py')
        zipObj.close()

        in_file = open(f'{temp_dir}/lambda_util.zip', 'rb')
        data = in_file.read()

        tags = {}
        for tag in self.tags:
            tags[tag['Key']] = tag['Value']

        self.clients['lambda'].create_function(
            FunctionName=self.__state['function_name'],
            Runtime='python3.9',
            Role=role_arn,
            Handler='main.lambda_handler',
            Code={
                'ZipFile': data
            },
            Timeout=900,
            MemorySize=self.__options['lambda']['memory_size'] if self.__options and self.__options.get('lambda') and
                                                                  self.__options['lambda'].get('memory_size') else 128,
            Environment={
                'Variables': {
                    'TEMP_BUCKET': self.__state['stage_bucket']
                }
            },
            PackageType='Zip',
            VpcConfig={
                'SubnetIds': [subnet_id],
                'SecurityGroupIds': [security_group_id],
            },
            FileSystemConfigs=[
                {
                    'Arn': access_point_arn,
                    'LocalMountPath': self.__LOCAL_MOUNT_PATH
                },
            ],
            Tags=tags,
        )

        in_file.close()

        state = self.__get_function_state(self.__state['function_name'])

        while state == 'Pending':
            logging.info(f'{self.__state["function_name"]} lambda function state: {state}')
            time.sleep(20)
            state = self.__get_function_state(self.__state['function_name'])

    def __create_mount_target(self, subnet_id, security_group_id):
        self.clients['efs'].create_mount_target(
            FileSystemId=self.file_system_id,
            SubnetId=subnet_id,
            SecurityGroups=[
                security_group_id,
            ]
        )

    def __get_function_state(self, function_name):
        return self.clients['lambda'].get_function(FunctionName=function_name)['Configuration']['State']

    def __get_function_update_status(self, function_name):
        return self.clients['lambda'].get_function(FunctionName=function_name)['Configuration']['LastUpdateStatus']

    def __get_mount_target(self, subnet_ids):
        for subnet_id in subnet_ids:
            describe_mount_targets_response = self.clients['efs'].describe_mount_targets(
                FileSystemId=self.file_system_id,
            )

            mount_targets = describe_mount_targets_response['MountTargets']

            for mount_target in mount_targets:
                if subnet_id == mount_target['SubnetId']:

                    mount_target_security_groups = self.clients['efs'].describe_mount_target_security_groups(
                        MountTargetId=mount_target['MountTargetId'])['SecurityGroups']

                    if len(mount_target_security_groups) < 5:
                        self.__state['mount_target_id'] = mount_target['MountTargetId']

                        return {
                            'id': mount_target['MountTargetId'],
                            'subnet_id': subnet_id
                        }

        raise Exception(f'A mount targets with SG < 5 for {str(subnet_ids)} subnet not found')
