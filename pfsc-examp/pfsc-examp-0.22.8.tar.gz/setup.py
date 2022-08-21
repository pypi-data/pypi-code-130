import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="pfsc-examp",
    version="0.22.8",
    license="Apache 2.0",
    url="https://github.com/proofscape/pfsc-examp",
    description="Example explorers for Proofscape",
    long_description=long_description,
    long_description_content_type="text/markdown",
    packages=setuptools.find_packages(),
    install_requires=[
        'lark067==0.6.7',
        'displaylang-sympy>=0.10.4',
        'displaylang>=0.22.8',
        'pfsc-util>=0.22.8',
        'Jinja2>=3.0.3,<4',
        'MarkupSafe>=2.0.1,<3',
    ],
    classifiers=[
        "License :: OSI Approved :: Apache Software License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
    ],
)

