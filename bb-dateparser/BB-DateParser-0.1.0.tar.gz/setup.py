# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['dateparser', 'dateparser.utils']

package_data = \
{'': ['*']}

setup_kwargs = {
    'name': 'bb-dateparser',
    'version': '0.1.0',
    'description': 'Try to parse date into a format for datetime',
    'long_description': '# BB-DateParser\n\nAttempts to convert any written date into a datetime object. It will try to return the most likely format but you can use the `list_all = True` option to get all the results. To make it more useful for my needs (and easier to write :P), it only works for years 1000 - 2099.\n\n## Usage\n\n```python\n\nfrom dateparser.dateparser import DateParser\n\ndp = DateParser()\nmy_date = "October 1st, 1985 4:35pm"\n\ndate_fmt = dp.parse_date( my_date )\n\nprint( date_fmt )\n\'%B %dst, %Y %I:%M%p\'\n\n# To obtain a list of all the results\n\ndate_fmt_list = dp.parse_date( my_date, list_all = True )\n\nprint( str(date_fmt_list) )\n"[\'%B %dst, %Y %I:%M%p\']"\n\n# In this case only one result was found but was returned in list format\n# The DateParser class holds the data from the last result\n# This is cleared and recreated each time self.parse_date() is used\n# Below are the variables created from each date parsed\n\n# separated list of the date string\ndp.alldata = [\'October\', \' \', \'01\', \'st,\', \' \', \'1985\', \' \', \'04\', \':\', \'35\', \'PM\']\n\n# list of actual date data in dictionary form { \'alldata index\': str(data) }\ndp.data = { 0: \'October\', 2: \'1\', 5: \'1985\', 7: \'4\', 9: \'35\', 10: \'pm\' }\n\n# created datetime object from date string\ndp.dateObject = datetime.datetime(1985, 1, 1, 16, 35)\n\n# format code for datetime\ndp.formatting = \'%B %mst, %Y %I:%M%p\'\n\n# boolean - True only if successful in parsing the date\ndp.isValid = True\n\n# list of non date data pulled from date string\ndp.separators = [\' \', \'st,\', \' \', \' \', \':\']\n\n# list of all possible results (is returned when \'list_all\' = True)\ndp.format_list = [\'%B %dst, %Y %I:%M%p\']\n\n# DateParser is a subclass of DateData which is a subclass of the builtin\n# dict class. Therefore, all the parsing variables are also available through\n# the DateParser class.\n\n```',
    'author': 'Erik Beebe',
    'author_email': None,
    'maintainer': None,
    'maintainer_email': None,
    'url': None,
    'packages': packages,
    'package_data': package_data,
    'python_requires': '>=3.10,<4.0',
}


setup(**setup_kwargs)
