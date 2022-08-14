# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['yaex']

package_data = \
{'': ['*']}

setup_kwargs = {
    'name': 'yaex',
    'version': '0.1.1',
    'description': '',
    'long_description': '# Yet Another EX command library\n\nThis is a library based on the ex command. So, it works the same way :)\n\n## Usage\n\n```python\nfrom yaex import append, go_to_first_line, go_to, delete, insert, yaex\n\nresult = yaex(\n    append("Hello"),\n    append("World"),\n)\nprint(result)\n# >Hello\n# >World\n# >\n\nresult = yaex(\n    append("first line"),\n    append("second line"),\n    append("third line"),\n    go_to(2),\n    delete(),\n)\nprint(result)\n# >first line\n# >third line\n# >\n\nresult = yaex(\n    append("# yaex\\n\\nThis is a library based on the ex command.\\n"),\n    go_to_first_line(),\n    delete(),\n    insert("# Yet Another EX command library"),\n)\nprint(result)\n# ># Yet Another EX command library\n# >\n# >This is a library based on the ex command.\n# >\n```\n',
    'author': 'Emerson Max de Medeiros Silva',
    'author_email': 'emersonmx@gmail.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://github.com/emersonmx/yaex',
    'packages': packages,
    'package_data': package_data,
    'python_requires': '>=3.10,<4.0',
}


setup(**setup_kwargs)
