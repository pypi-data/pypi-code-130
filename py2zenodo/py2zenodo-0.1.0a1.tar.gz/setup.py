# -*- coding: utf-8 -*-
from setuptools import setup

package_dir = \
{'': 'src'}

packages = \
['py2zenodo']

package_data = \
{'': ['*']}

install_requires = \
['requests>=2.28.1,<3.0.0', 'tqdm>=4.64.0,<5.0.0']

entry_points = \
{'console_scripts': ['py2zenodo = py2zenodo.cli:main']}

setup_kwargs = {
    'name': 'py2zenodo',
    'version': '0.1.0a1',
    'description': 'A Python wrapper for Zenodo REST API.',
    'long_description': '# py2zenodo\nA Python wrapper for Zenodo REST API\n\n## Installation\n\nWe use [Poetry](https://python-poetry.org/) to manage this package.\nTo install py2zenodo, run the following at the project root directory\n\n```bash\npoetry install\n```\n',
    'author': 'RemyLau',
    'author_email': 'remylau961@gmail.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://github.com/RemyLau/py2zenodo',
    'package_dir': package_dir,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'entry_points': entry_points,
    'python_requires': '>=3.8,<4.0',
}


setup(**setup_kwargs)
