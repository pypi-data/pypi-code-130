"""Python setup.py for hsproxy package"""
import io
import os
from setuptools import find_packages, setup


def read(*paths, **kwargs):
  """Read the contents of a text file safely.
    >>> read("hsproxy", "VERSION")
    '0.1.0'
    >>> read("README.md")
    ...
    """

  content = ""
  with io.open(
      os.path.join(os.path.dirname(__file__), *paths),
      encoding=kwargs.get("encoding", "utf8"),
  ) as open_file:
    content = open_file.read().strip()
  return content


setup(
    name="hsproxy",
    version=read("hsproxy", "VERSION"),
    description="hsproxy",
    url="https://github.com/iuser-dev/iuser_i18n/",
    long_description=read("README.md"),
    long_description_content_type="text/markdown",
    packages=find_packages(exclude=["tests", ".github"]),
    install_requires=["volcengine", "fire", "grpclib"],
    scripts=['hsproxy/hsproxy'],
    author='iuser',
    author_email='iuser.link@gmail.com',
)
