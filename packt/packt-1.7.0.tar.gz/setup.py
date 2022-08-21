import os
from setuptools import find_packages, setup

with open(os.path.join(os.path.dirname(__file__), 'README.md')) as f:
    long_description = f.read()

package_version = '1.7.0'

requirements = [
    'click==8.1.3',
    'google-api-python-client==2.57.0',
    'oauth2client==4.1.3',
    'requests==2.28.1',
    'python-slugify==6.1.2'
]

dev_requirements = [
    'bumpversion==0.6.0',
    'mccabe==0.7.0',
    'pycodestyle==2.9.1',
    'pyflakes==2.5.0',
    'pylama==8.4.1'
]

setup(
    name='packt',
    version=package_version,
    packages=find_packages(),
    license='MIT',
    description='Script for grabbing daily Packt Free Learning ebooks',
    author='Łukasz Uszko',
    author_email='lukasz.uszko@gmail.com',
    url='https://gitlab.com/packt-cli/packt-cli',
    long_description=long_description,
    long_description_content_type='text/markdown',
    py_modules=['packt'],
    install_requires=requirements,
    extras_require={'dev': dev_requirements},
    entry_points={
        'console_scripts': [
            'packt-cli = packt.packtPublishingFreeEbook:packt_cli',
        ],
    },
    download_url='https://gitlab.com/packt-cli/packt-cli/-/archive/v1.7.0/packt-cli-v1.7.0.tar.gz',
    classifiers=[
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3.9',
        'Programming Language :: Python :: 3.10'
    ]
)
