UNITTEST_TEMPLATE = r"""import unittest
import requests


class Test{{ test_class_name }}(unittest.TestCase):

    def setUp(self):
        self.url = "{{ base_url | default('')}}"

    def test_{{ test_func_name }}(self):

        requests_data = {
            "path": "{{ path | default(None)}}",
            "method": "{{ method | default(None)}}",
            "headers": {{ headers | default(None)}},
            "params": {{ params | default(None)}},
            "json": {{ json | default(None)}},
            "data": {{ data | default(None)}},
        }
        requests_data["url"] = f"{self.url}{requests_data.pop('path')}"
        resp = requests.request(**requests_data) 
        print(f"{'status_code'.center(30, '=')}\n"
              f"{resp.status_code}")
        print(f"{'headers'.center(30, '=')}\n"
              f"{resp.headers}")
        print(f"{'body'.center(30, '=')}\n"
              f"{resp.text}")

    def tearDown(self):
        pass


if __name__ == '__main__':
    unittest.main()
"""

PYTEST_TEMPLATE = r"""import pytest
import requests


class Test{{test_class_name}}:

    def setup(self):
        self.url = "{{ base_url | default('')}}"

    def test_{{test_func_name}}(self):

        requests_data = {
            "path": "{{ path | default(None)}}",
            "method": "{{ method | default(None)}}",
            "headers": {{headers | default(None)}},
            "params": {{params | default(None)}},
            "json": {{json | default(None)}},
            "data": {{data | default(None)}},
        }
        requests_data["url"] = f"{self.url}{requests_data.pop('path')}"
        resp = requests.request(**requests_data)
        print(f"{'status_code'.center(30, '=')}\n"
              f"{resp.status_code}")
        print(f"{'headers'.center(30, '=')}\n"
              f"{resp.headers}")
        print(f"{'body'.center(30, '=')}\n"
              f"{resp.text}")



    def teardown(self):
        pass


if __name__ == '__main__':
    pytest.main(['-s', '-v'])
"""

REQUESTS_TEMPLATE = r"""import requests

url = "{{ base_url | default('')}}"
requests_data = {
    "path": "{{ path | default(None)}}",
    "method": "{{ method | default(None)}}",
    "headers": {{headers | default(None)}},
    "params": {{params | default(None)}},
    "json": {{json | default(None)}},
    "data": {{data | default(None)}},
}
requests_data["url"] = f"{url}{requests_data.pop('path')}"
resp = requests.request(**requests_data)
print(f"{'status_code'.center(30,'=')}\n"
      f"{resp.status_code}")
print(f"{'headers'.center(30,'=')}\n"
      f"{resp.headers}")
print(f"{'body'.center(30,'=')}\n"
      f"{resp.text}")
"""