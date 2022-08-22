# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['pythonquerylanguage']

package_data = \
{'': ['*']}

install_requires = \
['SQLAlchemy>=1.4.31,<2.0.0',
 'ipython==8.0.1',
 'numpy>=1.22.2,<2.0.0',
 'pandas>=1.4.1,<2.0.0']

setup_kwargs = {
    'name': 'pythonquerylanguage',
    'version': '0.1.6',
    'description': 'Python SQL wrapper based on pandas and SQLalchemy',
    'long_description': '\n# <b>Python Query Language PQL</b>\n\n<b>PQL</b> is a python wrapper of the sql sintax based in SQLalchemy and pandas, this code introduces a new syntax to use \nin your code when calling a database table.\n\n## Requirements\n\nYou only need a distribution of python3 installed.\n\n## ⚙️Installation:\n\nYou can install the requirements (preferably in an environment) using:\n\n> pip install PythonQueryLanguage\n\n## Basic Usage:\n\nPQL is managed by a class called SQLManager, to instanciated you will need to pass your connection strings in a dictionary\nand the enviroment you are willoing to use\n\n`\nconnection_dict = {\'test_env\': \'connection string from engine\',\n                   \'prod_env\': \'mssql+pyodbc://ur@prod.com/url2?driver=ODBC+Driver+17+for+SQL+Server\'\n                  }\nenv = \'test_env\'\npql = SQLManager(connection_dict,env)\n`\n\nOnce you have instanciated the class you can use it with his convenient functions that will wrap SQL expresions.\n\n> pql.select_all(\'tableA\',\'id\',\'myid\')  =  SELECT * FROM tableA WHERE id = \'myid\n\nPQL supports searchs in arrays:\n\n> pql.select_all(\'tableA\',\'id\',[\'myid\',\'myid2\'])  =  SELECT * FROM tableA WHERE id IN (\'myid\',\'myid2\')\n\nPQL cast the data in a inteligent manner:\n\n> pql.select_all(\'tableA\',[\'id\',\'name\'],[\'myid\',\'myName\'])  =  SELECT * FROM tableA WHERE id = \'myid\' AND myName = \'myid2\'\n\nPQL accepts adiotional arguments:\n\n> pql.select(\'column\',\'tableA\',[\'id\',\'name\'],[\'myid\',\'myName\'],\'OR\')  =  SELECT column FROM tableA WHERE id = \'myid\' OR myName = \'myid2\'\n\nPQL accepts direct evaluation or raw sql expressions (thougt only recommended in edge cases)\n\n> pql.query("SELECT * FROM tableA WHERE id = \'myid")  =  SELECT * FROM tableA WHERE id = \'myid\'\n\nPQL accepst function and Store procedure evaluations.\n\n## Multy enviroment usage.\n\nPQL is built to support working with different db environments at the same time, this multi enviroment work can be done in different ways:\n\n- 1. Instanciate the PQLmanager with different enviroments and run them.\n- 2. Changing the enviroment of the class with the change_enviroment method.\n- 3. Using scoped functions.\n\nExample of scoped functions:\n\nYou are working in a database test enviroment but you need to extract some data from the production enviroment without changing the enviroment of the PQLmanager\nThen you can query the table at producion using a scope:\n\n> pql.select_all(\'TableA\',env=\'prod\')\n\nThis function will run in the production environment and retrieve the information from it without changing your global environment.\n\n## IUD\n\nPQL supports Insert Update Delete Operations, all these operations are based in pandas dataframes.\n\n## Interactive.\n\nPQL is thought to be used in a jupyter notebook as well as used in real code. PQL contains different functionalities that allows the user\nto know what query will be executed in the database and confirmation security.\n\n',
    'author': 'Pablo Ruiz',
    'author_email': 'pablo.r.c@live.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': None,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.8,<4.0',
}


setup(**setup_kwargs)
