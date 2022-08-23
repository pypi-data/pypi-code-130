from setuptools import setup, find_packages

setup(
    name='FStore',
    version='1.0.0',
    author='Colin Davis',
    author_email='colinmichaelsdavis@gmail.com',
    packages=find_packages(),
    url='https://github.com/colin-m-davis/kvs',
    license='LICENSE.txt',
    description='Key-value store in Python',
    long_description=open('README.md').read(),
    long_description_content_type='text/markdown',
    install_requires=[],
    entry_points = {
        'console_scripts': [
            'fstore = fstore.__main__:main'
        ]
    }
)