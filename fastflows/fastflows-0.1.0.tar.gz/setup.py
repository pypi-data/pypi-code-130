# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['fastflows',
 'fastflows.cli',
 'fastflows.config',
 'fastflows.core',
 'fastflows.core.catalog',
 'fastflows.core.utils',
 'fastflows.providers',
 'fastflows.routers',
 'fastflows.schemas',
 'fastflows.schemas.prefect',
 'fastflows.utils']

package_data = \
{'': ['*']}

install_requires = \
['fastapi-opa>=1.3.7,<2.0.0',
 'fsspec>=2022.7.1,<2023.0.0',
 'httpx>=0.23.0,<0.24.0',
 'loguru>=0.6.0,<0.7.0',
 'mangum>=0.15.0,<0.16.0',
 'pydantic[dotenv]>=1.9.1,<2.0.0',
 'python-slugify>=6.1.2,<7.0.0',
 'rich>=12.4.4,<13.0.0',
 's3fs>=2022.7.1,<2023.0.0',
 'typer>=0.4.1,<0.7.0',
 'uvicorn>=0.17.6,<0.19.0']

entry_points = \
{'console_scripts': ['fastflows = fastflows.cli.main:app']}

setup_kwargs = {
    'name': 'fastflows',
    'version': '0.1.0',
    'description': 'FastFlows is a FastAPI server & command line tool to comunicate with Prefect 2.0 as a Workflow manager (and in future other systems like Pygeoapi, for example) to deploy, run, track flows and more.',
    'long_description': "## Run FastFlow server\n\nFastFlows is a FastAPI server & command line tool to comunicate with Prefect 2.0 as a Workflow manager to deploy, run, track flows and more.\n\nTo start work with FastFlows you should define at least 2 environment variables:\n\n```console\n\n    # Prefect API Server address\n    PREFECT_URI=http://localhost:4200\n\n    # Path to folder with flows\n    FLOWS_HOME=flows\n\n```\n\nIf you want to define variables with env prefix, for example, like 'LOCAL_PREFECT_URI' or 'DEV_PREFECT_URI' you can use environment variable 'ENV_NAME'\n\nIf Fastflow will see 'ENV_NAME' variable in environment - it will search for variables with prefix defined in this ENV_NAME, for example:\n\nif ENV_NAME = 'LOCAL'\n\nFastflows will read variables like LOCAL_PREFECT_URI and LOCAL_FLOWS_HOME,\n\nif ENV_NAME = 'dev', then fastflow will expect variables like 'dev_PREFECT_URI' and 'dev_FLOWS_HOME'\n\n### How to run FastFlows with Prefect cluster\n\n#### with Kubernetes\n\n- [Kube instructions](docker/README.md)\n- [Kubernetes configuration](docker/kube-infra/)\n\n#### with Docker-Compose\n\n- [Docker-Compose readme](docker/README.md)\n- [Docker-compose YAML](docker/docker-compose.yml)\n\n### Run cli\n\n```console\n\n    fastflows --help\n\n```\n\n### Flows Deployment\n\n#### Auto deployment\n\nDeployment of Flows can be done by FastFlows automatically: if there is a new flow or changes in FLOWS_HOME directory - FastFlow create new deployment. To disable auto deployment set env variable to 0\n\n```console\n\n    FASTFLOWS_AUTO_DEPLOYMENT = 0\n\n```\n",
    'author': 'Francesco Bartoli',
    'author_email': 'francesco.bartoli@geobeyond.it',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://github.com/geobeyond/fastflows',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'entry_points': entry_points,
    'python_requires': '>=3.8,<4.0',
}


setup(**setup_kwargs)
