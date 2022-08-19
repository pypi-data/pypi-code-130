from tencentcloud.common import credential
from .agents.cvm_agent import CvmAgent
from .agents.cam_agent import CamAgent
from .agents.tdmq_agent import TdmqAgent
from .managers.cvm_manager import CvmManager
from .managers.cam_manager import CamManager
from .managers.tdmq_manager import TdmqManager

class TencentcloudManager:


	@staticmethod
	def create_agent(secret_id, secret_key, type_str: str, region: str):
		cred = credential.Credential(secret_id, secret_key)
		p_type = type_str.lower()
		if p_type == 'cvm':
			agent = CvmAgent(cred, region)
		elif p_type == 'tdmq':
			agent = TdmqAgent(cred, region)
		elif p_type == 'cam':
			agent = CamAgent(cred, region)
		else:
			raise Exception(f'unknown type: {type_str}')
		return agent

	@staticmethod
	def create_manager(secret_id, secret_key, type_str: str, region: str):
		agent = TencentcloudManager.create_agent(secret_id, secret_key, type_str, region)
		if type(agent) == CvmAgent:
			manager = CvmManager(agent)
		elif type(agent) == TdmqAgent:
			manager = TdmqManager(agent)
		elif type(agent) == CamAgent:
			manager = CamManager(agent)
		else:
			raise Exception(f'unknown type: {type_str}')
		return manager