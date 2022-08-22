# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['fxutils', 'fxutils.historyreader', 'fxutils.portfolio', 'fxutils.tools']

package_data = \
{'': ['*']}

install_requires = \
['pandas>=1.4.3,<2.0.0', 'requests>=2.28.1,<3.0.0']

extras_require = \
{':sys_platform == "windows"': ['MetaTrader5>=5.0.37,<6.0.0']}

setup_kwargs = {
    'name': 'fxutils',
    'version': '0.1.0',
    'description': 'Forex utilities for automatic trading',
    'long_description': None,
    'author': 'Xiaolei',
    'author_email': '26442779@qq.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': None,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'extras_require': extras_require,
    'python_requires': '>=3.9,<4.0',
}


setup(**setup_kwargs)
