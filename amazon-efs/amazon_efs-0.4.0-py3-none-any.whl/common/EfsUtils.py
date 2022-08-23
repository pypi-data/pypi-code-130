import time
import boto3

efs = boto3.client('efs')


class EfsUtils:
    def __init__(self, file_system_id: str, region: str = 'us-east-1', tags: list[dict] = None):
        self.__region = region
        self.__tags = tags if tags is not None else []
        self.__file_system_id = file_system_id
        self.efs_client = boto3.client('efs', region_name=region)

    def create_access_point(self):
        create_access_point_response = self.efs_client.create_access_point(
            Tags=[
                     {
                         'Key': 'Name',
                         'Value': f'TemporaryAccessPoint{str(time.time())}'
                     },
                 ] + self.__tags,
            FileSystemId=self.__file_system_id,
            PosixUser={
                'Uid': 0,
                'Gid': 0
            },
            RootDirectory={
                'Path': '/',
                'CreationInfo': {
                    'OwnerUid': 0,
                    'OwnerGid': 0,
                    'Permissions': '0777'
                }
            }
        )

        access_point_arn = create_access_point_response['AccessPointArn']

        access_point_id = create_access_point_response['AccessPointId']

        return access_point_arn

    def get_access_point_status(self, access_point_id):
        try:
            access_points = self.efs_client.describe_access_points(
                MaxResults=1,
                AccessPointId=access_point_id,
            )['AccessPoints']

            if len(access_points) == 0:
                return 'deleted'

            return access_points[0]['LifeCycleState']
        except Exception as e:
            if 'AccessPointNotFound' in str(e):
                return 'deleted'
            raise e
