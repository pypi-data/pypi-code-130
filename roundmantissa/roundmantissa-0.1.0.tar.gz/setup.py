import os
import re

from setuptools import find_packages, setup

# Recommendations from https://packaging.python.org/
here = os.path.abspath(os.path.dirname(__file__))
with open(os.path.join(here, "README.md"), encoding="utf-8") as f:
    long_description = f.read()


def read(*parts):
    with open(os.path.join(here, *parts), "r") as fp:
        return fp.read()


def find_version(*file_paths):
    version_file = read(*file_paths)
    version_match = re.search(r"^__version__ = ['\"]([^'\"]*)['\"]", version_file, re.M)
    if version_match:
        return version_match.group(1)
    raise RuntimeError("Unable to find version string.")


setup(
    name="roundmantissa",
    version=find_version("roundmantissa", "__init__.py"),
    description="Round mantissa of a float number",
    long_description=long_description,
    long_description_content_type="text/markdown",
    packages=find_packages(exclude=["tests.*", "tests"]),
    install_requires=[],
    include_package_data=True,
    classifiers=[],
    python_requires=">=3.7",
    license="MIT",
    license_files=["LICENSE"],
)
