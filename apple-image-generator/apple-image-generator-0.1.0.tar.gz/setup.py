# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['apple_image_generator']

package_data = \
{'': ['*']}

install_requires = \
['Pillow>=9.2.0,<10.0.0', 'typer>=0.6.1,<0.7.0']

entry_points = \
{'console_scripts': ['icons = apple_image_generator.main:run']}

setup_kwargs = {
    'name': 'apple-image-generator',
    'version': '0.1.0',
    'description': 'Generate images according Apple applications needs',
    'long_description': 'apple-image-generator\n\n\n- create Content.json\n- create all size for multi-platform app development\n',
    'author': 'Leonard TAVAE',
    'author_email': 'leonard.tavae@administration.gov.pf',
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
