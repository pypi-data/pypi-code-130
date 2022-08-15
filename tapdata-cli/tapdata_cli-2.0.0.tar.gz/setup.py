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
    'version': '2.0.0',
    'description': 'Tapdata Python Sdk',
    'long_description': '# TAPDATA OpenSource Terminal Client\n\n## Install\n1. Install python 3.7, pip, ipython By Yourself\n2. Run `pip3 install -r requirements.txt`, install client requirements\n3. If you want to embed it into your code as Python SDK, please [read this article](https://github.com/tapdata/tapdata/tree/master/tapshell/docs/Python-Sdk.md).\n\n## Prepare\n1. Edit config.ini, set server as iDaas Server address, and access_code as auth\n\nYou can ignore it, and run login after start client\n\n## Run\n1. `bash cli.sh` will open terminal client\n\n## Help Command\n*. Run `h` will display common help message\n![](./images/h.png)\n\n*. Run `h command` will display command mode message\n![](./images/h_command.png)\n\n*. Run `h lib` will display lib mode message\n![](./images/h_lib.png)\n\n## Example\n### Login\n![](./images/login.png)\n\n### See your Connections\n![](./images/show_db.png)\n![](./images/show_table.png)\n![](./images/desc_table.png)\n\n\n### Migrate a table with Data Check\n![](./images/migrate.png)\n\n### Migrate a table with UDF\n\n### Cache a table and Preview it\n![](./images/preview.png)\n\n## Document\n### 初始化\n1. 可以在 config.ini 填写地址和访问串, 启动时会自动识别并登录\n2. 可以在启动后, 通过 `login(server, access_code)` 进行手动登录\n3. 如果要作为Python Sdk的形式内嵌到您的代码当中，请看[这篇文档](https://github.com/tapdata/tapdata/tree/master/tapshell/docs/Python-Sdk_zh-hans.md)\n\n### 列出所有数据连接\nshow dbs\n```\n>>> show dbs\nid     status  database_type   name\n9c6046: ready   mysql           docker_mysql_5562\n9c604b: ready   mysql           docker_mysql_8023_target\n9c6052: ready   oracle          oracle_19c_TAPDATA\n```\n\n### 切换到某个连接\nuse 连接, 可以使用 show 的简略 id, 或者使用名字\n比如: use 9c6046, use docker_mysql_5562\n\n### 列出当前连接的全部数据表\nshow tables\n\n### 查看表信息\ndesc 表, 可以使用 show 的简略 id, 或者使用名字\n\n### 查看表的示例数据\npeek 表, 可以使用 show 的简略 id, 或者使用名字\n\n### 创建连接\n1. 支持使用封装对象创建, 比如 MongoDB\n```\nm = MongoDB("source").\nm.host("192.168.1.181:32560").db("source").username("root").password("Gotapd8!").type("source").props("authSource=admin");\nm.validate()\nCHECK_CONNECT: passed\nCHECK_AUTH: passed\nCHECK_PERMISSION: passed\nLOAD_SCHEMA: passed\nCHECK_CDC_PERMISSION: passed\n\nm.save()\n```\n\n2. 使用标准对象进行创建\n```\nm = DataSource("source")\nm.connector("mongodb")\n其余与封装对象一样, 需要保证每个属性与定义的数据表单一致\n\nm.validate()\nm.save()\n```\n\n### 库复制任务创建\n1. 可以使用简单语法: `库名.syncTo(目标库名, prefix=, suffix=)` 直接创建任务\n比如: docker_mysql_5562.syncTo(oracle_19c_TAPDATA, prefix="p_")\n返回一个任务, 可以通过返回的对象进行 start/stop/status/monitor 的操作\n\n2. 可以使用标准语法创建任务\n```\np = Pipeline()\np.readFrom(source).writeTo(sink, prefix=, suffix=)\n```\n\n### 表复制任务创建\n使用标准语法创建任务\n```\np = Pipeline()\np.readFrom(source.table).writeTo(sink.table)\n\np.accurateDelay() # 开启精准延迟计算\n```\n\n### 数据校验\n在创建表复制任务之后, 可以直接调用 `p.check()` 启动校验任务, 并打印校验结果, 重复调用可实时获取最新结果\n\n### 计算任务创建\n使用标准语法创建任务\n```\np = Pipeline("name")\np.readFrom(source1.table).writeTo(sink.table, writeMode=upsert)\np.readFrom(source2.table).filter("table_id > 1").writeTo(sink.table, writeMode=update)\n```\n\n创建的是一个主从表合并的任务, 支持的算子有:\n1. filter: 过滤源数据, 参数为 "a > 1 and b < 2" 类似风格, 简单查询与组合\n2. filterColumn: 保留或者删除某些列, 第一个参数为数组, 列名, 第二个参数为行为, keep 保留, delete 删除\n3. rename: 两个参数, 列名修改\n4. js: 自定义 js, 输入字符串, 为 js 脚本\n5. agg: 聚合, 暂时不建议使用\n\n### 列出 api\nshow apis\n\n### 发布 api\npublish name db.table\n\n### 取消发布 api\nunpublish name\n',
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
