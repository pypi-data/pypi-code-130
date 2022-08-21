"""Setup."""
from setuptools import find_packages, setup

setup(
    name='aiothrottles',
    version='0.2.0a0',
    author='Konstantin Togoi',
    author_email='konstantin.togoi@gmail.com',
    url='https://github.com/KonstantinTogoi/aiothrottles',
    project_urls={'Documentation': 'https://aiothrottles.readthedocs.io'},
    download_url='https://pypi.org/project/aiothrottles/',
    description='Throttles for Python coroutines.',
    long_description=open('README.rst').read(),  # noqa: WPS515
    license='BSD',
    packages=find_packages(),
    platforms=['Any'],
    python_requires='>=3.7',
    setup_requires=['pytest-runner==6.0.0'],
    tests_require=['pytest==7.1.2', 'pytest-asyncio==0.19.0'],
    keywords=[
        'asyncio synchronization lock semaphore'
        'throttler throttles throttling rate limiting',
    ],
    classifiers=[
        'Intended Audience :: Developers',
        'License :: OSI Approved :: BSD License',
        'Programming Language :: Python',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3.9',
        'Programming Language :: Python :: 3 :: Only',
        'Topic :: Software Development :: Libraries :: Python Modules',
    ],
)
