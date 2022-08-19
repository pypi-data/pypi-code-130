# -*- coding: utf-8 -*-
from setuptools import setup

package_dir = \
{'': 'src'}

packages = \
['O365_notifications']

package_data = \
{'': ['*']}

install_requires = \
['marshmallow>=3.17.0,<4.0.0', 'requests>=2.28.1,<3.0.0']

extras_require = \
{':extra == "O365"': ['O365>=2.0.19,<3.0.0']}

setup_kwargs = {
    'name': 'o365-notifications',
    'version': '0.1.1',
    'description': 'Pythonic handler for O365 Streaming & Push Notifications',
    'long_description': "******************\nO365-notifications\n******************\n\n.. image:: https://img.shields.io/pypi/v/O365-notifications\n    :target: https://pypi.org/project/O365-notifications\n    :alt: PyPI version\n.. image:: https://github.com/rena2damas/O365-notifications/actions/workflows/ci.yaml/badge.svg\n    :target: https://github.com/rena2damas/O365-notifications/actions/workflows/ci.yaml\n    :alt: CI\n.. image:: https://codecov.io/gh/rena2damas/O365-notifications/branch/master/graph/badge.svg\n    :target: https://app.codecov.io/gh/rena2damas/O365-notifications/branch/master\n    :alt: codecov\n.. image:: https://img.shields.io/badge/code%20style-black-000000.svg\n    :target: https://github.com/psf/black\n    :alt: code style: black\n.. image:: https://img.shields.io/badge/License-MIT-yellow.svg\n    :target: https://opensource.org/licenses/MIT\n    :alt: license: MIT\n\n**O365-notifications** is a *pythonic* implementation for the Notification services\nfrom Office 365. There are currently 2 ways for receiving notifications:\n\n* `Push Notifications <https://docs.microsoft.com/en-us/previous-versions/office/\n  office-365-api/api/beta/notify-rest-operations-beta>`__\n* `Stream Notifications <https://docs.microsoft.com/en-us/previous-versions/office/\n  office-365-api/api/beta/notify-streaming-rest-operations>`__\n\nThe versions on these are beta. For more details, see its documentation.\n\nThis approach is built on top of the current `O365 <https://github\n.com/O365/python-o365>`__ package. You are recommended to look into its\ndocumentation for advance setups.\n\nNotification strategies\n=======================\nAs mentioned, there currently 2 supported notification types in *O365*: **push** and\n**streaming**.\n\nAs of now, this project relies on *Outlook REST Beta API*. But because this API is\nnow deprecated and will be decommissioned, a transition to *Microsoft Graph API* is\nrequired. See `this <Important-note-⚠️>`__ section for more details.\n\nPush notifications\n------------------\nThis project does not contain an implementation for this type of notification.\nTherefore, contributions are more than welcome.\n\n*O365* documentation on push notifications can be found `here <https://docs.microsoft\n.com/en-us/previous-versions/office/office-365-api/api/beta/notify-rest-operations\n-beta>`__.\n\nStreaming notifications\n-----------------------\nThis project provides an implementation for this type of notification. A quick example\non how to use it is found below:\n\n.. code-block:: python\n\n    import O365\n    from O365_notifications.base import O365NotificationHandler\n    from O365_notifications.constants import O365EventType\n    from O365_notifications.streaming import O365StreamingSubscriber\n\n    account = O365.Account(...)\n    mailbox = account.mailbox()\n\n    # create a new streaming subscriber\n    subscriber = O365StreamingSubscriber(parent=account)\n\n    # ... and subscribe to resource events\n    resource = mailbox.inbox_folder()\n    events = [O365EventType.CREATED]\n    subscriber.subscribe(resource=resource, events=events)\n\n    # subscriber keeps track of active subscriptions\n    assert len(subscriber.subscriptions) == 1\n\n    # implement a notification handler for customized behavior\n    subscriber.start_streaming(handler=O365NotificationHandler())\n\n*O365* documentation on streaming notifications can be found `here <https://docs\n.microsoft.com/en-us/previous-versions/office/office-365-api/api/beta/\nnotify-streaming-rest-operations>`__.\n\nImportant note ⚠️\n=================\nAs communicated by *Microsoft* `here <https://developer.microsoft.com/en-us/graph/\nblogs/outlook-rest-api-v2-0-deprecation-notice>`__, The ``v2.0`` REST endpoint will be\nfully decommissioned in November 2022, and the ``v2.0`` documentation will be removed\nshortly after.\n\nWhat does it mean to this package?\n----------------------------------\nLet's see what it means for each one of the notification types:\n\nPush notifications\n^^^^^^^^^^^^^^^^^^\nPush notifications will be moved to *Microsoft Graph*, and go under the name of\n**change notifications**. Its documentation can be found `here <https://docs\n.microsoft.com/en-us/graph/api/resources/webhooks?view=graph-rest-1.0)>`__.\n\nTransitioning to the *Microsoft Graph* should be a simple and straightforward task.\n\nStreaming notifications\n^^^^^^^^^^^^^^^^^^^^^^^\nUnfortunately *Microsoft* will not port this service to *Microsoft Graph*. Therefore, as\nof November 2022, the current implementation in this project will be obsolete. More\ndetails on that can be found `here <https://docs.microsoft.com/en-us/outlook/rest/\ncompare-graph>`__.\n\nTests & linting\n===============\nRun tests with ``tox``:\n\n.. code-block:: bash\n\n    # ensure tox is installed\n    $ tox\n\nRun linter only:\n\n.. code-block:: bash\n\n    $ tox -e lint\n\nOptionally, run coverage as well with:\n\n.. code-block:: bash\n\n    $ tox -e coverage\n\nLicense\n=======\nMIT licensed. See `LICENSE <LICENSE>`__.\n",
    'author': 'Renato Damas',
    'author_email': 'rena2damas@gmail.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://github.com/rena2damas/O365-notifications',
    'package_dir': package_dir,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'extras_require': extras_require,
    'python_requires': '>=3.9,<4.0',
}


setup(**setup_kwargs)
