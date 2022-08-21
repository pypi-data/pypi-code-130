# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['django_business_metrics', 'django_business_metrics.v0']

package_data = \
{'': ['*']}

install_requires = \
['Django>=3,<4', 'prometheus-client>=0.13.0,<0.15']

setup_kwargs = {
    'name': 'django-business-metrics',
    'version': '0.1.0a4',
    'description': 'Django Prometheus business metrics',
    'long_description': "# Django Prometheus business metrics\n\nThis Django app provides a Prometheus metrics endpoint serving so-called business metrics. These are metrics that are calculated when Prometheus hits the metrics endpoint.\n\n## Usage\n\n1. Create a `BusinessMetricsManager` object and register some metrics:\n\n    ```\n    # project/business_metrics.py\n\n    from django_business_metrics.v0 import BusinessMetricsManager, users\n\n    metrics_manager = BusinessMetricsManager()\n\n    # Add a pre-defined metric\n    metrics_manager.add(users)\n\n    # Add some custom metrics\n    @metrics_manager.metric()\n    def my_metric():\n        return 10\n    ```\n\n2. Register a Prometheus endpoint:\n\n\n    ```\n    # project/urls.py\n\n    ...\n    from .business_metrics import metrics_manager\n\n    ...\n    urlpatterns = [\n        ...\n        path('business-metrics', metrics_manager.view),\n        ...\n    ]\n    ```\n\n3. Setup your Prometheus agent to scrape metrics from `/business-metrics` endpoint.",
    'author': 'Reef Technologies',
    'author_email': 'vykintas.baltrusaitis@reef.pl',
    'maintainer': None,
    'maintainer_email': None,
    'url': None,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.8,<3.11',
}


setup(**setup_kwargs)
