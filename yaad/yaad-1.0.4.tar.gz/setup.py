# -*- coding: utf-8 -*-
from setuptools import setup

package_dir = \
{'': 'src'}

packages = \
['yaad']

package_data = \
{'': ['*']}

setup_kwargs = {
    'name': 'yaad',
    'version': '1.0.4',
    'description': 'Yet Another Attribute Dict',
    'long_description': '\n# yaad\n\nYet Another Attribute Dictionary\n',
    'author': 'Daniel Sullivan',
    'author_email': 'mumblepins@users.noreply.github.com',
    'maintainer': 'None',
    'maintainer_email': 'None',
    'url': 'https://github.com/mumblepins/yaad',
    'package_dir': package_dir,
    'packages': packages,
    'package_data': package_data,
    'python_requires': '>=3.7',
}


setup(**setup_kwargs)
