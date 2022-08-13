from setuptools import setup

with open(r"/mnt/f/Projects/Work/HighThroughputScreen/requirements.txt") as fd:
    requires = fd.read().split("\n")
setup(
    install_requires=requires
)
