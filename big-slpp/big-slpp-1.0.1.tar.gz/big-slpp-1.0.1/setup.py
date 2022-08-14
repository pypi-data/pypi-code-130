# -*- coding: utf-8 -*-
from setuptools import setup

package_dir = \
{'': 'lib'}

packages = \
['big_slpp']

package_data = \
{'': ['*']}

setup_kwargs = {
    'name': 'big-slpp',
    'version': '1.0.1',
    'description': "SirAnthony's SLPP, but modernized code (also, trailing comma's)",
    'long_description': '#### SLPP\nSLPP is a simple lua-python data structures parser.\n\nLua data check:\n\n```lua\ndata = \'{ array = { 65, 23, 5 }, dict = { string = "value", array = { 3, 6, 4}, mixed = { 43, 54.3, false, string = "value", 9 } } }\'\n> data = assert(loadstring(\'return \' .. data))()\n> for i,j in pairs(data[\'dict\']) do print(i,j) end\nmixed   table: 0x2014290\nstring  value\narray   table: 0x2014200\n```\n\nParse lua data:\n\n```python\n>>> from slpp import slpp as lua\n>>> data = lua.decode(\'{ array = { 65, 23, 5 }, dict = { string = "value", array = { 3, 6, 4}, mixed = { 43, 54.3, false, string = "value", 9 } } }\')\n>>> print data\n{\'array\': [65, 23, 5], \'dict\': {\'mixed\': {0: 43, 1: 54.33, 2: False, 4: 9, \'string\': \'value\'}, \'array\': [3, 6, 4], \'string\': \'value\'}}\n```\n\nDump python object:\n\n```python\n>>> lua.encode(data)\n\'{array = {65,23,5},dict = {mixed = {43,54.33,false,9,string = "value"},array = {3,6,4},string = "value"}}\'\n```\n\nDump test:\n\n```lua\n> data = assert(loadstring(\'return \' .. \'{array = {65,23,5,},dict = {mixed = {43,54.33,false,9,string = "value",},array = {3,6,4,},string = "value",},}\'))()\n> print(data[\'dict\'])\ntable: 0x1b64ea0\n> for i,j in pairs(data[\'dict\']) do print(i,j) end\nmixed   table: 0x880afe0\narray   table: 0x880af60\nstring  value\n```\n',
    'author': 'NostraDavid',
    'author_email': '55331731+nostradavid@users.noreply.github.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://github.com/NostraDavid/big-slpp',
    'package_dir': package_dir,
    'packages': packages,
    'package_data': package_data,
    'python_requires': '>=3.9,<4.0',
}


setup(**setup_kwargs)
