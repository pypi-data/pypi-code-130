# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['fast_dash', 'tests']

package_data = \
{'': ['*'], 'fast_dash': ['assets/*']}

install_requires = \
['Flask>=2.0.2,<3.0.0',
 'Pillow>=9.2.0,<10.0.0',
 'dash-bootstrap-components>=1.0.2,<2.0.0',
 'dash>=2.6.1,<3.0.0',
 'plotly>=5.5.0,<6.0.0']

setup_kwargs = {
    'name': 'fast-dash',
    'version': '0.1.7',
    'description': 'Build Machine Learning prototypes web applications lightning fast.',
    'long_description': '# Overview\n\n\n<p align="center">\n<a href="https://pypi.python.org/pypi/fast_dash">\n    <img src="https://img.shields.io/pypi/v/fast_dash?color=%2334D058"\n        alt = "Release Status">\n</a>\n\n<a href="https://github.com/dkedar7/fast_dash/actions">\n    <img src="https://github.com/dkedar7/fast_dash/actions/workflows/release.yml/badge.svg" alt="CI Status">\n</a>\n\n\n<a href="https://github.com/dkedar7/fast_dash/blob/main/LICENSE">\n    <img src="https://img.shields.io/github/license/dkedar7/fast_dash" alt="MIT License">\n</a>\n\n<a href="https://docs.fastdash.app/">\n    <img src="https://img.shields.io/badge/Docs-MkDocs-<COLOR>.svg" alt="Documentation">\n</a>\n\n</p>\n\n\n<p align="center">\n  <a href="https://fastdash.app/"><img src="https://raw.githubusercontent.com/dkedar7/fast_dash/main/docs/assets/logo.png" alt="Fast Dash logo"></a>\n</p>\n<p align="center">\n    <em>Open source, Python-based tool to build prototypes lightning fast ⚡</em>\n</p>\n\n\n---\n\n* Website: <https://fastdash.app/>\n* Documentation: <https://docs.fastdash.app/>\n* Source code: <https://github.com/dkedar7/fast_dash/>\n* Installation: `pip install fast-dash`\n\n---\n\nFast Dash is a Python module that makes the development of web applications fast and easy. It is built on top of Plotly Dash and can be used to build web interfaces for Machine Learning models or to showcase any proof of concept without the hassle of developing UI from scratch.\n\n<p align="center">\n  <a href="https://fastdash.app/"><img src="https://raw.githubusercontent.com/dkedar7/fast_dash/main/docs/assets/gallery_4_apps.gif" alt="Fast Dash logo"></a>\n</p>\n\n## Simple example\n\nWith Fast Dash\'s decorator `fastdash`, it\'s a breeze to deploy any Python function as a web app. Here\'s how to use it to write your first Fast Dash app:\n```python\nfrom fast_dash import fastdash\n\n@fastdash\ndef text_to_text_function(input_text):\n    return input_text\n\n# * Running on http://127.0.0.1:5000/ (Press CTRL+C to quit)\n```\n\nAnd just like that (\U0001fa84), we have a completely functional interactive app!\n\nOutput:\n![Simple example](https://raw.githubusercontent.com/dkedar7/fast_dash/decorate/docs/assets/simple_example.gif)\n\n---\n\nFast Dash can read additional details about a function, like its name, input and output types, docstring, and uses this information to infer which components to use.\n\nFor example, here\'s how to deploy an app that takes a string and an integer as inputs and return some text.\n\n```python\nfrom fast_dash import fastdash\n\n@fastdash\ndef display_selected_text_and_number(text: str, number: int) -> str:\n    "Simply display the selected text and number"\n    processed_text = f\'Selected text is {text} and the number is {number}.\'\n    return processed_text\n\n# * Running on http://127.0.0.1:5000/ (Press CTRL+C to quit)\n```\nOutput:\n\n![Simple example with multiple inputs](https://storage.googleapis.com/fast_dash/0.1.7/simple_example_2.gif)\n\nAnd with just a few more lines, we can add a title icon, subheader and other social branding details.\n\n```python\nfrom fast_dash import fastdash\n\n@fastdash(title_image_path=\'https://raw.githubusercontent.com/dkedar7/fast_dash/main/docs/assets/favicon.jpg\',\n        github_url=\'https://github.com/dkedar7/fast_dash\',\n        linkedin_url=\'https://linkedin.com/in/dkedar7\',\n        twitter_url=\'https://twitter.com/dkedar\')\ndef display_selected_text_and_number(text: str, number: int) -> str:\n    "Simply display the selected text and number"\n    processed_text = f\'Selected text is {text} and the number is {number}.\'\n    return processed_text\n```\n\nOutput:\n\n![Simple example with multiple inputs and details](https://storage.googleapis.com/fast_dash/0.1.7/simple_example_multiple_inputs_details.png)\n\n---\nRead different ways to build Fast Dash apps and additional details by navigating to the [project documentation](https://docs.fastdash.app/).\n\n## Key features\n\n- Launch an app only by specifying the types of inputs and outputs.\n- Use multiple input and output components simultaneously.\n- Flask-based backend allows easy scalability and customizability.\n- Build fast, share and iterate.\n\nSome features are coming up in future releases:\n\n- More input and output components.\n- Deploy to Heroku and Google Cloud.\n- and many more.\n\n## Community\n\nFast Dash is built on open-source. You are encouraged to share your own projects, which will be highlighted on a common community gallery (coming up).\n\n## Credits\n\nFast Dash is built using [Plotly Dash](https://github.com/plotly/dash). Dash\'s Flask-based backend enables Fast Dash apps to scale easily and makes them highly compatibility with other integration services. This project is partially inspired from [gradio](https://github.com/gradio-app/gradio).\n\nThe project template was created with [Cookiecutter](https://github.com/audreyr/cookiecutter) and [zillionare/cookiecutter-pypackage](https://github.com/zillionare/cookiecutter-pypackage).',
    'author': 'Kedar Dabhadkar',
    'author_email': 'kedar@fastdash.app',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://github.com/dkedar7/fast_dash',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.7,<4.0',
}


setup(**setup_kwargs)
