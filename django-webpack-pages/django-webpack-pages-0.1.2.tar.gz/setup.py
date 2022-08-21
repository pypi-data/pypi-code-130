# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['webpack_pages']

package_data = \
{'': ['*']}

install_requires = \
['Django>=3.0', 'Jinja2>=3.0', 'django-webpack-loader>=1.5.0,<2.0.0']

setup_kwargs = {
    'name': 'django-webpack-pages',
    'version': '0.1.2',
    'description': 'Use webpack with your multi-page, multi-lingual django webapp',
    'long_description': '# django-webpack-pages\n\n[![PyPI version](https://badge.fury.io/py/django-webpack-pages.svg)](https://pypi.org/project/django-webpack-pages/)\n[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)\n\nUse webpack with your multi-page, multi-lingual django webapp.\n\nThis project is based on [django-webpack-loader](https://pypi.org/project/django-webpack-loader/)\nwhich handles the connection to webpack.\nConsider using [webpack-critical-pages](https://www.npmjs.com/package/webpack-critical-pages) as well\nif you are interested in speedups.\n\nPut the following in your settings file:\n\n```python\nWEBPACK_PAGES = {\n    "CRITICAL_CSS_ENABLED": True,\n    "ROOT_PAGE_DIR": osp.join(BASE_DIR, "pages"),\n    "STATICFILE_BUNDLES_BASE": "bundles/{locale}/",  # should end in /\n}\n\nSTATICFILES_FINDERS = (\n    "webpack_pages.pageassetfinder.PageAssetFinder",\n    # ... and more of your choosing:\n    "django.contrib.staticfiles.finders.FileSystemFinder",\n    "django.contrib.staticfiles.finders.AppDirectoriesFinder",\n)\n\n# configure the loaded page directories and add the WebpackExtension\nTEMPLATES = [\n    {\n        "BACKEND": "django_jinja.backend.Jinja2",\n        "DIRS": [osp.join(BASE_DIR, "templates"), osp.join(BASE_DIR, "pages")]\n        + [osp.join(BASE_DIR, app, "pages") for app in GRAZBALL_APPS]\n        + [osp.join(BASE_DIR, app, "components") for app in GRAZBALL_APPS],\n        "APP_DIRS": True,\n        "OPTIONS": {\n            # ...\n            "extensions": [\n                # ...\n                "webpack_pages.jinja2ext.WebpackExtension",\n            ],\n        }\n    }\n]\n```\n\nUsing `webpack_loader.contrib.pages` you can register entrypoints for corresponding pages in templates.\n\nAt the top of your individual page, do:\n\n```jinja2\n{% extends "layout.jinja" %}\n{% do register_entrypoint("myapp/dashboard") %}\n```\n\nIn the layout\'s (base template\'s) head, place the following:\n\n```jinja2\n<!DOCTYPE html>\n{% do register_entrypoint("main") %}\n<html lang="{{ LANGUAGE_CODE }}">\n<head>\n  ...\n  {{ render_css() }}\n</head>\n<body>\n  ...\n  {{ render_js() }}\n</body>\n```\n\nThis will load the registered entrypoints in order (`main`, then `myapp/dashboard`) and automatically inject\nthe webpack-generated css and js. It also supports critical css injection upon first request visits.\n',
    'author': 'MrP01',
    'author_email': 'peter@waldert.at',
    'maintainer': 'None',
    'maintainer_email': 'None',
    'url': 'https://github.com/MrP01/django-webpack-pages',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.8,<4.0',
}


setup(**setup_kwargs)
