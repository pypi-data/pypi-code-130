# -*- coding: utf-8 -*-
from setuptools import setup

package_dir = \
{'': 'src'}

packages = \
['iife']

package_data = \
{'': ['*']}

setup_kwargs = {
    'name': 'invoke-iife',
    'version': '1.0.1',
    'description': 'Bringing the fun of immediately-invoked function expressions to Python!',
    'long_description': "# iife\n\n## Immediately-invoked function expressions in Python\n\nThe `iife` package provides a decorator function `iife` that calls the function/class it decorates and assigns the result to the name of the function/class.\n\nSome use cases include...\n\n## Creating an anonymous object.\n\nHave you ever written a class that you know will only have one instance? You can use the iife decorator to create that instance immediately.\n\n```python\nfrom iife import iife\n\n@iife\n@dataclass\nclass player:\n    x: int = 1\n    y: int = 2\n\n# player is an instance of the player class\nplayer.x # -> 1\n\n# The class cannot be reinstantiated because the name is shadowed.\nnew_player = player(x=3, y=4) # -> SyntaxError\n```\n\nThis might also be useful in library development to hide the implementation details of the class from the end user, who can only access the single instance.\n\n## Complex initialization.\n\nSometimes a variable needs to be initialized by complex logic that cannot be expressed as a single assignment. Traditionally, this can be done with temporarily setting the variable to a default value:\n\n```python\nx = None\ny = [1, 2, 3]\nfor i in y:\n    if i == 2:\n        x = i\n```\n\nWhy not do it with an IIFE? (To be honest, this isn't the best example, but it's more fun to do it like this.)\n\n```python\nfrom iife import iife\n\n@iife\ndef x() -> Optional[int]:\n    y = [1, 2, 3]\n    for i in y:\n        if i == 2:\n            return i\n```\n\n... And a bunch more. Maybe. Tbh this is mostly for fun.\n",
    'author': 'Tor Shepherd',
    'author_email': 'tor.aksel.shepherd@gmail.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://torshepherd.github.io/iife-py',
    'package_dir': package_dir,
    'packages': packages,
    'package_data': package_data,
    'python_requires': '>=3.7,<4.0',
}


setup(**setup_kwargs)
