# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['events', 'events.migrations', 'events.tests']

package_data = \
{'': ['*'], 'events': ['templates/*', 'templates/events/*']}

install_requires = \
['django-filer', 'giant-mixins']

setup_kwargs = {
    'name': 'giant-events',
    'version': '0.2.5',
    'description': 'A small reusable package that adds an Events app to a project',
    'long_description': '# Giant Events\n\nA re-usable package which can be used in any project that requires a generic `Events` app. \n\nThis will include the basic formatting and functionality such as model creation via the admin.\n\n## Installation\n\nTo install with the package manager, run:\n\n    $ poetry add giant-events\n\nYou should then add `"events", "easy_thumbnails" and "filer"` to the `INSTALLED_APPS` in `base.py`.  \n\n\n## Configuration\n\nThis application exposes the following settings:\n\n- `EVENT_ADMIN_LIST_DISPLAY` is the field list for the admin index. This must be a list\n- `EVENT_ADMIN_FIELDSETS` allows the user to define the admin fieldset. This must be a list of two-tuples\n- `EVENT_ADMIN_READONLY_FIELDS` allows the user to configure readonly fields in the admin. This must be a list\n- `EVENT_ADMIN_SEARCH_FIELDS` allows the user to configure search fields in the admin. This must be a list\n- `EVENT_ADMIN_FILTER_FIELDS` allows the user to configure filter fields in the admin. This must be a list\n\nBy default the app will use the templates that are defined inside the app directory itself. However if you wish to override which template is used you will need to create a directory in the projects template directory\nThe structure should look something like this:\n\n```\ntemplates/\n    events/\n        index.html\n        detail.html\n```\n\n\n\n## URLs\n\nAdd the following to `core.urls` for general functionality:\n\n    path("events/", include("events.urls"), name="events"),\n\nIf you want to customize the urls to include a different path and/or templates, first you must import `from events import views as event_views` in `core.urls` and then you could add the following:\n\n    path("events/", event_views.EventIndex.as_view(template_name="event/index.html"), name="event-index"),\n    path("events/<slug:slug>/", event_views.EventDetail.as_view(template_name="event/detail.html"), name="event-detail"),\n \n ## Preparing for release\n \n In order to prep the package for a new release on TestPyPi and PyPi there is one key thing that you need to do. You need to update the version number in the `pyproject.toml`.\n This is so that the package can be published without running into version number conflicts. The version numbering must also follow the Semantic Version rules which can be found here https://semver.org/.\n \n ## Publishing\n \n Publishing a package with poetry is incredibly easy. Once you have checked that the version number has been updated (not the same as a previous version) then you only need to run two commands.\n \n    $ `poetry build` \n\nwill package the project up for you into a way that can be published.\n \n    $ `poetry publish`\n\nwill publish the package to PyPi. You will need to enter the username and password for the account which can be found in the company password manager',
    'author': 'Will-Hoey',
    'author_email': 'will.hoey@giantmade.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://github.com/giantmade/giant-events',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.6,<4.0',
}


setup(**setup_kwargs)
