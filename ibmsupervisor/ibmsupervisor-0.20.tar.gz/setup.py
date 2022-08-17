from setuptools import * 

with open('README.md', 'r') as f:
    LONG_DESCRIPTION = f.read()

DESCRIPTION = 'Extract the supervisor password from the ROM dump of an IBM ThinkPad'
VERSION = '0.20'

setup(
    name='ibmsupervisor',
    version=VERSION,
    description=DESCRIPTION,
    long_description=LONG_DESCRIPTION,
    long_description_content_type='text/markdown',
    url='https://gitlab.com/eloydegen/ibmsupervisor',
    author='Eloy',
    author_email='degeneloy@gmail.com',
    license='MIT License',
    packages=find_packages(),
    classifiers=[
        'Programming Language :: Python :: 3'
    ],
    entry_points={
        'console_scripts': [
            'ibmsupervisor=ibmsupervisor.main:main'
        ]
    },
    include_package_data=True
)
