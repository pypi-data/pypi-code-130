# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['monaco_racing_report']

package_data = \
{'': ['*']}

setup_kwargs = {
    'name': 'monaco-racing-report',
    'version': '0.1.5',
    'description': 'Report of Monaco 2018 Racing',
    'long_description': "# Report of Monaco 2018 Racing\n\n**monaco_racing_report** is a program where you can get a statistic of Monaco 2018 Racing\n\n### Install\n\n```python\npip install monaco-racing-report\n```\n\n### How to Use\n\n```python\nfrom monaco-racing-report import main\nmain()\n# you will get 15 drivers and theirs statistic\n```\n\n### Launch\n\nYou can use this program from the terminal(using cli)\n\n```python\npython monaco_racing_report/report.py --files [FOLDER PATH] --driver [NAME SURNAME DRIVER]\n# you will get driver statistic\n```\n\nFor example:\n```python\npython monaco_racing_report/report.py --files data_files --driver 'Sebastian Vettel'\n```\nResult: Sebastian Vettel | car - FERRARI | start time - 12:02:58.917 | finish time - 12:04:03.332 | result -\n 0:01:04.415000\n\n------------------------------\n\nShows list of drivers\n```python\npython monaco_racing_report/report.py --files <folder_path> --asc\n```\n--asc   - in ascending order\n<br>\n--desc  - in descending order\n\n<br>\n\nSee the source at  [Link](https://git.foxminded.com.ua/foxstudent102894/task-6-report-of-monaco-2018-racing)\n<br>\n© 2022 Anton Skazko\n",
    'author': 'Skazko Anton',
    'author_email': 'sk.anton06@gmail.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': None,
    'packages': packages,
    'package_data': package_data,
    'python_requires': '>=3.8,<4.0',
}


setup(**setup_kwargs)
