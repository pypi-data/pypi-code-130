from setuptools import setup, find_packages

setup(
    name="textnowdemonators",
    version='0.0.1',
    author="decrypt",
    description='textnow wrapper',
    packages=find_packages(),
    install_requires=['requests', 'bs4']
)
