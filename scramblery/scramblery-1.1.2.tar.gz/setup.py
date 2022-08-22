# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['scramblery']

package_data = \
{'': ['*']}

setup_kwargs = {
    'name': 'scramblery',
    'version': '1.1.2',
    'description': '',
    'long_description': '# Scramblery\nA simple tool to scramble your images or only faces from images or videos\n\n#### Purpose of Package\n The purpose of this package is the creating scrambled images from images or videos. User can either scramble the whole image or only facial area.\n This is very useful tool in psychology experiments especially if you are working with faces.\n\n#### **Features**\n- Scramble whole image with desired degree of scrambling\n- Scramble only facial area with desired degree of scrambling\n- Scramble only facial area in a video (useful for dynmaic stimuli) with desired degree of scrambling\n\n#### Installation\n- The package can be found in pypi. To install the package, run the following command in the terminal:\n- `pip install scramblery`\n#### Author\n  -  Main Maintainer: [Enes ALTUN]\n\n### Contributon\n Any kind of contribution is welcome. Thanks.',
    'author': 'altunenes',
    'author_email': 'enesaltun2@gmail.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://github.com/altunenes/scramblery',
    'packages': packages,
    'package_data': package_data,
    'python_requires': '>=3.8,<4.0',
}


setup(**setup_kwargs)
