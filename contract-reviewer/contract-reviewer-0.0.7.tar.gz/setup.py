# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['contract_reviewer']

package_data = \
{'': ['*']}

install_requires = \
['datasets>=2.4.0,<3.0.0',
 'pdfminer.six>=20220524,<20220525',
 'spacy>=3.4.1,<4.0.0',
 'torch>=1.12.1,<2.0.0',
 'transformers>=4.21.1,<5.0.0']

entry_points = \
{'console_scripts': ['contract-reviewer = '
                     'contract_reviewer.contractreviewer:main']}

setup_kwargs = {
    'name': 'contract-reviewer',
    'version': '0.0.7',
    'description': 'Using NLP to tag contracts across 12 different fields',
    'long_description': None,
    'author': 'Alex-apostolo',
    'author_email': 'alex-apostolo@hotmail.com',
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
