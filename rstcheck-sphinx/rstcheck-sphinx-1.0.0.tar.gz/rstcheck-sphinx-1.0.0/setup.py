# -*- coding: utf-8 -*-
from setuptools import setup

package_dir = \
{'': 'src'}

packages = \
['rstcheck_sphinx']

package_data = \
{'': ['*']}

extras_require = \
{':extra == "sphinx" or extra == "docs"': ['sphinx>=4.0,<6.0'],
 ':python_version < "3.8"': ['importlib-metadata>=1.6,<5.0'],
 'docs': ['sphinx-autobuild==2021.3.14',
          'm2r2>=0.3.2',
          'sphinx-rtd-theme<1',
          'sphinx-rtd-dark-mode>=1.2.4,<2.0.0',
          'sphinxcontrib-spelling>=7.3'],
 'testing': ['pytest>=6.0',
             'pytest-cov>=3.0',
             'coverage[toml]>=6.0',
             'coverage-conditional-plugin>=0.5',
             'pytest-sugar>=0.9.5',
             'pytest-randomly>=3.0',
             'pytest-mock>=3.7']}

setup_kwargs = {
    'name': 'rstcheck-sphinx',
    'version': '1.0.0',
    'description': 'Builder for the sphinx documentation generator to check the source with rstcheck.',
    'long_description': '===============\nrstcheck-sphinx\n===============\n\nBuilder extension for the sphinx documentation generator to check the source with rstcheck.\n\n**This project is under heavy development and not yet ready for use!**\n\n**The package on PyPI is empty.**\n',
    'author': 'Christian Riedel',
    'author_email': 'cielquan@protonmail.com',
    'maintainer': 'Christian Riedel',
    'maintainer_email': 'cielquan@protonmail.com',
    'url': 'https://github.com/rstcheck/rstcheck-sphinx',
    'package_dir': package_dir,
    'packages': packages,
    'package_data': package_data,
    'extras_require': extras_require,
    'python_requires': '>=3.7,<4.0',
}


setup(**setup_kwargs)
