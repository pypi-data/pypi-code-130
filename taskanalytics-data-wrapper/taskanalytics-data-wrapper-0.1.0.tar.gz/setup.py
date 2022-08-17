# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['taskanalytics_data_wrapper']

package_data = \
{'': ['*']}

install_requires = \
['requests>=2.28.1,<3.0.0', 'tqdm>=4.64.0,<5.0.0']

setup_kwargs = {
    'name': 'taskanalytics-data-wrapper',
    'version': '0.1.0',
    'description': 'a wrapper for using Task Analytics APIs and downloading survey responses',
    'long_description': '# Task Analytics Data Wrapper\n\n[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)\n\nThis is a wrapper for Task Analytics APIs. You can use it to download survey responses and metadata for each survey.\n\n## Supported APIs\n\n- [Task Analytics Data Wrapper](#task-analytics-data-wrapper)\n  - [Supported APIs](#supported-apis)\n    - [Log in to Task Analytics](#log-in-to-task-analytics)\n    - [Download Survey responses](#download-survey-responses)\n    - [Download Survey metadata](#download-survey-metadata)\n\n### Log in to Task Analytics\n\nYou can log in with email and password\n\n```python\nstatus = log_in_taskanalytics(username=email, password=password)  \nstatus.status_code\n```\n\n### Download Survey responses\n\nYou can download survey responses for a Top Task survey using the survey ID, email, password and setting a path for where to store the file.\n\n```python\nget_survey = download_survey(\n    username=email, password=password, survey_id="03324", filename="data/survey.csv"\n)\nget_survey.status_code\n```\n\n### Download Survey metadata\n\nYou can download the survey metadata which includes the questions and response options for each survey using the survey ID, email and password.\n\n```python\nsurvey_metadata = get_survey_metadata(\n    username=email, password=password, survey_id="03324"\n)\nsurvey_metadata.status_code\n```\n\nThe object can be easily inspected transformed into a dictionary for analysis\n\n```python\nsurvey_metadata.text # survey metadata\nour_dict = survey_metadata.json() # convert string to dict and store as a variable\n```',
    'author': 'Tobias McVey',
    'author_email': 'tobias.mcvey@nav.no',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://github.com/navikt/taskanalytics-data-wrapper',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.8,<4.0',
}


setup(**setup_kwargs)
