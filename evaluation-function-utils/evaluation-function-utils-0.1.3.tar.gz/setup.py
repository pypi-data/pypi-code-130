# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['evaluation_function_utils']

package_data = \
{'': ['*']}

install_requires = \
['boto3>=1.24.38,<2.0.0', 'python-dotenv>=0.20.0,<0.21.0']

setup_kwargs = {
    'name': 'evaluation-function-utils',
    'version': '0.1.3',
    'description': 'Miscellaneous Utilities to be used by LambdaFeedback Evaluation Functions',
    'long_description': '# Evaluation Function Utilities\n\nPython package containing a range of utilities that might be used by some (but not all) evaluation functions on the LambdaFeedback platform. This package is pre-installed on the [BaseEvaluationFunctionLayer](https://github.com/lambda-feedback/BaseEvalutionFunctionLayer), to be utilised by individual functions to carry a range of common tasks:\n\n- Better error reporting\n- Schema checking\n- Input symbols (multiple ways of inputing the same answer)\n\n## Testing\nRun tests from the root dir with:\n```bash\npytest\n```\n\n*Useful flags:*\n- **-vv**: verbose output\n- **-rP**: show captured output of passed tests\n- **-rx**: show captured output of failed tests',
    'author': 'RabidSheep55',
    'author_email': 'rabidsheep55@gmail.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': '',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.7,<4.0',
}


setup(**setup_kwargs)
