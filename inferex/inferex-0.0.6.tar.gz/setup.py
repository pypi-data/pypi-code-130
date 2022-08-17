# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['inferex',
 'inferex.api',
 'inferex.decorator',
 'inferex.decorator.inferex',
 'inferex.deployments',
 'inferex.endpoints',
 'inferex.help',
 'inferex.io',
 'inferex.projects',
 'inferex.subapp',
 'inferex.template']

package_data = \
{'': ['*']}

install_requires = \
['Cerberus>=1.3.4,<2.0.0',
 'GitPython>=3.1.27,<4.0.0',
 'PyYAML>=6.0,<7.0',
 'Pygments>=2.12.0,<3.0.0',
 'click>=8.1.3,<9.0.0',
 'dirhash>=0.2.1,<0.3.0',
 'humanize>=4.1.0,<5.0.0',
 'requests-toolbelt>=0.9.1,<0.10.0',
 'requests>=2.28.0,<3.0.0',
 'tabulate>=0.8.9,<0.9.0',
 'tqdm>=4.64.0,<5.0.0',
 'yaspin>=2.1.0,<3.0.0']

entry_points = \
{'console_scripts': ['inferex = inferex.__main__:main']}

setup_kwargs = {
    'name': 'inferex',
    'version': '0.0.6',
    'description': 'Inferex CLI - Init, deploy and manage your projects on Inferex infrastructure',
    'long_description': '# Inferex CLI\n\nDeploy and manage your AI projects on Inferex infrastructure.\n\n[See our online documentation for a tutorial.](https://docs.inferex.com/)\n\n## Installation\n\n```bash\npip install inferex\n```\n\nYou can invoke "inferex --help" for a list of commands. Each command may have\nsubcommands, which can be called with "--help" as well.\n\nVersion 0.0.6:\n\n```bash\nUsage: inferex [OPTIONS] COMMAND [ARGS]...\n\n  Inferex CLI is a tool that enables AI companies to rapidly deploy pipelines.\n  Init, deploy, and manage your projects with Inferex. Invoke "inferex --help"\n  for a list of commands.\n\nOptions:\n  --version  Show the version and exit.\n  --help     Show this message and exit.\n\nCommands:\n  deploy      🚀 Deploy a project.\n  deployment  🌎 Manage Inferex deployments.\n  endpoints   📞 List endpoints for a deployment.\n  init        ✨ Initializes a new project.\n  login       🔑 Fetch api key via username & password authentication.\n  logs        📃 Get logs from Inferex deployments.\n  projects    📁 Manage Inferex projects.\n  reset       ❌ Deletes the token.json file created at login.\n```\n\n## CLI - Basic usage\n\n1. Create or navigate to the project folder you wish to deploy. You may copy an\n   example project folder from the examples folder ("face_detection",\n   "sentiment_analysis", etc). Each example has inferex.yaml, pipeline.py, and\n   requirements.txt files.\n\n1. Run the "inferex login" command to log in with your inferex account\n   and save your token locally.\n\n1. Run "inferex deploy". This will create a tar archive of your project folder\n   and send it to the server for processing.\n\nThat\'s it! `inferex deployments` will list your deployed projects and their URLs.\n',
    'author': 'Greg',
    'author_email': 'greg@inferex.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': None,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'entry_points': entry_points,
    'python_requires': '>=3.8,<4.0',
}


setup(**setup_kwargs)
