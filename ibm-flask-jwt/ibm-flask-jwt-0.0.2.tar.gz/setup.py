
from setuptools import setup, find_namespace_packages
setup(
    name = 'ibm-flask-jwt',
    version = '0.0.2',
    description = 'A simple library for securing Flask REST APIs with JWTs using decorators',
    readme = 'README.md',
    package_dir = {'':'lib'},
    packages = find_namespace_packages(where='lib', exclude=['*test*']),
    install_requires = ['aniso8601==9.0.1', 'cffi==1.15.1', 'click==8.1.3', 'cryptography==37.0.4', 'environs==9.5.0', 'flask==2.2.2', 'flask-restful==0.3.9', 'itsdangerous==2.1.2', 'jinja2==3.1.2', 'markupsafe==2.1.1', 'marshmallow==3.17.0', 'packaging==21.3', 'pycparser==2.21', 'pyjwt==2.4.0', 'pyparsing==3.0.9', 'python-dotenv==0.20.0', 'pytz==2022.2.1', 'six==1.16.0', 'werkzeug==2.2.2'],
    long_description = """# IBM Flask JWT
This project provides a simple Python library for securing Flask APIs with JWT authentication.

[![Build](https://github.com/IBM/py-flask-jwt/actions/workflows/build.yaml/badge.svg?branch=main)](https://github.com/IBM/py-flask-jwt/actions/workflows/build.yaml)

## JSON Web Tokens
Secure endpoints are accessed by passing a [JSON Web Token](https://jwt.io/introduction) (JWT).

## API Decorators
The follow Python decorators are available for use on Flask API endpoints.
* `private` - Secures an API endpoint. Requests to the endpoint will return a `401 Unauthorized` response unless a valid JWT is attached to the HTTP request. The JWT must be sent as a bearer token in the standard authorization header: `Authorization: Bearer <token>`.
* `public` - This is a marker decorator to identify an endpoint as intentionally public.

### Example
The following example shows how to secure a private endpoint for a simple API built with the [Flask RESTful](https://flask-restful.readthedocs.io/en/latest/) framework. In this example, requests to the resource will return a `401 Unauthorized` response unless a valid JWT token is attached to the HTTP request.
```
from flask_restful import Resource
from ibm_flask_jwt.decorators import private


class PrivateApi(Resource):

    @private
    def get(self):
        return 'Success'
```

## Configuration
The following environment variables are loaded by the library:
* `JWT_PUBLIC_KEY` - (Required) RSA256 public key for JWT signature verification.

## Development

### Dependencies
Use [Pipenv](https://pipenv.pypa.io/en/latest/) for managing dependencies. Install all dependencies with `pipenv install --dev`.

### Testing
Run the unit tests with code coverage with `pipenv run pytest --cov lib test`.

### Building
Run the `build.py` file to generate the `setup.py` file. This allows us to read the required dependencies from `Pipfile.lock` so they are available in the `install_requires` configuration field of `setup.py`.
""",
    long_description_content_type = 'text/markdown',
    classifiers = [
        'Programming Language :: Python :: 3',
        'License :: OSI Approved :: Apache Software License',
        'Operating System :: OS Independent',
    ],
    url = 'https://github.com/IBM/py-flask-jwt'
)
