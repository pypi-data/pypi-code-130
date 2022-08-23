# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['fastapi_gateway', 'fastapi_gateway.utils']

package_data = \
{'': ['*']}

install_requires = \
['aiohttp>=3.7.4,<4.0.0', 'ujson>=5.4.0,<6.0.0']

setup_kwargs = {
    'name': 'fastapi-gateway',
    'version': '0.0.2',
    'description': 'FastAPI gateway for microservices.',
    'long_description': '<p align="center">\n<img src="https://scrutinizer-ci.com/g/dotX12/fastapi-gateway/badges/quality-score.png?b=master" alt="https://scrutinizer-ci.com/g/dotX12/fastapi-gateway/">\n<img src="https://scrutinizer-ci.com/g/dotX12/fastapi-gateway/badges/code-intelligence.svg?b=master" alt="https://scrutinizer-ci.com/g/dotX12/fastapi-gateway/">\n<img src="https://scrutinizer-ci.com/g/dotX12/fastapi-gateway/badges/build.png?b=master" alt="https://scrutinizer-ci.com/g/dotX12/fastapi-gateway/">\n<img src="https://badge.fury.io/py/fastapi-gateway.svg" alt="https://badge.fury.io/py/fastapi-gateway">\n<img src="https://pepy.tech/badge/fastapi-gateway" alt="https://pepy.tech/project/fastapi-gateway">\n<img src="https://pepy.tech/badge/fastapi-gateway/month" alt="https://pepy.tech/project/fastapi-gateway">\n<img src="https://img.shields.io/github/license/dotX12/fastapi-gateway.svg" alt="https://github.com/dotX12/fastapi-gateway/blob/master/LICENSE">\n\n# ⚙️ fastapi-gateway is async single entry point for microservices.\n\n#### API Gateway performs many tasks: accepts, processes and distributes requests, controls traffic, monitors and controls access and security, caching, throttling.\n\nInitially, this project was created for myself, I needed to implement identification, authentication and authorization. In the future, there was a need to limit requests for each user on every endpoint, create API plans. There were a lot of microservices and to keep in each microservice the logic for limiting endpoints, security logic, logging etc. - meaningless. Therefore, all this functionality is located at a single entry point, which already implements all the necessary tasks with security, limiting, etc., while microservices now directly solve their tasks.\n\n## 💿 Installation\n\n```\npip install fastapi_gateway\n```\n\n## 💻 Example\n\n<details> \n<summary>\n<code>Example of use (long code)</code>\n</summary>\n<br>\n\n```python3\nfrom starlette import status\nfrom starlette.requests import Request\nfrom starlette.responses import Response\nfrom fastapi_gateway import route\nfrom fastapi import FastAPI\nfrom pydantic import BaseModel\nfrom fastapi import Depends\nfrom fastapi.security import APIKeyHeader\nfrom starlette import status\nfrom starlette.exceptions import HTTPException\n\napp = FastAPI(title=\'API Gateway\')\nSERVICE_URL = "http://microservice.localtest.me:8002"\n\nAPI_KEY_NAME = "x-api-key"\n\napi_key_header = APIKeyHeader(\n    name=API_KEY_NAME,\n    auto_error=False\n)\n\n\ndef check_api_key(key: str = Depends(api_key_header)):\n    if key:\n        return key\n    raise HTTPException(\n        status_code=status.HTTP_401_UNAUTHORIZED,\n        detail="You didn\'t pass the api key in the header! Header: x-api-key",\n    )\n\n\nclass FooModel(BaseModel):\n    example_int: int\n    example_str: str\n\n\n@route(\n    request_method=app.post,\n    service_url=SERVICE_URL,\n    gateway_path=\'/query_and_body_path/{path}\',\n    service_path=\'/v1/query_and_body_path/{path}\',\n    query_params=[\'query_int\', \'query_str\'],\n    body_params=[\'test_body\'],\n    status_code=status.HTTP_200_OK,\n    tags=[\'Query\', \'Body\', \'Path\'],\n    dependencies=[\n        Depends(check_api_key)\n    ],\n)\nasync def check_query_params_and_body(\n        path: int, query_int: int, query_str: str,\n        test_body: FooModel, request: Request, response: Response\n):\n    pass\n  ```\n\n</details>\n\n#### See more examples here:  \n##### [Tests and instructions for launch](../master/tests)  \n##### [Souce code Gateway](../master/tests/fastapi_gateway_service)  \n##### [Souce code Microservice #1](../master/tests/fastapi_microservice)  \n\n ## 🪛 How to use?\n\n- **request_method** -  is a callable (like app.get, app.post, foo_router.patch and so on.).  \n- **service_url** - the path to the endpoint on another service (like "https://microservice1.example.com").  \n- **service_path** - the path to the method in microservice (like "/v1/microservice/users").  \n- **gateway_path** - is the path to bind gateway.  \nFor example, your gateway api is located here - *https://gateway.example.com* and the path to endpoint (**gateway_path**) - "/users" then the full way to this method will be - *https://gateway.example.com/users*\n- **override_headers** - Boolean value allows you to return all the headlines that were created by microservice in gateway.  \n- **query_params** - used to extract query parameters from endpoint and transmission to microservice\n- **form_params** -  used to extract form model parameters from endpoint and transmission to microservice\n- **param body_params** - used to extract body model from endpoint and transmission to microservice\n\n⚠️ - **Be sure to transfer the name of the argument to the router, which is in the endpoint func!**  \n\n```\nquery_params - List[Query]\nbody_params - List[Body]\nform_params - List[File, Form]\n ```\n\n<details> \n<summary>\n<code>In more detail how to transmit body, form and query (photo)</code>\n</summary>\n<br>\n<img width="450" height="456" src="https://user-images.githubusercontent.com/64792903/130335866-82be1684-cd54-43d3-8e0e-4013176a352a.jpg">\n</details>\n',
    'author': 'dotX12',
    'author_email': None,
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://github.com/dotX12/fastapi-gateway',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.7,<4.0',
}


setup(**setup_kwargs)
