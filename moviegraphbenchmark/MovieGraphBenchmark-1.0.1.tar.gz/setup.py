# -*- coding: utf-8 -*-
from setuptools import setup

package_dir = \
{'': 'src'}

packages = \
['moviegraphbenchmark']

package_data = \
{'': ['*']}

install_requires = \
['pandas', 'pystow', 'requests', 'tqdm']

entry_points = \
{'console_scripts': ['moviegraphbenchmark = '
                     'moviegraphbenchmark.create_graph:create_graph_data']}

setup_kwargs = {
    'name': 'moviegraphbenchmark',
    'version': '1.0.1',
    'description': 'Benchmark datasets for Entity Resolution on Knowledge Graphs containing information about movies, tv shows and persons from IMDB,TMDB and TheTVDB',
    'long_description': None,
    'author': 'Daniel Obraczka',
    'author_email': 'obraczka@informatik.uni-leipzig.de',
    'maintainer': None,
    'maintainer_email': None,
    'url': None,
    'package_dir': package_dir,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'entry_points': entry_points,
    'python_requires': '>=3.7.1,<3.11',
}


setup(**setup_kwargs)
