# -*- coding: utf-8 -*-
from setuptools import setup

package_dir = \
{'': 'cmdtools'}

packages = \
['callback',
 'cmdtools',
 'cmdtools.callback',
 'cmdtools.converter',
 'cmdtools.ext',
 'cmdtools.utils',
 'converter',
 'ext',
 'utils']

package_data = \
{'': ['*']}

setup_kwargs = {
    'name': 'cmdtools-py',
    'version': '3.0.1.post1',
    'description': 'A (not quite) flexible command framework',
    'long_description': '<div id="headline" align="center">\n  <h1>cmdtools</h1>\n  <p>A (not quite) flexible command framework.</p>\n  <a href="https://github.com/HugeBrain16/cmdtools/actions/workflows/python-package.yml">\n    <img src="https://github.com/HugeBrain16/cmdtools/actions/workflows/python-package.yml/badge.svg" alt="tests"></img>\n  </a>\n  <a href="https://pypi.org/project/cmdtools-py">\n    <img src="https://img.shields.io/pypi/dm/cmdtools-py" alt="downloads"></img>\n    <img src="https://badge.fury.io/py/cmdtools-py.svg" alt="PyPI version"></img>\n    <img src="https://img.shields.io/pypi/pyversions/cmdtools-py" alt="Python version"></img>\n  </a>\n  <a href="https://codecov.io/gh/HugeBrain16/cmdtools">\n    <img src="https://codecov.io/gh/HugeBrain16/cmdtools/branch/main/graph/badge.svg?token=mynvRn223H"/>\n  </a>\n  <a href=\'https://cmdtools-py.readthedocs.io/en/latest/?badge=latest\'>\n    <img src=\'https://readthedocs.org/projects/cmdtools-py/badge/?version=latest\' alt=\'Documentation Status\' />\n  </a>\n</div>\n\n## Installation\n\n```\npip install --upgrade cmdtools-py\n```\ninstall latest commit from GitHub  \n```\npip install git+https://github.com/HugeBrain16/cmdtools.git\n```\n\n### Basic example\n\n```py\nimport asyncio\nimport cmdtools\n\n@cmdtools.callback.add_option("message")\ndef send(ctx):\n    print(ctx.options.message)\n\n@send.error\ndef error_send(ctx):\n  if isinstance(ctx.error, cmdtools.NotEnoughArgumentError):\n    if ctx.error.option == "message":\n      print("Message is required!")\n\ncmd = cmdtools.Cmd(\'/send hello\')\nasyncio.run(cmdtools.execute(cmd, send))\n```\n\n## Links\n\nPyPI project: https://pypi.org/project/cmdtools-py  \nSource code: https://github.com/HugeBrain16/cmdtools  \nIssues tracker: https://github.com/HugeBrain16/cmdtools/issues  \nDocumentation: https://cmdtools-py.readthedocs.io/en/latest\n',
    'author': 'HugeBrain16',
    'author_email': 'joshtuck373@gmail.com',
    'maintainer': 'HugeBrain16',
    'maintainer_email': 'joshtuck373@gmail.com',
    'url': 'https://github.com/HugeBrain16/cmdtools',
    'package_dir': package_dir,
    'packages': packages,
    'package_data': package_data,
    'python_requires': '>=3.7,<4.0',
}


setup(**setup_kwargs)
