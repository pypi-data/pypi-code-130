"""
:Project: Cruncher
:Contents: setup.py
:copyright: © 2019-2022 Daniel Morell
:license: MIT, see LICENSE for more details.
:Author: Daniel Morell
"""

import io
import re
from setuptools import setup

with io.open("cruncher/__init__.py", "rt", encoding="utf8") as f:
    version = re.search(r"__version__ = '(.*?)'", f.read()).group(1)

with io.open("README.md", "rt", encoding='utf8') as fh:
    readme = fh.read()

setup(
    name='cruncher',
    version=version,
    license='GPLv3+',
    url='https://github.com/danielmorell/cruncher',
    project_urls={
        "Source Code": "https://github.com/danielmorell/cruncher",
        "Issue tracker": "https://github.com/danielmorell/cruncher/issues",
    },
    author='Daniel Morell',
    author_email='office@carintek.com',
    description="Simple CLI to optimize images for the web.",
    long_description=readme,
    long_description_content_type="text/markdown",
    py_modules=['cruncher'],
    packages=['cruncher'],
    install_requires=[
        'click==8.1.*',
        'pillow==9.2.*',
    ],
    include_package_data=True,
    python_requires=">=3.8",
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: GNU General Public License v3 or later (GPLv3+)",
        "Operating System :: OS Independent",
        "Programming Language :: Python",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
    ],
    entry_points='''
        [console_scripts]
        cruncher=cruncher:cli
    ''',
)
