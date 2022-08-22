# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['mkrst', 'mkrst_themes']

package_data = \
{'': ['*'],
 'mkrst_themes': ['classic/fonts/*',
                  'classic/html/*',
                  'classic/odt/*',
                  'classic/pdf/*',
                  'default/fonts/*',
                  'default/html/*',
                  'default/odt/*',
                  'default/pdf/*',
                  'overclock/fonts/*',
                  'overclock/html/*',
                  'overclock/odt/*',
                  'overclock/pdf/*']}

install_requires = \
['docutils>=0.10', 'rst2pdf>=0.99,<0.100']

entry_points = \
{'console_scripts': ['mkrst = mkrst:main']}

setup_kwargs = {
    'name': '2lazy2rest',
    'version': '0.1.2',
    'description': 'Effortless generation of PDF, HTML & ODT documents from RST (ReStructuredText)',
    'long_description': "##########\n2lazy2rest\n##########\n\nA simple way to produce short-to-medium document using *reStructuredText*\n\nMulti-format themes\n    Render the same document in HTML, ODT, PDF keeping the main visual identity\nUnified interface\n    - Tired of switching between rst2* tools having different arguments or behavior ?\n    - Would like to not lose *code-blocks* or some rendering options switching the output format ?\n\n    This tool try to address this\nMake your own theme\n    TODO: templates will be customizable easily (say, probably colors only)\n\nHow to use it\n#############\n\nDependencies\n============\n\nYou'll need **rst2pdf** to use all the features, other rst2* tools are coming from docutils.\n\nUsing\n=====\n\n.. code-block:: console\n\n    mkrst [-h] [--html] [--pdf] [--odt] [--theme THEME]\n                 [--themes-dir THEMES_DIR]\n                 FILE\n\noptional arguments:\n  -h, --help            show this help message and exit\n  --html                Generate HTML output\n  --pdf                 Generate PDF output\n  --odt                 Generate ODT output\n  --theme THEME         Use a different theme\n  --themes-dir THEMES_DIR\n                        Change the folder searched for theme\n\n\n.. code-block:: console\n\n    popo:~/2lazy2rest% ./mkrst test_page.rst --html --pdf\n    Using ./themes/default\n      html:  test_page.html\n       pdf:  test_page.pdf\n\n\nCustomizing\n===========\n\nMake a copy of ``themes/default``, edit to your needs the copy and use the **--theme** option with the name of your copy, that's All !\n\nExample\n-------\n\n.. code-block:: console\n\n   popo:~/2lazy2rest% cp -r themes/default themes/red\n   popo:~/2lazy2rest% sed -si 's/#FEFEFE/red/g' themes/red/html/stylesheet.css\n   popo:~/2lazy2rest% ./mkrst test_page.rst --html --theme red\n\nIssues\n######\n\n- ODT style is unfinished\n- PDF & HTML still needs more ReST coverage\n- No skin generation from template yet\n\n",
    'author': 'fdev31',
    'author_email': 'fdev31@gmail.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': None,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'entry_points': entry_points,
    'python_requires': '>=3.8,<4.0',
}


setup(**setup_kwargs)
