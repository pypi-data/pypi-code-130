# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['django_enum']

package_data = \
{'': ['*']}

install_requires = \
['Django>=3.2,<5.0']

extras_require = \
{'all': ['enum-properties>=1.1.1,<2.0.0',
         'django-filter>=21,<22',
         'djangorestframework>=3.9,<4.0'],
 'djangorestframework': ['djangorestframework>=3.9,<4.0'],
 'filters': ['django-filter>=21,<22'],
 'properties': ['enum-properties>=1.1.1,<2.0.0']}

setup_kwargs = {
    'name': 'django-enum',
    'version': '1.1.0',
    'description': 'Full and natural support for enumerations as Django model fields.',
    'long_description': "|MIT license| |PyPI version fury.io| |PyPI pyversions| |PyPI status| |Documentation Status|\n|Code Cov| |Test Status|\n\n.. |MIT license| image:: https://img.shields.io/badge/License-MIT-blue.svg\n   :target: https://lbesson.mit-license.org/\n\n.. |PyPI version fury.io| image:: https://badge.fury.io/py/django-enum.svg\n   :target: https://pypi.python.org/pypi/django-enum/\n\n.. |PyPI pyversions| image:: https://img.shields.io/pypi/pyversions/django-enum.svg\n   :target: https://pypi.python.org/pypi/django-enum/\n\n.. |PyPI status| image:: https://img.shields.io/pypi/status/django-enum.svg\n   :target: https://pypi.python.org/pypi/django-enum\n\n.. |Documentation Status| image:: https://readthedocs.org/projects/django-enum/badge/?version=latest\n   :target: http://django-enum.readthedocs.io/?badge=latest/\n\n.. |Code Cov| image:: https://codecov.io/gh/bckohan/django-enum/branch/main/graph/badge.svg?token=0IZOKN2DYL\n   :target: https://codecov.io/gh/bckohan/django-enum\n\n.. |Test Status| image:: https://github.com/bckohan/django-enum/workflows/test/badge.svg\n   :target: https://github.com/bckohan/django-enum/actions\n\n\n.. _Django: https://www.djangoproject.com/\n.. _GitHub: https://github.com/bckohan/django-enum\n.. _PyPI: https://pypi.python.org/pypi/django-enum\n.. _Enum: https://docs.python.org/3/library/enum.html#enum.Enum\n.. _enumerations: https://docs.python.org/3/library/enum.html#enum.Enum\n.. _ValueError: https://docs.python.org/3/library/exceptions.html#ValueError\n.. _DRY: https://en.wikipedia.org/wiki/Don%27t_repeat_yourself\n\nDjango Enum\n###########\n\nFull and natural support for enumerations_ as Django model fields.\n\nMany packages aim to ease usage of Python enumerations as model fields. Most\nwere made obsolete when Django provided ``TextChoices`` and ``IntegerChoices``\ntypes. The motivation for `django-enum <https://django-enum.readthedocs.io/en/latest/>`_\nwas to:\n\n* Always automatically coerce fields to instances of the Enum type.\n* Allow strict adherence to Enum values to be disabled.\n* Handle migrations appropriately. (See `migrations <https://django-enum.readthedocs.io/en/latest/usage.html#migrations>`_)\n* Integrate as fully as possible with Django_'s existing level of enum support.\n* Integrate with `enum-properties <https://pypi.org/project/enum-properties/>`_ to enable richer enumeration types.\n* Represent enum fields with the smallest possible column type.\n* Be as simple and light-weight an extension to core Django as possible.\n\n`django-enum <https://django-enum.readthedocs.io/en/latest/>`_ works in concert\nwith Django_'s built in ``TextChoices`` and ``IntegerChoices`` to provide a\nnew model field type, ``EnumField``, that resolves the correct native Django_\nfield type for the given enumeration based on its value type and range. For\nexample, ``IntegerChoices`` that contain values between 0 and 32767 become\n`PositiveSmallIntegerField <https://docs.djangoproject.com/en/stable/ref/models/fields/#positivesmallintegerfield>`_.\n\n.. code:: python\n\n    from django.db import models\n    from django_enum import EnumField\n\n    class MyModel(models.Model):\n\n        class TextEnum(models.TextChoices):\n\n            VALUE0 = 'V0', 'Value 0'\n            VALUE1 = 'V1', 'Value 1'\n            VALUE2 = 'V2', 'Value 2'\n\n        class IntEnum(models.IntegerChoices):\n\n            ONE   = 1, 'One'\n            TWO   = 2, 'Two',\n            THREE = 3, 'Three'\n\n        # this is equivalent to:\n        #  CharField(max_length=2, choices=TextEnum.choices, null=True, blank=True)\n        txt_enum = EnumField(TextEnum, null=True, blank=True)\n\n        # this is equivalent to\n        #  PositiveSmallIntegerField(choices=IntEnum.choices)\n        int_enum = EnumField(IntEnum)\n\n\n``EnumField`` **is more than just an alias. The fields are now assignable and\naccessible as their enumeration type rather than by-value:**\n\n.. code:: python\n\n    instance = MyModel.objects.create(\n        txt_enum=MyModel.TextEnum.VALUE1,\n        int_enum=3  # by-value assignment also works\n    )\n\n    assert instance.txt_enum == MyModel.TextEnum('V1')\n    assert instance.txt_enum.label == 'Value 1'\n\n    assert instance.int_enum == MyModel.IntEnum['THREE']\n    assert instance.int_enum.value == 3\n\n\n`django-enum <https://django-enum.readthedocs.io/en/latest/>`_ also provides\n``IntegerChoices`` and ``TextChoices`` types that extend from\n`enum-properties <https://pypi.org/project/enum-properties/>`_ which makes\npossible very rich enumeration fields.\n\n.. code:: python\n\n    from enum_properties import s\n    from django_enum import TextChoices  # use instead of Django's TextChoices\n    from django.db import models\n\n    class TextChoicesExample(models.Model):\n\n        class Color(TextChoices, s('rgb'), s('hex', case_fold=True)):\n\n            # name   value   label       rgb       hex\n            RED     = 'R',   'Red',   (1, 0, 0), 'ff0000'\n            GREEN   = 'G',   'Green', (0, 1, 0), '00ff00'\n            BLUE    = 'B',   'Blue',  (0, 0, 1), '0000ff'\n\n            # any named s() values in the Enum's inheritance become properties on\n            # each value, and the enumeration value may be instantiated from the\n            # property's value\n\n        color = EnumField(Color)\n\n    instance = TextChoicesExample.objects.create(\n        color=TextChoicesExample.Color('FF0000')\n    )\n    assert instance.color == TextChoicesExample.Color('Red')\n    assert instance.color == TextChoicesExample.Color('R')\n    assert instance.color == TextChoicesExample.Color((1, 0, 0))\n\n    # direct comparison to any symmetric value also works\n    assert instance.color == 'Red'\n    assert instance.color == 'R'\n    assert instance.color == (1, 0, 0)\n\n    # save by any symmetric value\n    instance.color = 'FF0000'\n\n    # access any enum property right from the model field\n    assert instance.color.hex == 'ff0000'\n\n    # this also works!\n    assert instance.color == 'ff0000'\n\n    # and so does this!\n    assert instance.color == 'FF0000'\n\n    instance.save()\n\n    # filtering works by any symmetric value or enum type instance\n    assert TextChoicesExample.objects.filter(\n        color=TextChoicesExample.Color.RED\n    ).first() == instance\n\n    assert TextChoicesExample.objects.filter(color=(1, 0, 0)).first() == instance\n\n    assert TextChoicesExample.objects.filter(color='FF0000').first() == instance\n\n\n.. note::\n\n    Consider using\n    `django-render-static <https://pypi.org/project/django-render-static/>`_\n    to make your enumerations DRY_ across the full stack!\n\nPlease report bugs and discuss features on the\n`issues page <https://github.com/bckohan/django-enum/issues>`_.\n\n`Contributions <https://github.com/bckohan/django-enum/blob/main/CONTRIBUTING.rst>`_\nare encouraged!\n\n`Full documentation at read the docs. <https://django-enum.readthedocs.io/en/latest/>`_\n\nInstallation\n------------\n\n1. Clone django-enum from GitHub_ or install a release off PyPI_ :\n\n.. code:: bash\n\n       pip install django-enum\n\n.. note::\n\n    ``django-enum`` has several optional dependencies that are not pulled in\n    by default. ``EnumFields`` work seamlessly with all Django apps that\n    work with model fields with choices without any additional work. Optional\n    integrations are provided with several popular libraries to extend this\n    basic functionality.\n\nIntegrations are provided that leverage\n`enum-properties <https://pypi.org/project/enum-properties/>`_ to make\nenumerations do more work and to provide extended functionality for\n`django-filter <https://pypi.org/project/django-filter/>`_  and\n`djangorestframework <https://www.django-rest-framework.org>`_.\n\n.. code:: bash\n\n    pip install enum-properties\n    pip install django-filter\n    pip install djangorestframework\n\nIf features are utilized that require a missing optional dependency an\nexception will be thrown.\n",
    'author': 'Brian Kohan',
    'author_email': 'bckohan@gmail.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://django-enum.readthedocs.io',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'extras_require': extras_require,
    'python_requires': '>=3.6,<4.0',
}


setup(**setup_kwargs)
