import setuptools

setuptools.setup(
    name = 'brassica',
    version = '1.0.0',
    author = 'Mike Lee',
    author_email = 'random.deviate@gmail.com',
    description = 'Interpreter for 1975 Altair/Microsoft BASIC',
    long_description = open('README.md').read(),
    long_description_content_type = 'text/markdown',
    packages = setuptools.find_packages(),
    classifiers = ['Programming Language :: Python :: 3.9'],
    python_requires = '>=3.9',
    include_package_data = True,
    package_data = {'': ['BASIC/*.bas']},
    zip_safe = True
)
