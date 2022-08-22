# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['mkrst', 'mkrst_themes']

package_data = \
{'': ['*'],
 'mkrst_themes': ['classic/fonts/*',
                  'classic/html/*',
                  'classic/odt/*',
                  'classic/pdf/*',
                  'default/fonts/*',
                  'default/html/*',
                  'default/odt/*',
                  'default/pdf/*',
                  'overclock/fonts/*',
                  'overclock/html/*',
                  'overclock/odt/*',
                  'overclock/pdf/*']}

install_requires = \
['docutils>=0.10', 'rst2pdf>=0.99,<0.100']

entry_points = \
{'console_scripts': ['mkrst = mkrst:main']}

setup_kwargs = {
    'name': '2lazy2rest',
    'version': '0.1.1',
    'description': 'Effortless generation of PDF, HTML & ODT documents from RST (ReStructuredText)',
    'long_description': None,
    'author': 'fdev31',
    'author_email': 'fdev31@gmail.com',
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
