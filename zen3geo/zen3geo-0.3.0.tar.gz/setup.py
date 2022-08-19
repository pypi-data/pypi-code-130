# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['zen3geo', 'zen3geo.datapipes', 'zen3geo.tests']

package_data = \
{'': ['*']}

install_requires = \
['rioxarray>=0.10.0', 'torchdata>=0.4.0']

extras_require = \
{'docs': ['datashader>=0.14.0',
          'pyogrio[geopandas]>=0.4.0',
          'spatialpandas>=0.4.0',
          'xbatcher>=0.1.0',
          'graphviz',
          'jupyter-book',
          'matplotlib',
          'planetary-computer',
          'pystac'],
 'raster': ['xbatcher>=0.1.0'],
 'spatial': ['datashader>=0.14.0', 'spatialpandas>=0.4.0'],
 'vector': ['pyogrio[geopandas]>=0.4.0']}

setup_kwargs = {
    'name': 'zen3geo',
    'version': '0.3.0',
    'description': "The 🌏 data science library you've been waiting for~",
    'long_description': "# zen3geo\n\nThe 🌏 data science library you've been waiting for~\n\n> 君の前前前世から僕は 君を探しはじめたよ\n>\n> Since your past life, I have been searching for you\n\n## 公案\n\n```\nGeography is difficult, but easy it can also be\nDeep Learning, you hope, has an answer to all\nToo this, too that, where to though, where to?\nLook out, sense within, and now you must know\n```\n\n## Installation\n\nTo install the development version from GitHub, do:\n\n    pip install git+https://github.com/weiji14/zen3geo.git\n\nOr the stable version from [PyPI](https://pypi.org/project/zen3geo):\n\n    pip install zen3geo\n\nMore detailed instructions at https://zen3geo.readthedocs.io/en/latest/#installation\n",
    'author': 'Wei Ji',
    'author_email': '23487320+weiji14@users.noreply.github.com',
    'maintainer': 'None',
    'maintainer_email': 'None',
    'url': 'None',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'extras_require': extras_require,
    'python_requires': '>=3.8,<3.12',
}


setup(**setup_kwargs)
