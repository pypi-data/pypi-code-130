import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="multikeygraph",
    version="1.2.2",
    author="Wes Hardaker",
    author_email="opensource@hardakers.net",
    description="Plot multiple keys on multiple graphs in a pyfsdb/FSDB file.",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/gawseed/multikeygraph",
    packages=setuptools.find_packages(),
    entry_points={
        'console_scripts': [
            'multi-key-graph = multikeygraph.main:main',
        ]
    },
    classifiers=[
        "Programming Language :: Python :: 3",
        "Operating System :: OS Independent",
    ],
    python_requires = '>=3.6',
    test_suite='nose.collector',
    tests_require=['nose'],
)
