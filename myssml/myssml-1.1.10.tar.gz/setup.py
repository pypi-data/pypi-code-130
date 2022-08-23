from setuptools import setup

setup(
    cmdclass={},

    name='myssml',
    packages=['myssml'],
    version='1.1.10',

    install_requires=[],

    description='Python library for building SSML for Amazon Alexa or Microsoft or Google etc.',

    long_description=
    """
    myssml

    Python 3 SSML builder for Alexa or Microsoft or Google etc..

    Inspired by and based on JavaScript project https://github.com/mandnyc/ssml-builder
    Inspired by and based on Python project  https://github.com/sumsted/pyssml
    """,

    url='https://github.com/rdaim',

    author='wanyangchun',
    author_email='rdaim@qq.com',
    license='Apache',
    classifiers=[
        'Development Status :: 5 - Production/Stable',
        'Intended Audience :: Developers',
        'Topic :: Software Development :: Libraries :: Python Modules',

        'License :: OSI Approved :: Apache Software License',

        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.2',
        'Programming Language :: Python :: 3.3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.9',
    ],

    keywords='ssml python myssml ',
)
