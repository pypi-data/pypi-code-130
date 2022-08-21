# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['nestd']

package_data = \
{'': ['*']}

setup_kwargs = {
    'name': 'nestd',
    'version': '0.3.0',
    'description': 'A package to extract your nested functions!',
    'long_description': '# nested\n\nExtract your nested functions!\n\n## Installation\n\n```python3\n    pip install nestd\n```\n\n\n## Usage\n\n```python3\nfrom nestd import nested, get_all_nested\n\n\ndef dummy_function():\n    test_variable = "hello, world"\n    def inner_function():\n        nonlocal test_variable\n        return test_variable\n\n\ndef dummy_function_with_two_inner_functions():\n    test_variable = "hello, world"\n    test_array = [1, 2, 3]\n    def inner_function():\n        nonlocal test_variable\n        return test_variable\n\n    def inner_function_2():\n        nonlocal test_array\n        return test_array[1:]\n\n\ndef test_nested_function():\n    inner_function = nested(dummy_function, "inner_function", test_variable="hello" )\n    assert "hello" == inner_function()\n\ndef test_2_nested_functions():\n    all_inner_functions = get_all_nested(dummy_function_with_two_inner_functions, "hello_world", [1,2])\n    inner_function, inner_function_2 = all_inner_functions\n\n    assert inner_function[0] == "inner_function"\n    assert inner_function[1]() == "hello_world"\n\n    assert inner_function_2[0] == "inner_function_2"\n    assert inner_function_2[1]() == [2]\n```\n\n\nTo perform a very deep nested search\n\n```python3\ndef dummy_function_with_nested_inner_functions():\n\n    test_array = [1, 2, 3]\n\n    def math():\n        nonlocal test_array\n\n        def sum():\n            nonlocal test_array\n\n            def sum_of_array():\n                nonlocal test_array\n                inside_arr = [random.randint(1, 10)] * len(test_array)\n                return test_array + inside_arr\n\n            def multi_of_array():\n                nonlocal test_array\n                inside_arr = [random.randint(1, 10)] * len(test_array)\n                for i in range(len(test_array)):\n                    inside_arr[i] = inside_arr[i] * test_array[i]\n                return inside_arr\n\n            ans = 0\n            for i in test_array:\n                ans += i\n            return ans\n\n        def multiply():\n            nonlocal test_array\n            ans = 1\n            for i in test_array:\n                ans = ans * i\n\n            return ans\n\n        return test_array\n\n    def stats():\n        nonlocal test_array\n\n        def mean():\n            nonlocal test_array\n            return sum(test_array) / len(test_array)\n\n        return test_array\n\n\ndef test_3_nested_functions():\n    inner_functions = get_all_deep_nested(\n        dummy_function_with_nested_inner_functions,\n        test_array=[1, 2, 3],\n    )\n\n    assert inner_functions["math"]() == [1, 2, 3]\n    assert inner_functions["sum"]() == 6\n    assert inner_functions["mean"]() == 2.0\n\n```\n\n## Contributor Guidelines\n\nFeel free to open an issue for any clarification or for any suggestions.\n\n\n## To Develop Locally\n\n1. `poetry install` to install the dependencies\n2. `pytest tests` to run the tests\n',
    'author': 'Sanskar Jethi',
    'author_email': 'sansyrox@gmail.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': None,
    'packages': packages,
    'package_data': package_data,
    'python_requires': '>=3.8,<4.0',
}


setup(**setup_kwargs)
