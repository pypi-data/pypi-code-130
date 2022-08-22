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
    'version': '0.1.11',
    'description': 'Tiny Block Operations for Data Pipelines',
    'long_description': ' tiny-blocks\n=============\n\n[![Documentation Status](https://readthedocs.org/projects/tiny-blocks/badge/?version=latest)](https://tiny-blocks.readthedocs.io/en/latest/?badge=latest)\n[![License-MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://github.com/pyprogrammerblog/tiny-blocks/blob/master/LICENSE)\n[![GitHub Actions](https://github.com/pyprogrammerblog/tiny-blocks/workflows/CI/badge.svg/)](https://github.com/pyprogrammerblog/tiny-blocks/workflows/CI/badge.svg/)\n[![PyPI version](https://badge.fury.io/py/tiny-blocks.svg)](https://badge.fury.io/py/tiny-blocks)\n\nTiny Blocks to build large and complex pipelines!\n\nTiny-Blocks is a library for **data engineering** operations. \nEach pipeline is made out of blocks glued with the `>>` operator. \nThis allows for easy extract, transform and load operations.\n\nTiny-Blocks use **generators** to stream data. The `chunksize` or buffer size \nis adjustable per extraction or loading operation.\n\n### Pipeline Components: Sources, Pipes, and Sinks\nThis library relies on a fundamental streaming abstraction consisting of three\nparts: extract, transform, and load. You can view a pipeline as an extraction, followed\nby zero or more transformations, followed by a sink. Visually, this looks like:\n\n```\nextract -> transform1 -> transform2 -> ... -> transformN >> load\n```\n\nYou can also `fan-in`, `fan-out` or `tee` for more complex operations.\n\n```\nextract1 -> transform1 -> |-> transform2 -> ... -> | -> transformN >> load1\nextract2 ---------------> |                        | -> load2\n```\n\n\nInstallation\n-------------\n\nInstall it using ``pip``\n\n```shell\npip install tiny-blocks\n```\n\nUsage examples\n---------------\n\n```python\nfrom tiny_blocks.extract import FromCSV, FromSQLTable\nfrom tiny_blocks.transform import DropDuplicates, Fillna, Merge\nfrom tiny_blocks.load import ToSQL, ToCSV\nfrom tiny_blocks.pipeline import Tee, FanIn\n\n# ETL Blocks\nfrom_csv = FromCSV(path=\'/path/to/source.csv\')\nfrom_sql = FromSQLTable(dsn_conn=\'psycopg2+postgres://...\', table_name="source")\nmerge = Merge(left_on="Column A", right_on="Column B", how="left")\nfill_na = Fillna(value="Hola Mundo")\ndrop_dupl = DropDuplicates()\nto_sql = ToSQL(dsn_conn=\'psycopg2+postgres://...\', table_name="sink")\nto_csv = ToCSV(path=\'/path/to/sink.csv\')\n\n# Run a simple Pipeline\nfrom_csv >> drop_dupl >> fill_na >> to_sql\n\n# Or a more complex one  \n# read_sql -> |                                | -> write into csv\n# read csv -> | -> merge -> drop duplicates -> | -> fill null values -> write to SQL\nFanIn(from_csv, from_sql) >> merge >> drop_dupl >> Tee(to_csv, fill_na >> to_sql)\n```\n\nExamples\n---------\n\nFor more complex examples please visit \nthe [notebooks\' folder](https://github.com/pyprogrammerblog/tiny-blocks/tree/master/notebooks).\n\n\nDocumentation\n--------------\n\nPlease visit this [link](https://tiny-blocks.readthedocs.io/en/latest/) for documentation.\n',
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
