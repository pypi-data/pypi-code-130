from reaccess import __version__

from setuptools import setup

with open(f'README.md', 'r') as reader:
    readme = reader.read()

setup(
    author='Jaedson Silva',
    author_email='imunknowuser@protonmail.com',
    name='reaccess',
    description='Execute commands on another machine remotely.',
    version=__version__,
    long_description=readme,
    long_description_content_type='text/markdown',
    url='https://github.com/jaedsonpys/REaccess',
    packages=['reaccess'],
    license='Apache 2.0',
    install_requires=['argeasy'],
    entry_points={
        'console_scripts': [
            'reaccess = reaccess.__main__:main'
        ]
    },
    keywords=['remote', 'backdoor', 'access']
)
