import os
import sys

from setuptools import setup

here = os.path.abspath(os.path.dirname(__file__))
__version__ = "0.1.0"


if sys.argv[-1] == "publish":
    os.system("python setup.py sdist")
    os.system("twine upload dist/* --skip-existing")
    sys.exit()

with open(os.path.join(here, "README.md"), encoding="utf-8") as f:
    long_description = f.read()

setup(
    name="reimagined-spoon",
    version=__version__,
    description="Spoon for testing",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/Jalkhov/reimagined-spoon",
    author="Pedro Torcatt",
    author_email="pedrotorcattsoto@gmail.com",
    include_package_data=True,
    python_requires=">=3.6",
    py_modules=["hacker", "hacker_tools", "index"],
    project_urls={
        "Bug Reports": "https://github.com/Jalkhov/reimagined-spoon/issues",
        "Source": "https://github.com/Jalkhov/reimagined-spoon",
    }
)
