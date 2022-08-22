from setuptools import setup, find_packages

# Use Readme as long description
with open("README.md", "r", encoding="utf-8") as readme_file:
    long_description = readme_file.read()

setup(
    name='orijin_sdk',
    version='0.1.1',

    url='https://github.com/orijinplus/python-tools',
    author='Orijin',
    license='MIT',
    author_email='',
    description="Orijin SDK for client development",
    long_description=long_description,

    packages=find_packages(),

    install_requires=['requests'],
)