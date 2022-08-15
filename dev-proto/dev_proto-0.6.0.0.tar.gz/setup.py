from setuptools import find_packages, setup
import os

setup(
  name="dev_proto",
  version="0.6.0.0",
  install_requires=["betterproto~=1.2.0"],
  packages=find_packages(),
)
