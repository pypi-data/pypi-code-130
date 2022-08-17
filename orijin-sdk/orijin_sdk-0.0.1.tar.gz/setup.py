from setuptools import setup, find_packages

from orijin_sdk import __version__

# Use Readme as long description
with open("README.md", "r", encoding="utf-8") as readme_file:
    long_description = readme_file.read()

setup(
    name='orijin_sdk',
    version=__version__,

    url='https://github.com/orijinplus/python-tools',
    author='Orijin',
    license='MIT',
    author_email='',
    description="Orijin SDK for client development",
    long_description=long_description,

    packages=find_packages(),

    install_requires=['requests', 'python-dotenv'],
)