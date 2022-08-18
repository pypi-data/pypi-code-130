# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['lucupy',
 'lucupy.decorators',
 'lucupy.helpers',
 'lucupy.minimodel',
 'lucupy.observatory.abstract',
 'lucupy.observatory.gemini',
 'lucupy.output',
 'lucupy.sky',
 'lucupy.timeutils',
 'lucupy.types']

package_data = \
{'': ['*']}

install_requires = \
['astropy>=5.1,<6.0', 'pytz>=2022.2,<2023.0']

setup_kwargs = {
    'name': 'lucupy',
    'version': '0.1.1',
    'description': 'A striped down version of the lucuma core in Python for Schedule',
    'long_description': '',
    'author': 'Sergio Troncoso',
    'author_email': 'sergio.troncoso@noirlab.edu',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://github.com/stroncod/lucupy',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.10,<4.0',
}


setup(**setup_kwargs)
