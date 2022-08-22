from setuptools import setup, find_packages

VERSION = '1.0.0'
DESCRIPTION = 'A Takeout client for Python.'

setup(
    name="takeout.py",
    version=VERSION,
    author="Takeout by Sourfruit",
    author_email="<hello@def-not-hacking-the.net>",
    description=DESCRIPTION,
    packages=find_packages(),
    install_requires=[],

    keywords=['python', 'takeout.py', 'takeout', 'sourfruit'],
)