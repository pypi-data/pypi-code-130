import json
from loguru import logger
from tencentcloud.common.exception.tencent_cloud_sdk_exception import TencentCloudSDKException


class TdmqManager:

	_agent: None

	def __init__(self, agent):
		self._agent = agent

	def list_queues(self, ):
		return self._agent.list_queues()

	def describe_queue(self, queue_name: str):
		return self._agent.describe_queue(queue_name)

	def queue_is_exist(self, queue_name):
		try:
			resp = self.describe_queue(queue_name)
			return True
		except TencentCloudSDKException as e:
			if e.code == 'ResourceNotFound' and e.message == 'The resource is not found.':
				return False
			raise Exception(e)

	def create_queue(self, queue_name):
		return self._agent.create_queue(queue_name)

	def delete_queue(self, queue_name):
		return self._agent.delete_queue(queue_name)