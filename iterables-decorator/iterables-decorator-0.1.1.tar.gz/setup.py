"""Setup config for Now CLI."""
import pathlib

from setuptools import setup

here = pathlib.Path(__file__).parent.resolve()
long_description = (here / "README.md").read_text(encoding="utf-8")

with open("version.txt", "r") as version_file:
    version = version_file.read().strip()

setup(
    name="iterables-decorator",
    version=version,
    description="Decorator to convert a class into an iterable.",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/mr-strawberry66/iterables-decorator",
    py_modules=["iterables"],
)
