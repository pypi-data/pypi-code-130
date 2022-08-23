# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['tailors_trainer', 'tailors_trainer.fast']

package_data = \
{'': ['*']}

install_requires = \
['demjson3',
 'hao>=3.7.0',
 'lmdb',
 'rich>=12.4.4,<13.0.0',
 'rocksdb3',
 'tailors',
 'tensorboard>=2.10.0,<3.0.0',
 'torch-optimizer>=0.3.0,<0.4.0',
 'torchinfo>=1.7.0,<2.0.0']

entry_points = \
{'console_scripts': ['tailors-corpus-from-eb = '
                     'tailors_trainer.corpus_from_eb:process',
                     'tailors-train = tailors_trainer.train:train',
                     'tailors-train-fast = tailors_trainer.fast.train:train']}

setup_kwargs = {
    'name': 'tailors-trainer',
    'version': '0.1.1',
    'description': '',
    'long_description': None,
    'author': 'orctom',
    'author_email': 'orctom@gmail.com',
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
