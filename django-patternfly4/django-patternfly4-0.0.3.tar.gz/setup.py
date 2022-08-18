# -*- coding: utf-8 -*-
from setuptools import setup

package_dir = \
{'': 'src'}

packages = \
['docs', 'patternfly', 'patternfly.templatetags', 'tests', 'tests.app']

package_data = \
{'': ['*'], 'patternfly': ['templates/patternfly/*']}

install_requires = \
['beautifulsoup4>=4.11.1,<5.0.0', 'django>=4.0,<5.0']

extras_require = \
{'docs': ['sphinx>=5.1.1,<6.0.0',
          'sphinx_rtd_theme>=1.0.0,<2.0.0',
          'm2r2>=0.3.2,<0.4.0']}

setup_kwargs = {
    'name': 'django-patternfly4',
    'version': '0.0.3',
    'description': 'Patternfly support for Django projects',
    'long_description': '# django-patternfly\n\n\n\nPatternfly integration for Django. Ported from [django-bootstrap4](https://github.com/zostera/django-bootstrap4)\n\nDISCLAIMER: This is a port done over the weekend and is a very poorly featured\npackage. The only purpose for this currently is to provide a CSS to be used in\nyour project templates\n\n## Goal\n\nThe goal of this project is to seamlessly blend Django and PatternFly.\n\n## Requirements\n\nPython 3.9 or newer with Django >= 4.0 or newer.\n\n## Documentation\n\nThe full documentation is (will be) at https://django-patternly4.readthedocs.io/\n\n## Installation\n\n1. Install using pip:\n\n   ```shell script\n   pip install django-patternfly4\n   ```\n\n\n2. Add to `INSTALLED_APPS` in your `settings.py`:\n\n   ```python\n   INSTALLED_APPS = (\n       # ...\n       "patternfly",\n       # ...\n   )\n   ```\n\n3. In your templates, load the `patternfly` library and use the `patternfly_*` tags:\n\n## Example template\n\n```djangotemplate\n{% load patternfly %}\n\n<html>\n    <head>\n        {% patternfly_css %}\n    </head>\n    <body>\n        {% block patternfly_content %}\n            Main Content\n        {% endblock %}\n    </body>\n</html>\n```\n\n## Development\n\nInstall poetry\n\n```shell script\n$ pip install poetry\n```\n\n## Bugs and suggestions\n\nIf you have found a bug or if you have a request for additional functionality, please use the issue tracker on GitHub.\n\nhttps://github.com/ayaseen/django-patternfly4/issues\n\n## License\n\nYou can use this under BSD-3-Clause. See [LICENSE](LICENSE) file for details.\n\n## Author\n\nDeveloped and maintained by Amjad Yaseen\n\nPlease see [AUTHORS.md](AUTHORS.md) for a list of contributors.\n',
    'author': 'ayaseen',
    'author_email': 'amjad.a.yaseen@gmail.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://github.com/ayaseen/django-patternfly4',
    'package_dir': package_dir,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'extras_require': extras_require,
    'python_requires': '>=3.9,<4.0',
}


setup(**setup_kwargs)
