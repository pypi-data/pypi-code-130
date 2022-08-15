# -*- coding: utf-8 -*-
from setuptools import setup

package_dir = \
{'': 'src'}

packages = \
['selenium_setup']

package_data = \
{'': ['*']}

install_requires = \
['httpx', 'rich', 'typer[all]', 'xmltodict']

entry_points = \
{'console_scripts': ['selenium_setup = selenium_setup:main']}

setup_kwargs = {
    'name': 'selenium-setup',
    'version': '0.0.4',
    'description': '',
    'long_description': "# selenium_setup\n\n[![pypi](https://img.shields.io/pypi/v/selenium_setup?color=%2334D058)](https://pypi.org/project/selenium_setup/)\n\n## install\n\n```shell\npip install selenium_setup\n```\n\n## CLI\n\n### download default version driver and unzip to CWD  \n\n```shell\npython -m selenium_setup\n```\n\n```console\nchrome ver = '104.0.5112.79'\nlinux64\ndownloading to: /path/to/chromedriver_linux64--104.0.5112.79.zip\n100% ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━ 7.1/7.1 MB 200.8 kB/s\n```\n\n### list 10 links of some latest versions\n\n```shell\npython -m selenium_setup --list\n```\n\n```console\nchrome linux64:\n  105.0.5195.19  https://chromedriver.storage.googleapis.com/105.0.5195.19/chromedriver_linux64.zip\n  104.0.5112.79  https://chromedriver.storage.googleapis.com/104.0.5112.79/chromedriver_linux64.zip\n  103.0.5060.134 https://chromedriver.storage.googleapis.com/103.0.5060.134/chromedriver_linux64.zip\n  102.0.5005.61  https://chromedriver.storage.googleapis.com/102.0.5005.61/chromedriver_linux64.zip\n  101.0.4951.41  https://chromedriver.storage.googleapis.com/101.0.4951.41/chromedriver_linux64.zip\n  100.0.4896.60  https://chromedriver.storage.googleapis.com/100.0.4896.60/chromedriver_linux64.zip\n  99.0.4844.51   https://chromedriver.storage.googleapis.com/99.0.4844.51/chromedriver_linux64.zip\n  98.0.4758.102  https://chromedriver.storage.googleapis.com/98.0.4758.102/chromedriver_linux64.zip\n  97.0.4692.71   https://chromedriver.storage.googleapis.com/97.0.4692.71/chromedriver_linux64.zip\n  96.0.4664.45   https://chromedriver.storage.googleapis.com/96.0.4664.45/chromedriver_linux64.zip\n```\n\n### download specific version\n\n```shell\npython -m selenium_setup --ver ...\n```\n",
    'author': ' ',
    'author_email': None,
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://github.com/m9810223/selenium_setup',
    'package_dir': package_dir,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'entry_points': entry_points,
    'python_requires': '>=3.7,<4',
}


setup(**setup_kwargs)
