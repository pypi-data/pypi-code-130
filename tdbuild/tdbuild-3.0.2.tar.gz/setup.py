# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['tdbuild']

package_data = \
{'': ['*']}

install_requires = \
['colorama>=0.4.5,<0.5.0']

entry_points = \
{'console_scripts': ['tdbuild = tdbuild.cli:main']}

setup_kwargs = {
    'name': 'tdbuild',
    'version': '3.0.2',
    'description': 'A simple build tool for C and C++',
    'long_description': "# Installation\n\n`pip install tdbuild`\n\n# Usage\n\nUsage is dead simple. Use `tdbuild new` to create a Python script called `tdfile.py`. Hand-edit some basic inputs to the compiler (what are your source files? what is the executable called? etc). Then, run `tdbuild` to build and `tdbuild run` to run your code. Altogether, it looks like this:\n\n ```\n mkdir new_project && cd new_project\n \n tdbuild new\n \n emacs tdfile.py\n \n tdbuild\n \n tdbuild run\n ```\n# Why did you write this software?\nDo you find CMake's scripting language arcane and its documentation unusable?\n\nDo you struggle to install and maintain a usable set of Unix tools on Windows? And do you hate creating Makefiles that are cross platform?\n\nDo you want to write code instead of learning how to use a flashy new build system like Meson?\n\nYeah. Me too. Use this C/C++ build system. Fundamentally, all it does it build a command line for your compiler. It's that simple. If `tdbuild` ever becomes insufficient for you, you can copy thee command line and do whatever the hell you want with it. You can also add custom flags to the command line.\n\nYes, this means your whole program will rebuild every time. If your program is very big or uses a lot of templates, your build times will be slow. If you are the target audience for this build tool, then you won't care. `tdbuild` is not for enterprise software, nor is it for large open source projects. It's for people who just want to write a damn C/C++ project that compiles on all platforms without screwing with build tools for a few days.\n\nSome projects that I build with `tdbuild` every day:\n- https://github.com/spaderthomas/tdengine, my game engine.\n- https://github.com/spaderthomas/tdeditor, my text editor.\n\n# Options\n\nYour build options are simply a Python dictionary. That's it. Here's a list of all the possible options the tool supports:\n\n### Top Level\n`options.project`: \n`options.source_dir`: \n`options.include_dirs`: \n`options.lib_dir`: \n`options.build_dir`: \n`options.source_files`: \n`options.build_type`: \n`options.binary_type`: \n`options.cpp`: \n`options.cpp_standard`: \n`options.disable_console`: \n`options.defines`:\n\n### Windows\n`options.Windows.system_libs`:\n`options.Windows.user_libs`:\n`options.Windows.dlls`:\n`options.Windows.ignore`:\n`options.Windows.arch`:\n`options.Windows.out`:\n`options.Windows.runtime_library`:\n`options.Windows.warnings`:\n`options.Windows.extras`:\n\n## Linux\n`options.Linux.compiler`:\n`options.Linux.user_libs`:\n`options.Linux.system_libs`:\n`options.Linux.extras`:\n`options.Linux.out`:\n",
    'author': 'spader',
    'author_email': 'thomas.spader@gmail.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://spader.zone',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'entry_points': entry_points,
    'python_requires': '>=3.9,<4.0',
}


setup(**setup_kwargs)
