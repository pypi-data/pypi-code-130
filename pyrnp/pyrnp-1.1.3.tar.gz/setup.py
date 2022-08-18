# Based on Zoomus' (https://github.com/prschmid/zoomus) setup file
from __future__ import print_function, unicode_literals

from setuptools import setup
import codecs
import os
import re

here = os.path.abspath(os.path.dirname(__file__))


def read(file_paths, default=""):
    try:
        with codecs.open(os.path.join(here, *file_paths), "r") as fh:
            return fh.read()
    except Exception:
        return default


def find_version(file_paths):
    version_file = read(file_paths)
    version_match = re.search(r"^__version__ = ['\"]([^'\"]*)['\"]", version_file, re.M)
    if version_match:
        return version_match.group(1)
    raise RuntimeError("Unable to find version string.")


setup(
    name="pyrnp",
    version=find_version(["pyrnp", "__init__.py"]),
    url="https://github.com/cnpem-iot/pyrnp",
    license="GNU Affero General Public License v3 or later (AGPLv3+)",
    author="Guilherme F. de Freitas",
    install_requires=["requests"],
    author_email="g.fr@tuta.io",
    description="Python client library for Eduplay (video platform from RNP)",
    long_description=read(["README.md"]),
    long_description_content_type="text/markdown",
    packages=["pyrnp"],
    include_package_data=True,
    platforms="any",
    zip_safe=False,
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "Topic :: Software Development :: Build Tools",
        "License :: OSI Approved :: GNU Affero General Public License v3 or later (AGPLv3+)",
        "Natural Language :: English",
        "Environment :: Web Environment",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3 :: Only",
        "Operating System :: OS Independent",
        "Topic :: Internet",
        "Topic :: Office/Business",
        "Topic :: Software Development :: Libraries",
    ],
)
