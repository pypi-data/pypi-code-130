from setuptools import setup, find_packages
import glob

setup(
    name='gaelib',
    version='0.1.8',
    description='Google App Engine Library',
    author='Shantanu Mallik',
    license='gpl-3.0',
    packages=find_packages(where='.') + find_packages(exclude=("tests",)),
    include_package_data=True,
    zip_safe=False,
    install_requires=[
        'wheel==0.36.2',
        'google-cloud-speech==2.4.0',
        'google-cloud-core==1.3.0',
        'grpcio==1.38.0',
        'google-auth==1.35.0',
        'google-cloud-datastore==1.15.3',
        'requests==2.25.1',
        'google-cloud-logging==1.15.1',
        'google-cloud-storage==1.30.0',
        'google-cloud-speech==1.3.2',
        'google-api-core==1.32.0',
        'google-api-python-client==1.9.1',
        'py-dateutil==2.2',
        'pyjwt==1.7.1',
        'hyper',
        'google-cloud-tasks==2.0.0',
        'googleapis_common_protos==1.53.0',
        'firebase-admin==4.3.0',
        'python-jose==3.3.0',
        'nose==1.3.7',
        'mock==2.0.0',
        'google-cloud==0.34.0',
        'Flask==2.0.1',
        'Flask-Cors==3.0.9',
        'gunicorn==20.1.0',
        'Jinja2==3.0.1',
        'six==1.15.0',
        'Werkzeug==2.0.1',
        'twilio==6.59.1',
        'certifi==2021.5.30',
        'chardet==4.0.0',
        'click==8.0.1',
        'cachetools==4.2.2',
        'constants==0.6.0',
        'protobuf==3.19.4'
    ],
    setup_requires=[
        'wheel'
    ]
)
