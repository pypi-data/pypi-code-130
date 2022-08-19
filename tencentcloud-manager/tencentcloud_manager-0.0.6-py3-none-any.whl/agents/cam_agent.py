import json
import time
from typing import List, Dict
from tencentcloud.cam.v20190116 import cam_client
from tencentcloud.cam.v20190116 import models

class CamAgent:

	def __init__(self, cred, region):
		self._client = cam_client.CamClient(cred, region)
		self._last_resp = None
		self._last_data = None		

	def get_account_summary(self):
		# 列出用户关联的策略（包括随组关联）
		# 例：
		# {"Policies": 112, "Roles": 39, "Idps": 1, "User": 330, "Group": 30, "Member": 202, "RequestId": "5194ef98-5a42-4991-a559-b30dd505a251"}
		req = models.GetAccountSummaryRequest()
		resp = self._client.GetAccountSummary(req)
		self._last_resp = resp
		return self._last_resp
	
	def list_all_users(self):
		# 获取所有子用户信息
		# 一次性获取全量，可能会请求多次
		req = models.ListUsersRequest()
		resp = self._client.ListUsers(req)
		resp_json = json.loads(resp.to_json_string())
		request_id = resp_json['RequestId']
		data_json = resp_json['Data']
		self._last_resp = resp_json
		self._last_data = data_json
		return self._last_resp

	def get_user(self, name):
		# 获取子用户详细信息
		# 不适用于协作者的Name！！！
		req = models.GetUserRequest()
		req.Name = name
		resp = self._client.GetUser(req)
		resp_json = json.loads(resp.to_json_string())
		self._last_resp = resp_json
		return self._last_resp

	def list_all_collaborators(self):
		# 获取所有协作者
		# 一次性获取全量，可能会请求多次
		req = models.ListCollaboratorsRequest()
		resp = self._client.ListCollaborators(req)
		resp_json = json.loads(resp.to_json_string())
		data_json = resp_json['Data']
		self._last_resp = resp_json
		self._last_data = data_json
		return self._last_resp

	def list_all_roles(self):
		# 获取所有角色
		# 一次性获取全量，可能会请求多次
		raise 'no implement'

	def list_all_policies(self, keyword=None) -> List[Dict]:
		# 获取所有策略
		# 一次性获取全量，可能会请求多次
		page = 1
		max_page = 200
		num_per_page = 20
		all_policy_list = []
		while page < max_page:
			req = models.ListPoliciesRequest()
			req.Rp = num_per_page
			req.page = page
			if keyword:
				req.Keyword = keyword
			resp = self._client.ListPolicies(req)
			resp_json = json.loads(resp.to_json_string())
			resp_policy_list = resp_json['List']
			all_policy_list += resp_policy_list
			if len(resp_policy_list) < num_per_page:
				break
			else:
				page += 1
		self._last_data = all_policy_list
		return all_policy_list

	def get_policy(self, policy_id):
		# 获取策略详情
		req = models.GetPolicyRequest()
		req.PolicyId = policy_id
		resp = self._client.GetPolicy(req)
		resp_json = json.loads(resp.to_json_string())
		self._last_resp = resp_json
		return self._last_resp

	def list_all_groups(self):
		# 列出所有用户组
		# 一次性获取全量，可能会请求多次
		"""
		{
		  "Response": {
		    "TotalNum": 2,
		    "GroupInfo": [
		      {
		        "GroupId": 2021,
		        "GroupName": "test2",
		        "CreateTime": "2019-04-03 15:15:18",
		        "Remark": "test2"
		      },
		      {
		        "GroupId": 2020,
		        "GroupName": "test1",
		        "CreateTime": "2019-04-03 15:11:34",
		        "Remark": "test2"
		      }
		    ],
		    "RequestId": "dbb91d87-5e3f-42b4-8cc9-ad9f16600370"
		  }
		}
		"""
		all_group_list = []
		has_next = True
		page = 1
		num_per_page = 200
		while has_next:
			req = models.ListGroupsRequest()
			req.Page = page
			req.Rp = num_per_page
			resp = self._client.ListGroups(req)
			resp_json = json.loads(resp.to_json_string())
			data_json = resp_json['GroupInfo']
			if data_json:
				all_group_list += data_json
			if len(data_json) >= num_per_page:
				page += 1
				has_next = True
			else:
				has_next = False
		self._last_data = all_group_list
		return self._last_data

	def list_group_policies(self, group_ids, keyword=None):
		# 列出用户组的策略列表
		group_id_to_policy_list = []
		for index, group_id in enumerate(group_ids):
			has_next = True
			page = 1
			num_per_page = 200
			group_id_policy_list = []
			while has_next:
				req = models.ListAttachedGroupPoliciesRequest()
				req.TargetGroupId = group_id
				req.Page = page
				req.Rp = num_per_page
				if keyword:
					req.Keyword = keyword
				resp = self._client.ListAttachedGroupPolicies(req)
				resp_json = json.loads(resp.to_json_string())
				data_json = resp_json['List']
				if data_json:
					group_id_policy_list += data_json
				# print('progress = {} / {}'.format(index, len(group_ids)))
				if len(data_json) >= num_per_page:
					page += 1
					has_next = True
				else:
					has_next = False
			group_id_to_policy_list.append({group_id: group_id_policy_list})
		self._last_data = group_id_to_policy_list
		return self._last_data

	def list_group_for_users(self, uins: list):
		# 列出用户关联的用户组
		# 一次性获取全量，可能会请求多次
		uin_to_group_list = []
		for index, uin in enumerate(uins):
			req = models.ListGroupsForUserRequest()
			req.SubUin = uin
			resp = self._client.ListGroupsForUser(req)
			resp_json = json.loads(resp.to_json_string())
			data_json = resp_json
			uin_to_group_list.append({uin: data_json})
			# print('progress = {} / {}'.format(index, len(uins)))
		self._last_data = uin_to_group_list
		return self._last_data

	def list_policy_for_users(self, uins: list):
		# 列出用户关联的授权策略（不包含随组关联的策略）
		# 一次性获取全量，可能会请求多次
		"""
		{'AddTime': '2019-06-20 15:46:48',
                  'CreateMode': 2,
                  'Deactived': 0,
                  'DeactivedDetail': [],
                  'OperateOwnerUin': None,
                  'OperateUin': None,
                  'OperateUinType': None,
                  'PolicyId': 21505287,
                  'PolicyName': 'QcloudOceanusFullAccess',
                  'PolicyType': '',
                  'Remark': '流计算（Oceanus）全读写访问权限'},
		"""
		uin_to_policy_list = []
		for index, uin in enumerate(uins):
			has_next = True
			page = 1
			num_per_page = 200
			uin_policy_list = []
			while has_next:
				req = models.ListAttachedUserPoliciesRequest()
				req.TargetUin = uin
				req.Page = page
				req.Rp = num_per_page
				resp = self._client.ListAttachedUserPolicies(req)
				resp_json = json.loads(resp.to_json_string())
				data_json = resp_json['List']
				if data_json:
					uin_policy_list += data_json
				# print('progress = {} / {}'.format(index, len(uins)))
				if len(data_json) >= num_per_page:
					page += 1
					has_next = True
				else:
					has_next = False
			uin_to_policy_list.append({uin: uin_policy_list})
		self._last_data = uin_to_policy_list
		return self._last_data

	def list_policy_num_for_users(self, uins: list):
		# 列出用户关联的授权策略数量（不包含随组关联的策略数量）
		# 一次性获取全量，可能会请求多次
		uin_to_policy_num_list = []
		for index, uin in enumerate(uins):
			req = models.ListAttachedUserPoliciesRequest()
			req.TargetUin = uin
			req.Page = 1
			req.Rp = 200
			resp = self._client.ListAttachedUserPolicies(req)
			resp_json = json.loads(resp.to_json_string())
			total_num = resp_json['TotalNum']
			uin_to_policy_num_list.append({uin: total_num})
			print('progress = {} / {}'.format(index, len(uins)))
		self._last_data = uin_to_policy_num_list
		return self._last_data

	def find_out_direct_policy_users(self, uins):
		# 列出直接关联授权策略的用户（不包含随组关联的策略）
		# 判断规则是list_policy_num_for_users的数量大于0
		policy_num_for_users = self.list_policy_num_for_users(uins)
		self._last_data = [list(item.keys())[0] for item in policy_num_for_users if list(item.values())[0] > 0]
		return self._last_data

	def list_all_policy_for_users(self, uins):
		# 列出用户关联的策略（包括随组关联）
		# 一次性获取全量，可能会请求多次
		uin_to_all_policy_list = []
		sec = 0
		for index, uin in enumerate(uins):
			has_next = True
			page = 1
			num_per_page = 200
			uin_all_policy_list = []
			while has_next:
				req = models.ListAttachedUserAllPoliciesRequest()
				req.TargetUin = uin
				req.Page = page
				req.Rp = num_per_page
				req.AttachType = 0
				resp = self._client.ListAttachedUserAllPolicies(req)
				resp_json = json.loads(resp.to_json_string())
				data_json = resp_json['PolicyList']
				if data_json:
					uin_all_policy_list += data_json
				print('progress = {} / {}'.format(index, len(uins)))
				if len(data_json) >= num_per_page:
					page += 1
					has_next = True
				else:
					has_next = False
				sec += 1
				print(sec / 5)
				if sec % 5 == 0:
					time.sleep(1)
			uin_to_all_policy_list.append({uin: uin_all_policy_list})
		self._last_data = uin_to_all_policy_list
		return self._last_data

	def list_all_policy_num_for_users(self, uins: list):
		# 列出用户关联的授权策略数量（不包含随组关联的策略数量）
		# 一次性获取全量，可能会请求多次
		uin_to_all_policy_num_list = []
		for index, uin in enumerate(uins):
			req = models.ListAttachedUserAllPoliciesRequest()
			req.TargetUin = uin
			req.Page = 1
			req.Rp = 200
			req.AttachType = 0
			resp = self._client.ListAttachedUserAllPolicies(req)
			resp_json = json.loads(resp.to_json_string())
			print(resp_json)
			total_num = resp_json['TotalNum']
			uin_to_all_policy_num_list.append({uin: total_num})
			# print('progress = {} / {}'.format(index, len(uins)))
		self._last_data = uin_to_all_policy_num_list
		return self._last_data
