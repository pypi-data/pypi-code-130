from setuptools import find_packages
from setuptools import setup

setup(
    name='HolaRivworks',
    version='1.0.0',
    description='just saying hello',
    author='j rivera',
    author_email='joerivera@rivworks.net',
    url='https://github.com/rivworks/hello-mundo',
    install_requires=[],
    packages=find_packages(exclude=('tests*', 'testing*')),
    entry_points={
        'console_scripts': ['HolaRivworks-cli=HolaRivworks.main:main'],
    },
)
