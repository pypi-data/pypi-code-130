from setuptools import setup, find_packages

setup(
    name='chpypi',
    version='1.1.1',
    author='maker',
    author_email='c13826564630@163.com',
    packages=find_packages(),
    python_requires='>=3.6',
    url="https://www.itaxs.com/",
    install_requires=[
        'requests'
    ]
)
