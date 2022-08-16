# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['flask_botox']

package_data = \
{'': ['*']}

install_requires = \
['Flask>=2.1.0,<3.0.0', 'boto3>=1.24.49,<2.0.0']

setup_kwargs = {
    'name': 'flask-botox',
    'version': '0.1.1',
    'description': 'Flask extension that ties boto3 clients and resources to the application context.',
    'long_description': '# flask-botox\n\nFlask extension that ties [boto3](https://github.com/boto/boto3) connectors to the application context.\nTo be used with Python 3.7+.\n\n## Install\n\n* Via `pip`:\n    ```bash\n    $ pip install flask-botox\n    ```\n\n* Locally with [Poetry](https://python-poetry.org) for development purposes:\n    ```bash\n    $ git clone https://github.com/jperras/flask-botox.git\n    $ cd flask-botox\n    $ poetry install\n    ```\n\n## How-to\n\nThe main class `flask_botox.Boto3` takes a Flask application as its contructor\'s parameter:\n\n```python\nfrom flask import Flask\nfrom flask_botox import Boto3\napp = Flask(__name__)\napp.config["BOTOX_SERVICES"] = ["s3", "ses", "sqs"]\n\nbotox = Boto3(app)\n```\n\nThe application factory pattern for extensions is also valid:\n\n```python\nfrom flask import Flask\nfrom flask_botox import Boto3\n\nbotox = Boto3()\n\napp = Flask(__name__)\napp.config["BOTOX_SERVICES"] = ["s3", "ses", "sqs"]\n\nbotox.init_app(app)\n\n```\n\n\nThen `boto3`\'s clients and resources will be available as properties within the application context:\n\n```python\n>>> with app.app_context():\n        print(botox.clients)\n        print(botox.resources)\n{\'s3\': <botocore.client.S3 object at 0x..>}\n{\'s3\': s3.ServiceResource()}\n```\n\n## Configuration\n\nFlask-botox uses several keys from a Flask configuration objects to customize its behaviour. Any of the `AWS_*` keys are _not_ required; if they are not specified, then the usual `boto3` configuration parameter rules will apply.\n\n- `AWS_ACCESS_KEY_ID` & `AWS_SECRET_ACCESS_KEY` : The AWS credentials. Note that it\'s not a good idea to put your secret access key in a configuration file, but it can be useful for e.g. testing purposes.\n- `AWS_DEFAULT_REGION` : The region, e.g. `us-east-1`, for the `boto3` AWS services.\n- `AWS_PROFILE` : The AWS nanmed profile to use, if one is desired.\n- `BOTOX_SERVICES` : The name of the AWS resources you want to use, e.g. `[\'sqs\', \'s3\', \'ses\']`.\n- `BOTOX_OPTIONAL_PARAMS` : Useful if you need to pass additional parameters to the client/resource connections, e.g. a custom `endpoint_url` for a particular service. The format is a `dict` where the top-level keys are the name of the services you\'re using and for each the value is a `dict` containing to keys `args` (contains the parameters as `tuple`) and `kwargs` (contains the parameters as a `dict` when they should be passed as keyword arguments).\n',
    'author': 'Joel Perras',
    'author_email': 'joel@nerderati.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://github.com/jperras/flask-botox',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.7,<4',
}


setup(**setup_kwargs)
