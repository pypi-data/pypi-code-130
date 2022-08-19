from tencentcloud.cvm.v20170312 import cvm_client
from tencentcloud.cvm.v20170312 import models

class CvmAgent:

	_client: None

	def __init__(self, cred, region):
		self._client = cvm_client.CvmClient(cred, region)

	def list_cvms(self, ):
		req = models.DescribeInstancesRequest()
		resp = self._client.DescribeInstances(req)
		return resp
