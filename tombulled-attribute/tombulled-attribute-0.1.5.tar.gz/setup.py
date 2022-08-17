# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['attribute']

package_data = \
{'': ['*']}

setup_kwargs = {
    'name': 'tombulled-attribute',
    'version': '0.1.5',
    'description': 'Attribute management made easy',
    'long_description': '# attribute\nAttribute management made easy\n\n## Installation\n```console\npip install git+https://github.com/tombulled/attribute@main\n```\n\n## Usage\n### Custom Attribute\n```python\nfrom attribute import Attribute\n\nclass Foo:\n    bar: str = "hello!"\n```\n```python\n>>> bar = Attribute("bar")\n>>> bar.get(Foo)\n"hello!"\n```\n\n### Bundled Attribute\n```python\nimport attribute\n\nclass Foo:\n    pass\n```\n```python\n>>> attribute.name.get(Foo)\n"Foo"\n```',
    'author': 'Tom Bulled',
    'author_email': '26026015+tombulled@users.noreply.github.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://github.com/tombulled/attribute',
    'packages': packages,
    'package_data': package_data,
    'python_requires': '>=3.8,<4.0',
}


setup(**setup_kwargs)
