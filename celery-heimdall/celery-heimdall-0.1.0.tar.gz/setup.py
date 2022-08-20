# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['celery_heimdall']

package_data = \
{'': ['*']}

install_requires = \
['celery>=5.2.7,<6.0.0', 'redis>=4.3.4,<5.0.0']

setup_kwargs = {
    'name': 'celery-heimdall',
    'version': '0.1.0',
    'description': 'Helpful celery extensions.',
    'long_description': '# celery-heimdall\n\n[![codecov](https://codecov.io/gh/TkTech/celery-heimdall/branch/main/graph/badge.svg?token=1A2CVHQ25Q)](https://codecov.io/gh/TkTech/celery-heimdall)\n![GitHub](https://img.shields.io/github/license/tktech/celery-heimdall)\n\nCelery Heimdall is a set of common utilities useful for the Celery background\nworker framework, built on top of Redis. It\'s not trying to handle every use\ncase, but to be an easy, modern, and maintainable drop-in solution for 90% of\nprojects.\n\n## Features\n\n- Globally unique tasks, allowing only 1 copy of a task to execute at a time, or\n  within a time period (ex: "Don\'t allow queuing until an hour has passed")\n- Global rate limiting. Celery has built-in rate limiting, but it\'s a rate limit\n  _per worker_, making it unsuitable for purposes such as limiting requests to\n  an API.\n\n## Installation\n\n`pip install celery-heimdall`\n\n## Usage\n\n### Unique Tasks\n\nImagine you have a task that starts when a user presses a button. This task\ntakes a long time and a lot of resources to generate a report. You don\'t want\nthe user to press the button 10 times and start 10 tasks. In this case, you\nwant what Heimdall calls a unique task:\n\n```python\nfrom celery import shared_task\nfrom celery_heimdall import HeimdallTask\n\n@shared_task(\n  base=HeimdallTask,\n  heimdall={\n    \'unique\': True\n  }\n)\ndef generate_report(customer_id):\n    pass\n```\n\nAll we\'ve done here is change the base Task class that Celery will use to run\nthe task, and passed in some options for Heimdall to use. This task is now\nunique - for the given arguments, only 1 will ever run at the same time.\n\nWhat happens if our task dies, or something goes wrong? We might end up in a\nsituation where our lock never gets cleared, called [deadlock][]. To work around\nthis, we add a maximum time before the task is allowed to be queued again:\n\n\n```python\nfrom celery import shared_task\nfrom celery_heimdall import HeimdallTask\n\n@shared_task(\n  base=HeimdallTask,\n  heimdall={\n    \'unique\': True,\n    \'unique_timeout\': 60 * 60\n  }\n)\ndef generate_report(customer_id):\n  pass\n```\n\nNow, `generate_report` will be allowed to run again in an hour even if the\ntask got stuck, the worker ran out of memory, the machine burst into flames,\netc...\n\nBy default, a hash of the task name and its arguments is used as the lock key.\nBut this often might not be what you want. What if you only want one report at\na time, even for different customers? Ex:\n\n```python\nfrom celery import shared_task\nfrom celery_heimdall import HeimdallTask\n\n@shared_task(\n  base=HeimdallTask,\n  heimdall={\n    \'unique\': True,\n    \'key\': lambda args, kwargs: \'generate_report\'\n  }\n)\ndef generate_report(customer_id):\n  pass\n```\nBy specifying our own key function, we can completely customize how we determine\nif a task is unique.\n\n#### Unique Interval Task\n\nWhat if we want the task to only run once in an hour, even if it\'s finished?\nIn those cases, we want it to run, but not clear the lock when it\'s finished:\n\n```python\nfrom celery import shared_task\nfrom celery_heimdall import HeimdallTask\n\n@shared_task(\n  base=HeimdallTask,\n  heimdall={\n    \'unique\': True,\n    \'unique_timeout\': 60 * 60,\n    \'unique_wait_for_expiry\': True\n  }\n)\ndef generate_report(customer_id):\n  pass\n```\n\nBy setting `unique_wait_for_expiry` to `True`, the task will finish, and won\'t\nallow another `generate_report()` to be queued until `unique_timeout` has\npassed.\n\n### Rate Limiting\n\nCelery offers rate limiting out of the box. However, this rate limiting applies\non a per-worker basis. There\'s no reliable way to rate limit a task across all\nyour workers. Heimdall makes this easy:\n\n```python\nfrom celery import shared_task\nfrom celery_heimdall import HeimdallTask\n\n@shared_task(\n  base=HeimdallTask,\n  heimdall={\n    \'times\': 2,\n    \'per\': 60\n  }\n)\ndef download_report_from_amazon(customer_id):\n  pass\n```\n\nThis says "every 60 seconds, only allow this task to run 2 times". If a task\ncan\'t be run because it would violate the rate limit, it\'ll be rescheduled.\n\nIt\'s important to note this does not guarantee that your task will run _exactly_\ntwice a second, just that it won\'t run _more_ than twice a second. Tasks are\nrescheduled with a random jitter to prevent the [thundering herd][] problem.\n\n\n## Inspirations\n\nThese are more mature projects which inspired this library, and which may\nsupport older versions of Celery & Python then this project.\n\n- [celery_once][], which is unfortunately abandoned and the reason this project\n  exists.\n- [celery_singleton][]\n- [This snippet][snip] by Vigrond, and subsequent improvements by various\n  contributors.\n\n\n[celery_once]: https://github.com/cameronmaske/celery-once\n[celery_singleton]: https://github.com/steinitzu/celery-singleton\n[deadlock]: https://en.wikipedia.org/wiki/Deadlock\n[thundering herd]: https://en.wikipedia.org/wiki/Thundering_herd_problem\n[snip]: https://gist.github.com/Vigrond/2bbea9be6413415e5479998e79a1b11a',
    'author': 'Tyler Kennedy',
    'author_email': 'tk@tkte.ch',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://github.com/tktech/celery-heimdall',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.7,<4.0',
}


setup(**setup_kwargs)
