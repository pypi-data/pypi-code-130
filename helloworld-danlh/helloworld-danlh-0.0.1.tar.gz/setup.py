from setuptools import setup

with open(r"README.md", "r") as f:
    long_description = f.read()

setup(
    name='helloworld-danlh',  #  The name used when pip installing (pip install helloworld)
    version='0.0.1',
    description='Test say hello func',
    py_modules=["helloworld"],
    package_dir={'': 'src'},
    classifiers=[
                 "Programming Language :: Python :: 3",
                 "License :: OSI Approved :: MIT License",
                 "Operating System :: OS Independent"
                 ],
    long_description=long_description,
    long_description_content_type="text/markdown",
    install_requires = [
                        "blessings >= 1.7",
                        ],
    extras_require = {
        "dev": [
                "pytest >= 3.7"
                ]
    }
)