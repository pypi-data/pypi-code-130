# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['easy_sql',
 'easy_sql.sql_linter',
 'easy_sql.sql_linter.rules',
 'easy_sql.sql_processor',
 'easy_sql.sql_processor.backend',
 'easy_sql.sql_processor.backend.sql_dialect',
 'easy_sql.udf',
 'easy_sql.utils']

package_data = \
{'': ['*']}

extras_require = \
{'cli': ['click>=8.1.3,<9.0.0'],
 'clickhouse': ['SQLAlchemy>=1.4.40,<2.0.0',
                'clickhouse-driver>=0.2.4,<0.3.0',
                'clickhouse-sqlalchemy>=0.2.1,<0.3.0'],
 'linter': ['regex>=2022.7.25,<2023.0.0',
            'colorlog>=6.6.0,<7.0.0',
            'sqlfluff>=1.2.1,<2.0.0'],
 'pg': ['SQLAlchemy>=1.4.40,<2.0.0', 'psycopg2-binary>=2.9.3,<3.0.0'],
 'spark': ['pyspark>=3.3.0,<4.0.0']}

setup_kwargs = {
    'name': 'easy-sql-easy-sql-j',
    'version': '0.3.0',
    'description': 'A library developed to ease the data ETL development process.',
    'long_description': '# Easy SQL\n\nEasy SQL is built to ease the data ETL development process.\nWith Easy SQL, you can develop your ETL in SQL in an imperative way.\nIt defines a few simple syntax on top of standard SQL, with which SQL could be executed one by one.\nEasy SQL also provides a processor to handle all the new syntax.\nSince this is SQL agnostic, any SQL engine could be plugged-in as a backend.\nThere are built-in support for several popular SQL engines, including SparkSQL, PostgreSQL, Clickhouse, Aliyun Maxcompute, Google BigQuery.\nMore will be added in the near future.\n\n- Docs: <https://easy-sql.readthedocs.io/>\n- Enterprise extended product: <https://data-workbench.com/>\n\n[![GitHub Action Build](https://github.com/easysql/easy_sql/actions/workflows/build.yaml/badge.svg?branch=main&event=push)](https://github.com/easysql/easy_sql/actions/workflows/build.yaml?query=branch%3Amain+event%3Apush)\n[![Docs Build](https://readthedocs.org/projects/easy-sql/badge/?version=latest)](https://easy-sql.readthedocs.io/en/latest/?badge=latest)\n[![EasySQL Coverage](https://codecov.io/gh/easysql/easy_sql/branch/main/graph/badge.svg)](https://codecov.io/gh/easysql/easy_sql)\n\n## Install Easy SQL\n\nInstall Easy SQL using pip: `python3 -m pip install easy_sql-easy_sql`\n\n## Building Easy SQL\n\nEasy SQL is developed in Python and could be built with the following make command:\n\n```bash\nmake package-pip\n```\n\nAfter the above command, there will be a file named `easy_sql*.whl` generated in the `dist` folder.\nYou can install it with command `pip install dist/easy_sql*.whl`.\n\n## Dependencies\n\nSince there are several backends, we only need to install some specific dependencies if we only use one of them.\n\nFor spark, you need to install some version of `pyspark`.\n\nFor other backends, install the dependencies as listed below:\n```\n# for pg/clickhouse/bigquery backend only\nSQLAlchemy==1.3.23\n# for pg backend only\npsycopg2-binary==2.8.6\n# for clickhouse backend only\nclickhouse-driver==0.2.0\nclickhouse-sqlalchemy==0.1.6\n# for BigQuery backend only\nsqlalchemy-bigquery==1.4.3\n# for MaxCompute backend only\npyodps==0.10.7.1\n```\n\nTo use other tools / functionalities, install the dependencies as listed below:\n\n```\n# for Linter only\nsqlfluff==1.2.1\ncolorlog==4.0.2\nregex==2022.6.2\n# for command line tools only\nclick==6.7\n```\n\n## First ETL with Easy SQL\n\n(You need to install click package (by command `python3 -m pip install click==6.7`) before run the command below.)\n\n### For spark backend\n\nCreate a file named `sample_etl.spark.sql` with content as below:\n\n```sql\n-- prepare-sql: drop database if exists sample cascade\n-- prepare-sql: create database sample\n-- prepare-sql: create table sample.test as select 1 as id, \'1\' as val\n\n-- target=variables\nselect true as __create_output_table__\n\n-- target=variables\nselect 1 as a\n\n-- target=log.a\nselect \'${a}\' as a\n\n-- target=log.test_log\nselect 1 as some_log\n\n-- target=check.should_equal\nselect 1 as actual, 1 as expected\n\n-- target=temp.result\nselect\n    ${a} as id, ${a} + 1 as val\nunion all\nselect id, val from sample.test\n\n-- target=output.sample.result\nselect * from result\n\n-- target=log.sample_result\nselect * from sample.result\n```\n\nRun it with command:\n\n```bash\nbash -c "$(python3 -m easy_sql.data_process -f sample_etl.spark.sql -p)"\n```\n\n### For postgres backend:\n\nYou need to start a postgres instance first.\n\nIf you have docker, run the command below:\n\n```bash\ndocker run -d --name postgres -p 5432:5432 -e POSTGRES_PASSWORD=123456 postgres\n```\n\nCreate a file named `sample_etl.postgres.sql` with content as the test file [here](https://github.com/easysql/easy_sql/blob/main/test/sample_etl.postgres.sql).\n\nRun it with command:\n\n```bash\nPG_URL=postgresql://postgres:123456@localhost:5432/postgres python3 -m easy_sql.data_process -f sample_etl.postgres.sql\n```\n\n### For clickhouse backend:\n\nYou need to start a clickhouse instance first.\n\nIf you have docker, run the command below:\n\n```bash\ndocker run -d --name clickhouse -p 9000:9000 yandex/clickhouse-server:20.12.5.18\n```\n\nCreate a file named `sample_etl.clickhouse.sql` with content as the test file [here](https://github.com/easysql/easy_sql/blob/main/test/sample_etl.clickhouse.sql).\n\nRun it with command:\n\n```bash\nCLICKHOUSE_URL=clickhouse+native://default@localhost:9000 python3 -m easy_sql.data_process -f sample_etl.clickhouse.sql\n```\n\n### For other backends:\n\nThe usage is similar, please refer to API.\n\n## Run ETL in your code\n\nEasy SQL can be used as a very light-weight library. If you\'d like to run ETL programmatically in your code.\nPlease refer to the code snippets below:\n\n```python\nfrom pyspark.sql import SparkSession\n\nfrom easy_sql.sql_processor import SqlProcessor\nfrom easy_sql.sql_processor.backend import SparkBackend\n\nif __name__ == \'__main__\':\n    spark = SparkSession.builder.enableHiveSupport().getOrCreate()\n    backend = SparkBackend(spark)\n    sql = \'\'\'\n-- target=log.some_log\nselect 1 as a\n    \'\'\'\n    sql_processor = SqlProcessor(backend, sql)\n    sql_processor.run()\n```\n\nMore sample code about other backends could be referred [here](https://github.com/easysql/easy_sql/blob/main/test/sample_data_process.py)\n\n## Debugging ETL\n\nWe recommend debugging ETLs from jupyter. You can follow the steps below to start debugging your ETL.\n\n1. Install jupyter first with command `pip install jupyterlab`.\n\n2. Create a file named `debugger.py` with contents like below:\n\nA more detailed sample could be found [here](https://github.com/easysql/easy_sql/blob/main/debugger.py).\n\n```python\nfrom typing import Dict, Any\n\ndef create_debugger(sql_file_path: str, vars: Dict[str, Any] = None, funcs: Dict[str, Any] = None):\n    from pyspark.sql import SparkSession\n    from easy_sql.sql_processor.backend import SparkBackend\n    from easy_sql.sql_processor_debugger import SqlProcessorDebugger\n    spark = SparkSession.builder.enableHiveSupport().getOrCreate()\n    backend = SparkBackend(spark)\n    debugger = SqlProcessorDebugger(sql_file_path, backend, vars, funcs)\n    return debugger\n\n```\n\n3. Create a file named `test.sql` with contents as [here](https://github.com/easysql/easy_sql/blob/main/test/sample_etl.spark.sql).\n\n4. Then start jupyter lab with command: `jupyter lab`.\n\n5. Start debugging like below:\n\n![ETL Debugging](https://raw.githubusercontent.com/easysql/easy_sql/main/debugger-usage.gif)\n\n## Contributing\n\nPlease submit PR.\n',
    'author': 'Easy SQL from Thoughtworks',
    'author_email': 'easy_sql@thoughtworks.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://easy-sql.readthedocs.io',
    'packages': packages,
    'package_data': package_data,
    'extras_require': extras_require,
    'python_requires': '>=3.7,<4.0',
}


setup(**setup_kwargs)
