# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['multilookupdict']

package_data = \
{'': ['*']}

setup_kwargs = {
    'name': 'multilookupdict',
    'version': '0.1.6',
    'description': 'A dict-like container that allows multiple keys to address the same value.',
    'long_description': '# Multi-Lookup-Dict\n\n### A `dict`-like container that allows multiple keys to address the same value.\n<br/>\n\n## Installation\n\n`pip install multilookupdict`\n\n\n## Usage\n\n```python\n>>> d = MultiLookupDict()\n>>> d["a_key"] = "some_value"\n>>> d.map_key("a_key", "another_key") # Make "another_key" an alias of "a_key"\n```\n\nImplemented as two dicts:\n    - `MultiLookupDict._data` holds the \'canonical key\' and value\n    - `MultiLookupDict._key_to_canonical_map` maps \'alias keys\' onto canonical keys.\n        (Canonical keys are mapped to themselves in this dict)\n\nExternally, all keys (canonical and alias) are treated identically,\nand all refer to the same value, unless a key is reassigned to another value using `map_key`.\n\n\nMulti-key lookups and assignments\n---------------------------------\n\nIterables of keys can also be accessed, set, and mapped.\n\n```python\n>>> d = MultiLookupDict()\n>>> d[("key_a", "key_b", "key_c")] = "some_value"\n>>> d["key_a"] == "some_value"\n```\nWhere items are accessed with multiple keys, all distinct matching values are returned\nas a list (where multiple keys are requested, the result is always a list, for consistency)\n```python\n>>> d["key_d"] = "some_other_value" # Add a distinct value\n>>> d[("key_a", "key_b", "key_d")] == ["some_value", "some_other_value"]\n\n\n>>> d.map_key("key_a", ("key_e", "key_f")) # Also do multiple mappings\n```\n\nTo use a tuple as a _single_ key, rather than a group of independent keys, make sure it is\ncontained within another iterable, i.e. `d[(("tuple_part1", "tuple_part2"),)] = "some value"`. \nRemember that when accessing this tuple-key, a list of items will be returned.\n\n\n\nMethods\n-------\n\n<dl>\n<dt>\n<code>__setitem__(key/iterable_of_keys, value)</code>\n</dt>\n    <dd>Sets a key to the value. If a (non-string) iterable is provided\n    as key, each key will be assigned the value.</dd>\n<dt><code>__getitem__(key/iterable_of_keys)</code></dt>\n    <dd>Gets a value from a key. If a (non-string) iterable is provided as a key, a list\n    of distinct values matching all provided keys will be returned.</dd>\n<dt><code>map_key(existing_key, new_key)</code></dt>\n    <dd>Assign the value of one key to another key. Both keys\n    now point to the same value.</dd>\n<dt><code>keys()</code></dt>\n    <dd>Returns all keys in MultiLookupDict. Returned keys refer to same or different objects.</dd>\n<dt><code>values()</code></dt>\n    <dd>[Same as <code>dict.values</code>]</dd>\n<dt><code>items()</code></dt>\n    <dd>Same as <code>dict.items</code>, except "key" part of the tuple is a <code>set</code> of keys for the corresponding value</dd>\n<dt><code>pop(key)</code><dd>\n    <dd>Same as <code>dict.pop</code>. All keys pointing to value are removed.</dd>\n<dt><code>aliases(key, omit_requested_key=False)</code></dt>\n    <dd>Returns all aliases of a given key, including the key provided. (Set <code>omit_requested_key</code> to <code>True</code> to exclude the provided key.)</dd>\n</dl>',
    'author': 'Richard Hadden',
    'author_email': 'richard.hadden@oeaw.ac.at',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://github.com/richardhadden/multilookupdict',
    'packages': packages,
    'package_data': package_data,
    'python_requires': '>=3.9,<4.0',
}


setup(**setup_kwargs)
