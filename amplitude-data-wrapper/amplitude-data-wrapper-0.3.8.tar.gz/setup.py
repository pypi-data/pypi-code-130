# -*- coding: utf-8 -*-
from setuptools import setup

package_dir = \
{'': 'src'}

packages = \
['amplitude_data_wrapper']

package_data = \
{'': ['*']}

install_requires = \
['requests>=2.27.1,<3.0.0', 'tqdm>=4.62.3,<5.0.0']

setup_kwargs = {
    'name': 'amplitude-data-wrapper',
    'version': '0.3.8',
    'description': 'python wrapper for using the amplitude analytics and taxonomy APIs',
    'long_description': '# Amplitude data wrapper\n\n[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)\n\nThis is a wrapper for [Amplitude](https://amplitude.com/) APIs. You can use it to query and export data from your account and use the taxonomy API.\n\nBuilt with [requests](https://requests.readthedocs.io/en/latest/) and [tqdm](https://github.com/tqdm/tqdm)\n\n**Why use this package instead of other wrappers?**\n\nThis package supports regions and so you can use it with Amplitude accounts in the EU and USA.\n\nThis package also supports using a proxy so you can keep your project API keys and API secrets confidential.\n\n## Supported Amplitude APIs and docs\n\n- [Amplitude data wrapper](#amplitude-data-wrapper)\n  - [Supported Amplitude APIs and docs](#supported-amplitude-apis-and-docs)\n    - [Dashboard Rest API](#dashboard-rest-api)\n    - [Privacy API](#privacy-api)\n    - [Cohort API](#cohort-api)\n    - [Export API](#export-api)\n    - [Taxonomy API](#taxonomy-api)\n\nSee examples below and in [example.py](example.py)\n\nInstall with\n\n```\npip install amplitude-data-wrapper\n```\n\n### Dashboard Rest API\n\n[Results from an existing chart](https://developers.amplitude.com/docs/dashboard-rest-api#results-from-an-existing-chart)\n\nGet data from EU account by setting `region=1`.\n\n```python\nfrom amplitude_data_wrapper import get_chart\n\nr = get_chart(chart_id, api_key, api_secret, region=1)\nr.status_code  # 200\nr.text # print data\n```\n\nGet data from US account by setting `region=2`.\n\n```python\nfrom amplitude_data_wrapper import get_chart\n\nr = get_chart(chart_id, api_key, api_secret, region=2)\nr.status_code  # 200\nr.text # print data\n```\n\nGet data from EU account with a proxy by setting region and proxy using a dictionary.\n\n```python\nfrom amplitude_data_wrapper import get_chart\n\nproxies = {"http": "http://myproxy.domain.org/path"}\nr = get_chart(chart_id, api_key, api_secret, region=1, proxy=proxies)\nr.status_code  # 200\nr.text # print data\n```\n\n[Event segmentation](https://developers.amplitude.com/docs/dashboard-rest-api#event-segmentation) lets you export events with segments and filters.\n\n```python\nour_event_dict = {\n    "event_type": "pageview",\n    "group_by": [{"type": "event", "value": "app"}, {"type": "event", "value": "team"}],\n}\ndata = get_event_segmentation(\n    api_key=api_key,\n    secret=api_secret,\n    start="20220601",\n    end="20220602",\n    event=our_event_dict,\n    metrics="uniques",\n    interval=1,\n    limit=1000,\n)\n```\n\n[User search](https://developers.amplitude.com/docs/dashboard-rest-api#user-search) lets you search for a user with a specific Amplitude ID, Device ID, User ID, or User ID prefix.\n\n```python\nuser = find_user(\n    user=example_id_eu, \n    api_key=api_key, \n    secret=api_secret,\n    region=1)\n```\n\n### Privacy API\n\nDelete user data with a [deletion job](https://developers.amplitude.com/docs/user-deletion#deletion-job)\n\n```python\ndeleteme = delete_user_data(\n    user["matches"][0]["amplitude_id"],\n    email=email,\n    api_key=api_key,\n    secret=api_secret,\n    region=1,\n    ignore_invalid_id=True,\n    delete_from_org=False,\n)\n```\n\n[Get a list of deletion jobs](https://developers.amplitude.com/docs/user-deletion#get)\n\n```python\ntobe_deleted = get_deletion_jobs(\n    start="2022-06-01",\n    end="2022-07-01",\n    api_key=api_key,\n    secret=api_secret,\n    region=1,\n)\n```\n\n### Cohort API\n\n[Getting one cohort](https://developers.amplitude.com/docs/behavioral-cohorts-api#getting-one-cohort)\n\n```python\nproxies = {"http": "http://myproxy.domain.org/path"}\nfile_path = "path-to/cohortdata.csv"\nkull = get_cohort(\n    api_key,\n    api_secret,\n    cohort_id,\n    filename=file_path,\n    props=1,\n    region=1,\n    proxy=proxies,\n)\n```\n\n### Export API\n\n[Export API - Export your project\'s event data](https://developers.amplitude.com/docs/export-api#export-api---export-your-projects-event-data)\n\n```python\nstart = "20220601T00"\nend = "20220601T01"\ndata = export_project_data(\n    start=start,\n    end=end,\n    api_key=api_key,\n    secret=api_secret,\n    filename="path-to/projectdata_eu.zip",\n    region=1,\n)\n```\n\n### Taxonomy API\n\n[Get all event types](https://developers.amplitude.com/docs/taxonomy-api#get-all-event-types)\n\n```python\ntypes = get_all_event_types(\n    api_key=api_key, \n    secret=api_secret, \n    region=1)\n```',
    'author': 'Tobias McVey',
    'author_email': 'tobias.mcvey@nav.no',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://github.com/navikt/amplitude-data-wrapper',
    'package_dir': package_dir,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.8,<4.0',
}


setup(**setup_kwargs)
