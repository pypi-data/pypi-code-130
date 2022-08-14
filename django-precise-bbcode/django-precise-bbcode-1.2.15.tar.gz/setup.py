# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['precise_bbcode',
 'precise_bbcode.bbcode',
 'precise_bbcode.bbcode.defaults',
 'precise_bbcode.conf',
 'precise_bbcode.core',
 'precise_bbcode.migrations',
 'precise_bbcode.templatetags']

package_data = \
{'': ['*'], 'precise_bbcode': ['locale/fr/LC_MESSAGES/*']}

install_requires = \
['django>=3.2', 'pillow>=2.2.1']

setup_kwargs = {
    'name': 'django-precise-bbcode',
    'version': '1.2.15',
    'description': 'A django BBCode integration..',
    'long_description': '=====================\ndjango-precise-bbcode\n=====================\n\n*Django-precise-bbcode* is a Django application providing a way to create textual contents based on BBCodes.\n\n  BBCode is a special implementation of HTML. BBCode itself is similar in style to HTML, tags are enclosed in square brackets [ and ] rather than < and > and it offers greater control over what and how something is displayed.\n\nThis application includes a BBCode compiler aimed to render any BBCode content to HTML and allows the use of BBCodes tags in models, forms and admin forms. The BBCode parser comes with built-in tags (the default ones ; ``b``, ``u``, etc) and allows the use of smilies, custom BBCode placeholders and custom BBCode tags. These can be added in two different ways:\n\n* Custom tags can be defined in the Django administration panel and stored into the database ; doing this allows any non-technical admin to add BBCode tags by defining the HTML replacement string associated with each tag\n* Tags can also be manually registered to be used by the parser by defining a tag class aimed to render a given bbcode tag and its content to the corresponding HTML markup\n\n.. contents:: Table of Contents\n    :local:\n\n\nDocumentation\n-------------\n\nOnline browsable documentation is available at https://django-precise-bbcode.readthedocs.org.\n\n\nRequirements\n------------\n\n* Python 3.6+\n* Django 3.2+\n* PIL or Pillow (required for smiley tags)\n\nInstallation\n------------\n\nJust run:\n\n::\n\n  pip install django-precise-bbcode\n\nOnce installed you can configure your project to use *django-precise-bbcode* with the following steps.\n\nAdd ``precise_bbcode`` to ``INSTALLED_APPS`` in your project\'s settings module:\n\n.. code-block:: python\n\n  INSTALLED_APPS = (\n      # other apps\n      \'precise_bbcode\',\n  )\n\nThen install the models:\n\n.. code-block:: shell\n\n  python manage.py migrate\n\nUsage\n-----\n\nRendering bbcodes\n*****************\n\n*Django-precise-bbcode* comes with a BBCode parser that allows you to transform a textual content containing BBCode tags to the corresponding HTML markup. To do this, simply import the ``get_parser`` shortcut and use the ``render`` method of the BBCode parser::\n\n  >>> from precise_bbcode.bbcode import get_parser\n  >>> parser = get_parser()\n  >>> parser.render(\'[b]Hello [u]world![/u][/b]\')\n  \'<strong>Hello <u>world!</u></strong>\'\n\n*It\'s that easy!*\n\nAs you may need to render bbcodes inside one of your Django template, this parser can be used as a template filter or as a template tag after loading ``bbcode_tags``::\n\n  {% load bbcode_tags %}\n  {% bbcode entry.bbcode_content %}\n  {{ "[b]Write some bbcodes![/b]"|bbcode }}\n\nThe BBCode content included in the ``entry.bbcode_content``  field will be converted to HTML and displayed. The last statement will output ``<strong>Write some bbcodes!</strong>``.\n\nStoring bbcodes\n***************\n\nWhile you can use the Django built-in ``models.TextField`` to add your BBCode contents to your models, a common need is to store both the BBCode content and the corresponding HTML markup in the database. To address this *django-precise-bbcode* provides a ``BBCodeTextField``.\n\n.. code-block:: python\n\n  from django.db import models\n  from precise_bbcode.fields import BBCodeTextField\n\n  class Post(models.Model):\n      content = BBCodeTextField()\n\nThis field will store both the BBCode content and the correspondign HTML markup. The HTML content of such a field can then be displayed in any template by using its ``rendered`` attribute:\n\n::\n\n  {{ post.content.rendered }}\n\nAnd more...\n***********\n\nHead over to the `documentation <https://django-precise-bbcode.readthedocs.org>`_ for all the details on how to use the BBCode parser and how to define custom BBcode tags, placeholders and smilies.\n\nAuthors\n-------\n\nMorgan Aubert (`@ellmetha <https://github.com/ellmetha>`_) and contributors_\n\n.. _contributors: https://github.com/ellmetha/django-precise-bbcode/contributors\n\nLicense\n-------\n\nBSD. See ``LICENSE`` for more details.\n',
    'author': 'Morgan Aubert',
    'author_email': 'me@morganaubert.name',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://github.com/ellmetha/django-precise-bbcode',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.6,<4.0',
}


setup(**setup_kwargs)
