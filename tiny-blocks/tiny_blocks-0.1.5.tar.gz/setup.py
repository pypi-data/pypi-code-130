# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['tiny_blocks',
 'tiny_blocks.extract',
 'tiny_blocks.load',
 'tiny_blocks.transform']

package_data = \
{'': ['*']}

install_requires = \
['PyMySQL>=1.0.2,<2.0.0',
 'SQLAlchemy>=1.4.39,<2.0.0',
 'boto3>=1.24.43,<2.0.0',
 'cryptography>=37.0.4,<38.0.0',
 'cx-Oracle>=8.3.0,<9.0.0',
 'kafka-python>=2.0.2,<3.0.0',
 'minio>=7.1.11,<8.0.0',
 'pandas>=1.4.3,<2.0.0',
 'psycopg2>=2.9.3,<3.0.0',
 'pydantic>=1.9.1,<2.0.0']

setup_kwargs = {
    'name': 'tiny-blocks',
    'version': '0.1.5',
    'description': 'Tiny Block Operations for Data Pipelines',
    'long_description': ' tiny-blocks\n=============\n\n[![Documentation Status](https://readthedocs.org/projects/tiny-blocks/badge/?version=latest)](https://tiny-blocks.readthedocs.io/en/latest/?badge=latest)\n[![License-MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://github.com/pyprogrammerblog/tiny-blocks/blob/master/LICENSE)\n[![GitHub Actions](https://github.com/pyprogrammerblog/tiny-blocks/workflows/CI/badge.svg/)](https://github.com/pyprogrammerblog/tiny-blocks/workflows/CI/badge.svg/)\n[![PyPI version](https://badge.fury.io/py/tiny-blocks.svg)](https://badge.fury.io/py/tiny-blocks)\n\nTiny Blocks to build large and complex pipelines!\n\nTiny-Blocks is a library for streaming operations, composed using the `>>`\noperator. This allows for easy extract, transform and load operations.\n\n### Pipeline Components: Sources, Pipes, and Sinks\nThis library relies on a fundamental streaming abstraction consisting of three\nparts: extract, transform, and load. You can view a pipeline as a extraction, followed\nby zero or more transformations, followed by a sink. Visually, this looks like:\n\n```\nsource >> pipe1 >> pipe2 >> pipe3 >> ... >> pipeN >> sink\n```\n\nInstallation\n-------------\n\nInstall it using ``pip``\n\n```shell\npip install tiny-blocks\n```\n\nBasic usage example\n--------------------\n\n```python\nfrom tiny_blocks.extract import FromCSV\nfrom tiny_blocks.transform import DropDuplicates\nfrom tiny_blocks.transform import Fillna\nfrom tiny_blocks.load import ToSQL\n\n# ETL Blocks\nfrom_csv = FromCSV(path=\'/path/to/file.csv\')\ndrop_duplicates = DropDuplicates()\nfill_na = Fillna(value="Hola Mundo")\nto_sql = ToSQL(dsn_conn=\'psycopg2+postgres://...\')\n\n# Run the Pipeline\nfrom_csv >> drop_duplicates >> fill_na >> to_sql\n```\n\nDocumentation\n--------------\n\nPlease visit this [link](https://tiny-blocks.readthedocs.io/en/latest/) for documentation.\n',
    'author': 'Jose Vazquez',
    'author_email': 'josevazjim88@gmail.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://github.com/pyprogrammerblog/tiny-blocks',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.9,<4.0',
}


setup(**setup_kwargs)
