"""Python Tools.

This is a meta-package providing an easy way to initialize a python
distribution to have the tools I commonly use.

**Source:**
  https://alum.mit.edu/www/mforbes/hg/forbes-group/mmf-setup
**Issues:**
  https://alum.mit.edu/www/mforbes/hg/forbes-group/mmf-setup/issues
"""
import io
from glob import glob
from os.path import basename, dirname, join, splitext

import sys

from setuptools import setup, find_packages
import setuptools

print(setuptools.__version__)

NAME = "mmf_setup"

install_requires = [
    "tomlkit",
    "importlib-metadata",
]

test_requires = [
    "notebook",
    "pytest>=2.8.1",
    "pytest-cov>=2.2.0",
    "pytest-flake8",
    "coverage",
    "mercurial",
    "hg-evolve",
    "hg-git",
    "twine",
    "docutils",
]

extras_require = {
    # Hack so that pip install -e .[test] works for testing.
    # https://inneka.com/programming/python/pip-install-test-dependencies-for-tox-from-setup-py/
    "test": test_requires,
    "nbextensions": ["jupyter_contrib_nbextensions"],
    "hg": ["mercurial>=5.7.1", "hg-evolve>=10.3.0", "hg-git>=0.10.0"],
    "mercurial": ["mercurial>=5.7.1", "hg-evolve>=10.3.0", "hg-git>=0.10.0"],
}


# Remove NAME from sys.modules so that it gets covered in tests. See
# http://stackoverflow.com/questions/11279096
for mod in sys.modules.keys():
    if mod.startswith(NAME):
        del sys.modules[mod]
del mod


def read(*names, **kwargs):
    with io.open(
        join(dirname(__file__), *names), encoding=kwargs.get("encoding", "utf8")
    ) as fh:
        return fh.read()


# Get the long description from the README.md file
LONG_DESCRIPTION = "\n".join([read("README.md"), read("CHANGES.md")])


setup(
    name=NAME,
    version="0.4.8",
    packages=find_packages("src"),
    package_dir={"": "src"},
    py_modules=[splitext(basename(_path))[0] for _path in glob("src/*.py")],
    install_requires=install_requires,
    tests_require=test_requires,
    extras_require=extras_require,
    scripts=["bin/mmf_setup", "bin/mmf_initial_setup", "bin/mmf_setup_bash.py"],
    # Include data from MANIFEST.in
    include_package_data=True,
    # Metadata
    author="Michael McNeil Forbes",
    author_email="michael.forbes+bitbucket@gmail.com",
    url="https://bitbucket.org/mforbes/mmf_setup",
    description="Python Tools",
    long_description=LONG_DESCRIPTION,
    long_description_content_type="text/markdown",
    license="GNU GPLv2 or any later version",
    classifiers=[
        # How mature is this project? Common values are
        #   3 - Alpha
        #   4 - Beta
        #   5 - Production/Stable
        "Development Status :: 3 - Alpha",
        # Indicate who your project is intended for
        "Intended Audience :: Developers",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "Topic :: Utilities",
        # Pick your license as you wish (should match "license" above)
        "License :: OSI Approved :: GNU General Public License v3 or later (GPLv3+)",
        # Specify the Python versions you support here. In particular, ensure
        # that you indicate whether you support Python 2, Python 3 or both.
        "Programming Language :: Python :: 3",
    ],
    keywords="ipython jupyter notebook setup mercurial",
)
