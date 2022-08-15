# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['tapdata_cli']

package_data = \
{'': ['*'], 'tapdata_cli': ['startup/*']}

install_requires = \
['PyYAML==5.4.1',
 'allure-pytest>=2.9.45,<3.0.0',
 'asyncio==3.4.3',
 'atomicwrites==1.4.0',
 'attrs==21.2.0',
 'certifi==2020.12.5',
 'chardet==4.0.0',
 'colorama==0.4.4',
 'colorlog==5.0.1',
 'idna==2.10',
 'iniconfig==1.1.1',
 'javascripthon>=0.12,<0.13',
 'jupyter>=1.0.0,<2.0.0',
 'packaging==20.9',
 'pluggy==0.13.1',
 'py==1.10.0',
 'pymongo==4.1.1',
 'pyparsing==2.4.7',
 'pytest>=7.1.2,<8.0.0',
 'requests==2.25.1',
 'toml==0.10.2',
 'urllib3==1.26.4',
 'websockets==9.0.2']

setup_kwargs = {
    'name': 'tapdata-cli',
    'version': '2.1.0',
    'description': 'Tapdata Python Sdk',
    'long_description': '# Tapdata Python Sdk\n\n[中文文档地址](https://github.com/tapdata/tapdata/tree/master/tapshell/docs/Python-Sdk_zh-hans.md)\n\n## Install\n\n1. Install python 3.7, pip By Yourself.\n2. Run ```pip install tapdata_cli``` to install sdk.\n3. If you use poetry, please run ```poetry add tapdata_cli``` to install sdk.\n\n## Initial\n\n```python\nserver = "127.0.0.1:3000"\naccess_code = "3324cfdf-7d3e-4792-bd32-571638d4562f"\nfrom tapdata_cli import cli\ncli.init(server, access_code)\n```\n\n**Multi-thread concurrency is not supported**\n\nIt will send a request to the server to obtain the identity information and save it as a global variable. Therefore, after multiple init the \'server\' and \'access_code\' variable will be overwritten. \n\nFor situations where you need to use different servers and access_codes concurrently, use Python\'s multiprocess.\n\n## Create DataSource\n\n```python\n# create datasource by uri\nfrom tapdata_cli import cli\nmongo = cli.DataSource("mongodb", name="source")\nmongo.uri("mongodb://localhost:8080")\nmongo.validate() # available -> True, disabled -> False\nmongo.save() # success -> True, Failure -> False\n\n# create datasource by form\nmongo = cli.DataSource("mongodb", name="source")\nmongo.host("localhost:8080").db("source").user("user").password("password").type("source").props("")\nmongo.validate() # success -> True, Failure -> False\nmongo.save() # success -> True, Failure -> False\n\n# list datasource\nres = mongo.list()\n\n# res struct\n{\n    "total": 94,\n    "items": [{\n        "id": "",\n        "lastUpdBy": "",\n        "name": "",\n        "config": {},\n        "connection_type": "",\n        "database_type": "",\n        "definitionScope": "",\n        "definitionVersion": "",\n        "definitionGroup": "",\n        "definitionPdkId": "",\n        ...\n    }]\n}\n\n# get datasource by name/id\n\ncli.DataSource.get(id="")\n\n# return\n\n{\n    "id": "",\n    "lastUpdBy": "",\n    "name": "",\n    "config": {},\n    "connection_type": "",\n    "database_type": "",\n    "definitionScope": "",\n    "definitionVersion": "",\n    "definitionGroup": "",\n    "definitionPdkId": "",\n    ...\n}\n\n```\n\n## create Pipeline\n\n```python\nfrom tapdata_cli import cli\n\n# pipeline create\nsource = cli.DataSource("mongodb", name="source").uri("").save()\ntarget = cli.DataSource("mongodb", name="target").uri("").save()\np = cli.Pipeline(name="")\np.readFrom("source").writeTo("target")\n\n# pipeline start\np.start()\n\n# pipeline stop\np.stop()\n\n# pipeline delete\np.delete()\n\n# pipeline status\np.status()\n\n# list job object\ncli.Job.list()\n```\n\nJob is the underlying implementation of pipeline, so you can use job.start() like pipeline.start().\n\n```python\n# init job (get job info) by id\nfrom tapdata_cli import cli\njob = cli.Job(id="some id string")\njob.save() # success -> True, failure -> False\njob.start() # success -> True, failure -> False\n```\n\n### data operator\n\n```python\nfrom tapdata_cli import cli\nsource = cli.DataSource("mongodb", name="source").uri("").save()\ntarget = cli.DataSource("mongodb", name="target").uri("").save()\np = cli.Pipeline(name="")\np = p.readFrom("source.player") # source is db, player is table\np.dag.jobType = cli.JobType.sync\n\n# filter cli.FilterType.keep (keep data) / cli.FilterType.delete (delete data)\np = p.filter("id > 2", cli.FilterType.keep)\n\n# filerColumn cli.FilterType.keep (keep column) / cli.FilterType.delete (delete column)\np = p.filterColumn(["name"], cli.FilterType.delete)\n\n# rename\np = p.rename("name", "player_name")\n\n# valueMap\np = p.valueMap("position", 1)\n\n# js\np = p.js("return record;")\n\np.writeTo("target.player")  # target is db, player is table\n```\n\n## API Operation\n\n### Publish Api\n\n```python\nfrom tapdata_cli import cli\ncli.Api(name="test", table="source.player").publish() # source is db, player is table\n```\n\n### Unpublish APi\n\n```python\nfrom tapdata_cli import cli\ncli.Api(name="test").unpublish()\n```\n\n\n',
    'author': 'Tapdata',
    'author_email': 'team@tapdata.io',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://github.com/tapdata/tapdata/tree/master/tapshell',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.7,<4.0',
}


setup(**setup_kwargs)
