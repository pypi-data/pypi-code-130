import json

import jinja2
import requests
from loguru import logger

from .templates import UNITTEST_TEMPLATE, PYTEST_TEMPLATE, REQUESTS_TEMPLATE
from .utils import build_test_name_from_path, replace_json_data_to_python_obj

CLIENT = requests.session()


class Yapi2Requests:

    def __init__(self, yapi_base_url, username, password, project_id):
        self.yapi_base_url = yapi_base_url
        self.login_yapi(username, password)
        self.project_id = project_id
        self.requests_des = None
        self.requests_base_url = None

    def login_yapi(self, username, password):
        """
        yapi登录接口
        """
        path = f"/api/user/login_by_ldap"
        url = f'{self.yapi_base_url}{path}'

        json_body = {
            "email": username,
            "password": password
        }

        resp = CLIENT.post(url, json=json_body)
        try:
            assert resp.status_code == 200
            assert resp.json()['errcode'] == 0
            assert "logout success" in resp.json()['errmsg']
        except Exception as msg:
            raise Exception(f"yapi平台登录失败，请检查账号和密码\n"
                            f"登录错误信息：{resp.text}")
        logger.info("yapi平台登录成功")

    def get_api_doc_from_id(self, api_id):
        """
        yapi查询接口文档接口
        """
        path = "/api/interface/get"
        url = f"{self.yapi_base_url}{path}"
        params = {
            "id": api_id
        }
        resp = CLIENT.get(url, params=params)
        try:
            assert resp.status_code == 200
            assert resp.json()['errcode'] == 0
            assert resp.json()['errmsg'] == "成功！"
        except Exception as msg:
            raise Exception(f"找不到相关的api，请检查api_id的正确性\n"
                            f"错误信息：{resp.text}")
        logger.info(f"===找到api_id:{api_id} 相关api_doc===\n"
                    f"{resp.text}")
        return resp.json()

    def get_requests_kwargs_from_api_id(self, api_id):
        api_doc = self.get_api_doc_from_id(api_id=api_id)
        requests_kwargs = self.parse_api_doc(api_doc=api_doc)
        return requests_kwargs

    def parse_api_doc(self, api_doc):
        api_doc_data = api_doc.get("data")
        api_name = api_doc_data.get("title")
        logger.info(f"api_name: {api_name}")

        yapi_api_id = api_doc_data.get("_id")
        logger.info(f"yapi_api_id: {yapi_api_id}")

        path = api_doc_data.get('path')
        logger.info(f"path: {path}")

        method = api_doc_data.get('method')
        logger.info(f"method: {method}")

        req_params = api_doc_data.get("req_params", list())
        req_body_form = api_doc_data.get("req_body_form", list())
        req_headers = api_doc_data.get("req_headers", list())
        req_query = api_doc_data.get("req_query", list())
        req_body_type = api_doc_data.get("req_body_type")
        req_body_other = api_doc_data.get("req_body_other", dict())
        if req_body_other:
            try:
                req_body_other = json.loads(req_body_other)
            except Exception as e:
                logger.warning(f"req_body_other反序列化失败")

        headers = self.parse_api_doc_parameters(req_headers) or None
        logger.info(f"headers: {headers}")

        req_params = self.parse_api_doc_parameters(req_params)
        # logger.info(f"req_params: {req_params}")

        params = self.parse_api_doc_parameters(req_query)
        params = params.update(req_params) or None
        logger.info(f"params: {params}")

        json_body = self.parse_api_doc_json_desc(req_body_other) or None
        logger.info(f"json_body:\n"
                    f"{json.dumps(json_body, ensure_ascii=False)}")

        form_body = self.parse_api_doc_parameters(req_body_form) or None
        logger.info(f"form_body:\n"
                    f"{json.dumps(form_body, ensure_ascii=False)}")

        requests_kwargs = {
            "path": path,
            "method": method,
            "headers": headers,
            "params": params,
            "json": json_body,
            "data": form_body
        }
        requests_kwargs = {k: v for k, v in requests_kwargs.items() if v}

        self.requests_des = requests_kwargs
        logger.info(f"requests_kwargs: \n"
                    f"{json.dumps(requests_kwargs, ensure_ascii=False)}")
        return requests_kwargs

    def parse_api_doc_parameters(self, data):
        rebuild_data = {}
        for _value in data:
            name = _value.get("name")
            value = _value.get("value")
            desc = _value.get("desc")
            rebuild_data[name] = value or desc
        return rebuild_data

    def parse_api_doc_json_desc(self, json_desc, data=None):

        data_type = json_desc.get('type')  # object or array
        properties = json_desc.get('properties')
        array_items = json_desc.get('items')

        if properties:
            json_desc.pop('properties')

        for kj1 in list(json_desc.keys()):
            if kj1 in ["required", "title", "description", "$$ref", "type"]:
                json_desc.pop(kj1)

        # if 'required' in json_desc:
        #     json_desc.pop('required')
        #
        # if 'title' in json_desc:
        #     json_desc.pop('title')
        #
        # if 'description' in json_desc:
        #     json_desc.pop('description')
        #
        # if '$$ref' in json_desc:
        #     json_desc.pop('$$ref')
        #
        # if 'type' in json_desc:
        #     json_desc.pop('type')

        if data is None:
            if data_type == 'object':
                data = {}

            elif data_type == 'array':
                data = [json_desc.get('items')]

        if properties:
            for key, value in properties.items():
                value_type = value.get("type")
                if value_type not in ["object", "array"]:
                    data[key] = value.get("description")
                elif value_type == "object":
                    data[key] = value
                    # 使用python字典的内存指向，递归解析, 清洗数据
                    self.parse_api_doc_json_desc(json_desc=value, data=value)
                elif value_type == "array":
                    # data[key] = value
                    data[key] = [value.get('items')]
                    self.parse_api_doc_json_desc(json_desc=value, data=value)

        if array_items:
            self.parse_api_doc_json_desc(json_desc=array_items, data=array_items)

        return data

    def generate_requests_with_template(self, api_id, template, file_name=None):
        # 获取yapi接口文档数据源
        api_doc = self.get_api_doc_from_id(api_id=api_id)
        # 解析yapi接口文档，生成requests数据结构
        requests_des = self.parse_api_doc(api_doc)
        # 构建请求中的base_url
        if self.requests_base_url:
            requests_des["base_url"] = self.requests_base_url
        # 构建测试类和测试方法名
        requests_des["test_class_name"], requests_des["test_func_name"] = build_test_name_from_path(
            requests_des["path"])
        # 序列化后，改变json字符串中的特殊值，特殊值映射python的对象null->None, true->True , false->False
        replace_json_data_to_python_obj(requests_des)
        # 生成测试模板
        template = jinja2.Template(template)
        content = template.render(requests_des)
        file_name = file_name or f"test_{requests_des['test_func_name']}.py"
        with open(file_name, 'w', encoding='utf-8') as f:
            f.write(content)

    def generate_requests(self, api_id):
        return self.generate_requests_with_template(api_id, REQUESTS_TEMPLATE)

    def generate_requests_with_unittest(self, api_id):
        return self.generate_requests_with_template(api_id, UNITTEST_TEMPLATE)

    def generate_requests_with_pytest(self, api_id):
        return self.generate_requests_with_template(api_id, PYTEST_TEMPLATE)

    def generate_requests_with_unittest_data_driven(self):
        pass

    def generate_requests_with_pytest_data_driven(self):
        pass

    def generate_http(self):
        pass

    def generate_httprunner_template(self):
        pass
