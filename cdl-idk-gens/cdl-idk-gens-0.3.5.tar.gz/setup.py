"""
Tools for building insight generators.
"""

from idkgens._version import __version__

try:
    from setuptools import setup
except ImportError:
    from distutils.core import setup

with open("README.md") as fp:
    long_description = fp.read()


setup(
    name="cdl-idk-gens",
    version=__version__,
    description="Tools for building insight generators",
    long_description=long_description,
    long_description_content_type="text/markdown",
    author="eden.trainor@compassdigital.io",
    packages=["idkgens"],
    install_requires=[
        "mypy",
        "pandas"
    ],
    python_requires=">=3.6"
)
