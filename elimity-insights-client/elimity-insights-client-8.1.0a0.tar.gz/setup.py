# -*- coding: utf-8 -*-
from setuptools import setup

modules = \
['elimity_insights_client']
install_requires = \
['python-dateutil>=2.8.2,<3.0.0',
 'requests>=2.28.1,<3.0.0',
 'simplejson>=3.17.6,<4.0.0']

setup_kwargs = {
    'name': 'elimity-insights-client',
    'version': '8.1.0a0',
    'description': 'Client for connector interactions with an Elimity Insights server',
    'long_description': '# Elimity Insights Python client\n\nThis Python module provides a client for connector interactions with an Elimity\nInsights server.\n\n## Usage\n\n```python3\nfrom datetime import datetime\n\nfrom elimity_insights_client import Client, Config, ConnectorLog, Level\n\nif __name__ == "__main__":\n    config = Config(url="https://local.elimity.com:8081", token="token")\n    client = Client(config)\n\n    timestamp = datetime.now()\n    log = ConnectorLog(level=Level.INFO, message="Hello world!", timestamp=timestamp)\n    logs = [log]\n    client.create_connector_logs(logs)\n```\n\n## Installation\n\n```sh\n$ pip install elimity-insights-client\n```\n\n## Compatibility\n\n| Client version | Insights version |\n| -------------- | ---------------- |\n| 1              | 2.8 - 2.10       |\n| 2 - 3          | 2.11 - 3.0       |\n| 4              | 3.1 - 3.3        |\n| 5 - 6          | 3.4 - 3.5        |\n| 7              | 3.6 - 3.7        |\n| 8              | ^3.8             |\n',
    'author': 'Elimity development team',
    'author_email': 'dev@elimity.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://github.com/elimity-com/insights-client-python',
    'py_modules': modules,
    'install_requires': install_requires,
    'python_requires': '>=3.7,<4.0',
}


setup(**setup_kwargs)
