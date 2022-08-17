# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['annotate']

package_data = \
{'': ['*']}

install_requires = \
['attribute>=0.1.4,<0.2.0']

setup_kwargs = {
    'name': 'tombulled-annotate',
    'version': '0.1.11',
    'description': 'Python Annotation System Inspired by Java Annotations',
    'long_description': "# annotate\nPython Annotation System Inspired by Java Annotations\n\n## About\nAnnotations are tags that store object metadata (e.g. for functions/classes)\n\n## Installation\n```console\npip install git+https://github.com/tombulled/annotate\n```\n\n## Usage\n\n### Marker\nAn annotation with a fixed value\n```python\nimport annotate\n\n@annotate.marker\ndef deprecated() -> bool:\n    return True\n\n@deprecated\ndef foo():\n    pass\n```\n\n```python\n>>> annotate.get_annotations(foo)\n{'deprecated': True}\n```\n\n### Annotation\nAn annotation with a configurable value\n```python\nimport annotate\n\n@annotate.annotation\ndef metadata(*, author: str, version: str) -> dict:\n    return dict(\n        author = author,\n        version = version,\n    )\n\n@metadata(author='sam', version='1.0.1')\ndef foo():\n    pass\n```\n\n```python\n>>> annotate.get_annotations(foo)\n{'metadata': {'author': 'sam', 'version': '1.0.1'}}\n```\n\n## Repeatable Annotation\nAn annotation that can be used to annotate the same object multiple times\n```python\nimport annotate\n\n@annotate.annotation(repeatable=True)\ndef tag(tag: str, /) -> str:\n    return tag\n\n@tag('awesome')\n@tag('cool')\n@tag('funky')\ndef foo():\n    pass\n```\n\n```python\n>>> annotate.get_annotations(foo)\n{'tag': ['funky', 'cool', 'awesome']}\n```\n\n## Inherited Annotation\nAn annotation that gets added to subclasses of an annotated class\n```python\nimport annotate\n\n@annotate.annotation(inherited=True)\ndef identifier(identifier: str, /) -> str:\n    return identifier\n\n@identifier('abc')\nclass Class:\n    pass\n\nclass Subclass(Class):\n    pass\n```\n\n```python\n>>> annotate.get_annotations(Class)\n{'identifier': 'abc'}\n>>> annotate.get_annotations(Subclass)\n{'identifier': 'abc'}\n```\n\n## Targetted Annotation\nAn annotation that targets objects of specific types\n```python\nimport annotate\nimport types\n\n@annotate.annotation(targets=(types.FunctionType,))\ndef description(description: str, /) -> str:\n    return description\n\n@description('A really cool function')\ndef foo():\n    pass\n```\n\n```python\n>>> annotate.get_annotations(foo)\n{'description': 'A really cool function'}\n```\n\n### Non-Stored Annotation\n```python\nimport annotate\n\n@annotate.annotation(stored=False)\ndef author(name: str, /) -> None:\n    pass\n\n@author('Tim')\ndef foo():\n    pass\n```\n\n```python\n>>> annotate.get_annotations(foo)\n{}\n```",
    'author': 'Tom Bulled',
    'author_email': '26026015+tombulled@users.noreply.github.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://github.com/tombulled/annotate',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.8,<4.0',
}


setup(**setup_kwargs)
