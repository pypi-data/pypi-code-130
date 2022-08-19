# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['codebox']

package_data = \
{'': ['*']}

install_requires = \
['Jinja2>=3.1.2,<4.0.0', 'PyYAML>=6.0,<7.0']

extras_require = \
{':extra == "docs"': ['sphinx-rtd-theme>=1.0.0,<2.0.0',
                      'sphinxcontrib-napoleon>=0.7,<0.8']}

setup_kwargs = {
    'name': 'codebox',
    'version': '1.1.0',
    'description': 'A collection of Python utility modules',
    'long_description': 'codebox - Python tools collection.\n-----------------------------------------\n\nInstallation\n==================\n\n.. code-block:: bash\n\n    pip install codebox\n\n\nDocumentation\n=============\n\nhttps://wils0ns.github.io/codebox/\n',
    'author': 'Wilson Santos',
    'author_email': 'wilson@codeminus.org',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://github.com/wils0ns/codebox',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'extras_require': extras_require,
    'python_requires': '>=3.8,<4.0',
}


setup(**setup_kwargs)
