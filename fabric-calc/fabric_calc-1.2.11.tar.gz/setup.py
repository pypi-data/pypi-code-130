# -*- coding: utf-8 -*-
from setuptools import setup

package_dir = \
{'': 'src'}

packages = \
['fabric_calc']

package_data = \
{'': ['*']}

install_requires = \
['rectpack>=0.2.2,<0.3.0']

setup_kwargs = {
    'name': 'fabric-calc',
    'version': '1.2.11',
    'description': 'Promail: The Python Email Automation Framework',
    'long_description': '# Fabric Calc\n\nList of rectangle, a rectangle is a tuple of two ints, (length, width)\n```python\n\nfrom fabric_calc.fabric_calc import calculate \n\n# length, width, quantity\nrectangles = [\n            (30, 40, 5),\n            (55, 36, 4),\n            (33, 16,1),\n            (20, 36,6),\n        ]\nprint(calculate(rectangles))\n\n```',
    'author': 'Antoine Wood',
    'author_email': 'antoinewood@gmail.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': None,
    'package_dir': package_dir,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
}


setup(**setup_kwargs)
