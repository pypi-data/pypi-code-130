from setuptools import setup

with open("README.md", "r") as fh:
    long_description = fh.read()

setup(
    name='mitsubishi_monitor',
    version='0.0.4',
    packages=['mitsubishi_monitor'],
    author='Roland Zitny',
    long_description=long_description,
    long_description_content_type="text/markdown",
)
