from setuptools import setup, find_packages

import django_postgres_extensions

setup(name='django-postgres-extensions-ng',
    version=django_postgres_extensions.__version__,
    description="Extra features for django.contrib.postgres",
    long_description=open('description.rst').read(),
    author='ifanr',
    author_email='ifanrx@ifanr.com',
    url='https://github.com/ifanrx/django_postgres_extensions',
    packages=find_packages(exclude=['tests', 'tests.*']),
    install_requires=[
        'Django>=4.0',
        'six'
    ],
    classifiers=[
        'Development Status :: 4 - Beta',
        'Environment :: Web Environment',
        'Framework :: Django',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: BSD License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 3',
        'Topic :: Database',
        'Topic :: Software Development :: Libraries :: Python Modules',
    ],
)
