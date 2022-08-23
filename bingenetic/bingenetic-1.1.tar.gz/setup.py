import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="bingenetic",
    version="1.1",
    author="Ravin Kumar",
    author_email="mr.ravin_kumar@hotmail.com",
    description="convert binary data (in digital form) to genetic codes and further genetic codes back to binary data",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/mr-ravin/BinGenetic",
    keywords = ['Data Storage', 'DNA Data Storage', 'RNA Data Storage','Genetic Storage'],   # Keywords that define your package best
    install_requires=[
      ],

    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 2",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
)
