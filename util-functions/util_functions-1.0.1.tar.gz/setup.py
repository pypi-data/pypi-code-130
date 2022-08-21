from setuptools import setup, find_packages

VERSION = "1.0.1"

setup(
  name="util_functions",
  version=VERSION,
  author="Patryk Palej",
  description="Repository contains utility functions which perform commonly needed operations ",
  packages=find_packages(),
  install_requires=["numpy", "pandas"]
)
