from setuptools import setup

import pylcount

with open('README.md', 'r') as reader:
    readme = reader.read()

setup(
    author='Jaedson Silva',
    author_email='imunknowuser@protonmail.com',
    name='pylcount',
    description='Python file line counter.',
    long_description=readme,
    long_description_content_type='text/markdown',
    version=pylcount.__version__,
    packages=['pylcount'],
    url='https://github.com/jaedsonpys/pylcount',
    license='MIT',
    keywords=['line', 'counter', 'count', 'file'],
    platforms=['any'],
    entry_points={
        'console_scripts': [
            'pylcount = pylcount.__main__:main'
        ]
    }
)
