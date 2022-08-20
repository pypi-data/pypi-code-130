# -*- coding: utf-8 -*-
from setuptools import setup

package_dir = \
{'': 'src'}

packages = \
['unfold',
 'unfold.contrib',
 'unfold.contrib.numeric_filters',
 'unfold.templatetags']

package_data = \
{'': ['*'],
 'unfold': ['static/unfold/css/*',
            'static/unfold/img/*',
            'static/unfold/js/*',
            'templates/admin/*',
            'templates/admin/auth/user/*',
            'templates/admin/edit_inline/*',
            'templates/admin/includes/*',
            'templates/admin/widgets/*',
            'templates/auth/widgets/*',
            'templates/unfold/helpers/*',
            'templates/unfold/layouts/*',
            'templates/unfold/widgets/*'],
 'unfold.contrib.numeric_filters': ['static/js/*', 'templates/admin/*']}

install_requires = \
['django>=3.2']

setup_kwargs = {
    'name': 'django-unfold',
    'version': '0.1.1',
    'description': 'Clean & minimal Django admin theme based on Tailwind CSS',
    'long_description': None,
    'author': None,
    'author_email': None,
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://github.com/remastr/django-unfold',
    'package_dir': package_dir,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.8',
}


setup(**setup_kwargs)
