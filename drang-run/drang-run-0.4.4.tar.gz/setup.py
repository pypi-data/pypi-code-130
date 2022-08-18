# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['drang_run']

package_data = \
{'': ['*']}

install_requires = \
['click>=8.0.3,<9.0.0']

entry_points = \
{'console_scripts': ['run = drang_run:run']}

setup_kwargs = {
    'name': 'drang-run',
    'version': '0.4.4',
    'description': 'Generate a run of integers or characters. Similar to jot and seq.',
    'long_description': '=========\ndrang-run\n=========\n\n  A simple command line tool to print sequences of numbers.\n\n``drang-run`` is comparable to  `jot`_ or `seq`_, but with a more intuitive interface. It was inspired (and named after) `a post by Dr. Drang`_.\n\nInstallation\n============\n\nJust install like any other package:\n\n.. code-block:: console\n\n   $ pip3 install drang-run\n\nThis will install the ``run`` command.\n\n.. code-block:: console\n\n   $ run --version\n   run, version 0.4.4\n\nUsage\n=====\n\nBasic usage includes up to three arguments:\n\n::\n\n   run [START] STOP [STEP]\n\n``[START]`` and ``[STEP]`` are optional and default to 1.\n\n.. code-block:: console\n\n    $ run 4\n    1\n    2\n    3\n    4\n    $ run 5 8\n    5\n    6\n    7\n    8\n    $ run 0 10 3\n    0\n    3\n    6\n    9\n\nReverse the sequence with ``-r``:\n\n.. code-block:: console\n\n    $ run 4 -r\n    4\n    3\n    2\n    1\n\nOr switch the arguments:\n\n.. code-block:: console\n\n   $ run 4 1 -1\n   4\n   3\n   2\n   1\n\n.. note::\n    ``run`` will try to guess the correct direction for the sequence based on the arguments. The example above could be simply written as ``run 4 1``.\n\n    For conflicting sets of arguments, the values for START and STOP will take precedence over STEP. So ``run 1 4 -1`` will be the same as ``run 1 4 1``.\n\n    The only exeption to this is ``STEP = 0`` which will cause an error.\n\n    This also means that ``run`` will almost never produce an empty output because at least ``START`` will be part of the sequence.\n\nFormat the output with ``--format``. The option accepts any kind of `Python format string`_.\n\n.. code-block:: console\n\n    $ run 998 1002 --format "{: >4}."\n     998.\n     999.\n    1000.\n    1001.\n    1002.\n\nYou can use decimals for ``[START]``, ``STOP`` and ``[STEP]``:\n\n.. code-block:: console\n\n    $ run 1.1 1.5 .15\n    1.1\n    1.25\n    1.4\n\n.. note::\n    If at least one argument is a decimal, the output will be formatted as decimals as well.\n\n    .. code-block:: console\n\n        $ run 1.0 4 1\n        1.0\n        2.0\n        3.0\n        4.0\n\n    You can always change this by using appropriate format strings.\n\n    .. code-block:: console\n\n        $ run 1.0 4 1 --format "{:g}"\n        1\n        2\n        3\n        4\n\nUsing letters for ``[START]`` and ``STOP`` will generate character sequences:\n\n.. code-block:: console\n\n    $ run d g\n    d\n    e\n    f\n    g\n\nBy default, the items are separated by a newline character ``\\n``, but you can change this with ``-s``:\n\n.. code-block:: console\n\n    $ run d g -s "\\t"\n    d       e       f       g\n\nRun additional sequences with ``--also START STOP STEP``:\n\n.. code-block:: console\n\n    $ run 1 2 --also 3 4 1\n    1-3\n    1-4\n    2-3\n    2-4\n\n.. note::\n    ``--also`` requires all three arguments to be present.\n\nOf course, this can be used with characters and be formatted:\n\n.. code-block:: console\n\n    $ run 1 2 --also b c 1 --format "{0:02}. {1}_{1}"\n    01. a_a\n    01. b_b\n    02. a_a\n    02. b_b\n\n.. note::\n    The sequences can be referenced in the format string by order of appearance. ``-r`` will reverse *all* sequences.\n\nSince version 0.4.0 you can define variables with the ``--def`` option. A variable can be set to a simple arithmetic expression that is evaluated with the current counter values. Similar to the format string (``-f``) the counters can be referenced with ``{0}``, ``{1}`` and so on. All defined variables are initialized with ``0`` and can be used in other expressions, even in the definition of themselves.\n\n.. code-block:: console\n\n    $ run 4 --also 1 3 1 --def sum "{0}+{1}" --def akk "{akk}+{sum}" --format "{0} + {1} = {sum} ({akk})"\n    1 + 1 = 2 (2)\n    1 + 2 = 3 (5)\n    1 + 3 = 4 (9)\n    2 + 1 = 3 (12)\n    2 + 2 = 4 (16)\n    2 + 3 = 5 (21)\n    3 + 1 = 4 (25)\n    3 + 2 = 5 (30)\n    3 + 3 = 6 (36)\n    4 + 1 = 5 (41)\n    4 + 2 = 6 (47)\n    4 + 3 = 7 (54)\n\nThe expressions allow for some additional functions to be used. Notably the\n``randint(max)`` and ``rand()`` functions for genrating random numbers:\n\n.. code-block:: console\n\n    $ run 10 --def r "randint(100)" --format "{r}" -s ,\n    51,0,55,50,56,43,20,5,51,90\n\n.. note::\n    The expressions are evaluated using the `simpleeval`_ module. Read the docs to see, what expressions are possible. In general, the basic arithmetic operators (``+``, ``-``, ``*``, ``/``, ``*``, ``//``) are supported.\n\nIn version 0.4.3 the ``--filter`` option was added to filter out some values from the run. The option requires an expression similar to ``--def`` that evaluates to a\nboolean value. Any iteration that evaluates to ``False`` will be omitted from the run.\n\n.. code-block:: console\n\n    $ run 100 --filter "{}%3==0 and {}%5==0"\n    15\n    30\n    45\n    60\n    75\n    90\n\nExamples\n========\n\nGenerating a CSV file with a lists of decimal, binary and hexadecimal numbers:\n\n.. code-block:: console\n\n    $ echo "dec,bin,oct,hex" > hostnames.csv\n    $ run 0 255 -f "{0:2},{0:08b},{0:02o},{0:02X}" >> numbers.csv\n\n\nGenerating a list of computers in a network with hostnames and IP.\n\n.. code-block:: console\n\n    $ echo "room,hostname,ip" > hostnames.csv\n    $ run 4 --also 1 24 1 --also 1 16 1 -f "{0}{1:02},r{0}{1:02}-{2:02},18.45.{1}{0}.{2}" >> hostnames.csv\n\n\n.. _jot: https://www.unix.com/man-page/osx/1/jot/\n.. _seq: https://www.unix.com/man-page/osx/1/seq/\n.. _a post by Dr. Drang: https://leancrew.com/all-this/2020/09/running-numbers/\n.. _pip: http://www.pip-installer.org/\n.. _Python format string: https://docs.python.org/3.6/library/string.html#formatstrings\n.. _simpleeval: https://github.com/danthedeckie/simpleeval\n',
    'author': 'J. Neugebauer',
    'author_email': 'github@neugebauer.cc',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'http://github.com/jneug/drang-run',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'entry_points': entry_points,
    'python_requires': '>=3.6.2,<4.0.0',
}


setup(**setup_kwargs)
