import pathlib
from setuptools import setup
HERE = pathlib.Path(__file__).parent
README = (HERE / "README.md").read_text()
setup(
  name="koya_utilities",
  version="0.0.1",
  description="",
  long_description=README,
  long_description_content_type="text/markdown",
  author="",
  author_email="",
  license="MIT",
  packages=["koya_utilities"],
  zip_safe=False
)
