import json
from tencentcloud.tdmq.v20200217 import tdmq_client, models

class TdmqAgent:

	_client: None

	def __init__(self, cred, region):
		self._client = tdmq_client.TdmqClient(cred, region)

	def list_queues(self, ):
		req = models.DescribeCmqQueuesRequest()
		resp = self._client.DescribeCmqQueues(req)
		return resp

	def describe_queue(self, queue_name: str):
		req = models.DescribeCmqQueueDetailRequest()
		params = {
			'QueueName': queue_name
		}
		req.from_json_string(json.dumps(params))
		resp = self._client.DescribeCmqQueueDetail(req)
		return resp

	def create_queue(self, queue_name):
		"""
		MaxMsgHeapNum
		PollingWaitSeconds
		VisibilityTimeout
		MaxMsgSize
		MsgRetentionSeconds
		Tags [{TagKey: TagValue}]
		"""
		req = models.CreateCmqQueueRequest()
		params = {
			'QueueName': queue_name, 
		}
		req.from_json_string(json.dumps(params))
		resp = self._client.CreateCmqQueue(req)
		return resp

	def delete_queue(self, queue_name):
		req = models.DeleteCmqQueueRequest()
		params = {
			'QueueName': queue_name, 
		}
		req.from_json_string(json.dumps(params))
		resp = self._client.DeleteCmqQueue(req)
		return resp