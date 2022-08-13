# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['roboswag', 'roboswag.generate', 'roboswag.generate.models']

package_data = \
{'': ['*'], 'roboswag.generate': ['templates/*']}

install_requires = \
['Jinja2>=3.1.2,<4.0.0',
 'PyYAML>=6.0,<7.0',
 'black>=22.3.0,<23.0.0',
 'jsonschema>=4.5.1,<5.0.0',
 'openapi-spec-validator>=0.4.0,<0.5.0',
 'prance>=0.21.8,<0.22.0',
 'requests>=2.27.1,<3.0.0',
 'robotframework>=4.1',
 'urllib3>=1.26.9,<2.0.0']

entry_points = \
{'console_scripts': ['roboswag = roboswag:run_roboswag']}

setup_kwargs = {
    'name': 'roboswag',
    'version': '0.2.0',
    'description': 'Test framework for auto-generating libraries from OpenAPI specification file.',
    'long_description': "# Roboswag \n\n- [Introduction](#introduction)\n- [Installation](#installation)\n- [Usage](#usage)\n- [Limitations](#limitations)\n\n## Introduction\n\n:robot: Roboswag is a tool that automatically generates Python libraries out of your Swagger (OpenAPI specification \nfile). These libraries can be used to create tests with various payload content and its validation. It also supports \nresponse validation against schema and verification of different status codes.\n\n> **Note**\n>\n> The tool is in the ***Alpha*** state, which means it may be unstable and should be used at your own risk. Some \n> features may be broken and there are still many things to be developed. Happy testing!\n\nThe OpenAPI Specification (OAS) defines a standard, language-agnostic interface to RESTful APIs.\nClick [here for v3 documentation](https://swagger.io/specification/) and\n[here for v2 documentation](https://swagger.io/specification/v2).\n\n> Hosted on [GitHub](https://github.com/MarketSquare/roboswag). :medal_military:\n\n## Installation\n\n> **Note**\n>\n> The PyPI package will be released when Beta version is out.\n\nFirst, you need to install Roboswag, and there are currently 2 ways to do it:\n- you can clone the repository, go to the main `roboswag` directory and install the tool locally:\n\n```commandline\npip install .\n```\n\n- you can install the tool directly from GitHub's source code:\n\n```commandline\npip install -U git+https://github.com/MarketSquare/roboswag.git\n```\n\n## Usage\n\nRoboswag can be easily run from command line. To check if it's installed, run this to see the current version:\n\n```commandline\nroboswag -v\n```\n\nTo execute Roboswag with its full capabilities, run it with provided path to the Swagger (OpenAPI specification) file:\n\n```commandline\nroboswag -s <path_to_swagger>\n```\n\n> You can try out the tool using the example of swagger file located in `swaggers/petstore.json`.\n\nSuccessful execution should result in printing the information about generated files and a whole new directory (named \nby the value of `info.title` from your Swagger file) consisting of:\n- `endpoints` directory with files representing each `tag` as a class with methods representing its endpoints,\n- `models` directory with API models represented as Python classes,\n- `schemas` directory with every possible schema from your API as JSON file used for validating payload and responses. \n\nNow you can just create a test file, import desired endpoint and start automating the testing!\n\n## Limitations\n\nThe tool is already able to generate libraries but...\n- Not all fields from the swagger specification may be supported. This means that a specific file may break the tool \n  and flood the terminal with stack trace\n- Also, the support for Swagger V3 is not yet implemented\n- Authorization to access the API is not yet fully covered\n- There is not much to be configured here - it works always the same\n- There is no real documentation apart from this file\n- There are nearly no tests assuring this tool works correctly\n\nPlease be forgiving and submit an issue, if you struggle with something or just contact us on our\n[Slack channel](https://robotframework.slack.com/archives/C035KMZ2FGA). It's more than welcome also to support us by \ncode contribution! :keyboard:\n",
    'author': 'Mateusz Nojek',
    'author_email': 'matnojek@gmail.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://pypi.org/project/roboswag',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'entry_points': entry_points,
    'python_requires': '>=3.7,<4.0',
}


setup(**setup_kwargs)
