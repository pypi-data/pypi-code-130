# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['bareasgi_static']

package_data = \
{'': ['*']}

install_requires = \
['aiofiles>=0.7,<0.8', 'bareASGI>=4.0.0,<5.0.0']

setup_kwargs = {
    'name': 'bareasgi-static',
    'version': '4.1.0',
    'description': 'Static file support for bareASGI',
    'long_description': "# bareasgi-static\n\nStatic file support for [bareASGI](http://github.com/rob-blackbourn/bareasgi) (read the [documentation](https://rob-blackbourn.github.io/bareASGI-static/))\n\n## Overview\n\nThis package provides support for serving static files to bareasgi.\n\n## Usage\n\nThe following example serves a single file.\n\n```python\nimport uvicorn\nimport os.path\nfrom bareasgi import Application\nfrom bareasgi_static import file_response\n\nhere = os.path.abspath(os.path.dirname(__file__))\n\nasync def http_request_callback(request):\n    return await file_response(request, 200, os.path.join(here, 'file_stream.html'))\n\napp = Application()\napp.http_router.add({'GET'}, '/example1', http_request_callback)\n\nuvicorn.run(app, port=9010)\n\n```\n\nThe next example serves files below a given directory.\n\n```python\nimport os.path\nimport uvicorn\nfrom bareasgi import Application\nfrom bareasgi_static import add_static_file_provider\n\nhere = os.path.abspath(os.path.dirname(__file__))\n\napp = Application()\nadd_static_file_provider(app, os.path.join(here, simple_www), index_filename='index.html')\n\nuvicorn.run(app, port=9010)\n```\n",
    'author': 'Rob Blackbourn',
    'author_email': 'rob.blackbourn@gmail.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://github.com/rob-blackbourn/bareASGI-static',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.8,<4.0',
}


setup(**setup_kwargs)
