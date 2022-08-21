# -*- coding: utf-8 -*-
from setuptools import setup

modules = \
['aioratelimits']
setup_kwargs = {
    'name': 'aioratelimits',
    'version': '0.2.1',
    'description': '',
    'long_description': "# aioratelimits\n\nClient rate limiter. It enqueues function calls and run them as leaky bucket to\nensure specified rates.\n\n## Implementation\n\nLeaky bucket. We have one queue for requests and `count` number of workers.\nEach worker can handle one request per `delay` seconds\n\n## Install\n\n```\npip install aioratelimits\n```\n\n## Use\n\nThe following code prints not more than 2 lines per second.\n\n```python\nimport asyncio\nfrom aioratelimits import RateLimiter\n\n\nasync def critical_resource(i: int):\n    print('request:', i)\n\n\nasync def main():\n    async with RateLimiter(count=2, delay=1) as limiter:\n        await asyncio.gather(*(\n            limiter.run(critical_resource(i))\n            for i in range(10)\n        ))\n\n\nasyncio.run(main())\n```\n\nArguments to `RateLimiter`:\n- `count` - how many calls can we do in the specified interval\n- `delay` - the interval in seconds \n",
    'author': 'Dmitry Kostromin',
    'author_email': 'kupec-k@ya.ru',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://github.com/kupec/aioratelimits',
    'py_modules': modules,
    'python_requires': '>=3.8,<4.0',
}


setup(**setup_kwargs)
