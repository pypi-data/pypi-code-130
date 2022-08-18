
from setuptools import setup, find_namespace_packages
setup(
    name = 'ibm-flask-jwt',
    version = '0.0.1',
    description = 'A simple library for securing Flask REST APIs with JWTs using decorators',
    readme = 'README.md',
    package_dir={'':'lib'},
    packages = find_namespace_packages(where='lib', exclude=['*test*']),
    install_requires = ['aniso8601==9.0.1', 'cffi==1.15.1', 'click==8.1.3', 'cryptography==37.0.4', 'environs==9.5.0', 'flask==2.2.2', 'flask-restful==0.3.9', 'itsdangerous==2.1.2', 'jinja2==3.1.2', 'markupsafe==2.1.1', 'marshmallow==3.17.0', 'packaging==21.3', 'pycparser==2.21', 'pyjwt==2.4.0', 'pyparsing==3.0.9', 'python-dotenv==0.20.0', 'pytz==2022.2.1', 'six==1.16.0', 'werkzeug==2.2.2'],
    classifiers = [
        'Programming Language :: Python :: 3',
        'License :: OSI Approved :: Apache Software License',
        'Operating System :: OS Independent',
    ],
    url = 'https://github.com/IBM/py-flask-jwt'
)
