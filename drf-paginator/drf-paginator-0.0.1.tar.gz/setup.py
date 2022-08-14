from setuptools import setup, find_packages


VERSION = '0.0.1'
DESCRIPTION = 'DjangoRestFramework paginated response'
LONG_DESCRIPTION = 'A package that makes paginated response of QuerySet with given serializer.'

# Setting up
setup(
    name="drf-paginator",
    version=VERSION,
    author="anqov",
    author_email="jamoliddin.bakhriddinov@gmail.com",
    description=DESCRIPTION,
    long_description_content_type="text/markdown",
    long_description=LONG_DESCRIPTION,
    packages=find_packages(),
    install_requires=['django', 'djangorestframework'],
    keywords=['python', 'django', 'djangorestframework', 'drf', 'pagination'],
    classifiers=[
        "Development Status :: 1 - Planning",
        "Intended Audience :: Developers",
        "Programming Language :: Python :: 3",
        "Operating System :: Unix",
        "Operating System :: MacOS :: MacOS X",
        "Operating System :: Microsoft :: Windows",
    ]
)