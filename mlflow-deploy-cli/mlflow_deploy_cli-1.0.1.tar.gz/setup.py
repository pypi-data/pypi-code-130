# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['mlflow_deploy_cli', 'mlflow_deploy_cli.utils']

package_data = \
{'': ['*'], 'mlflow_deploy_cli': ['template/*']}

install_requires = \
['prompt-toolkit>=3.0.30,<4.0.0']

setup_kwargs = {
    'name': 'mlflow-deploy-cli',
    'version': '1.0.1',
    'description': 'CLI for deployment of [MLFlow](https://mlflow.org/) with support for backend and artifact stores.',
    'long_description': "# mlflow-deployment\n\nCLI for deployment of [MLFlow](https://mlflow.org/) with support for backend and artifact stores.\n\nDeploy MLFlow with support for PostgreSQL, Azure Blobs, Amazon S3 and Google Cloud Platform with ease.\n\n# Usage\n\n1. [`pip install mlflow-deploy-cli`](https://pypi.org/project/mlflow-deploy-cli/)\n\n2. `python -m mlflow_deploy_cli --artifact-store '<desired_store>'` _can be [`azure`](https://www.mlflow.org/docs/latest/tracking.html#azure-blob-storage), [`s3`](https://www.mlflow.org/docs/latest/tracking.html#id82), [`gcp`](https://www.mlflow.org/docs/latest/tracking.html#id84) or `local`_\n\n3. `cd build`\n\n4. `docker build . -t mlflow`\n\n5. `docker-compose up -f docker-compose.yml up`\n\nMLFlow is up and running 🚀.",
    'author': 'Aleksandar Ivanovski',
    'author_email': 'aleksandar.ivanovski@codechem.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': None,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.9,<4.0',
}


setup(**setup_kwargs)
