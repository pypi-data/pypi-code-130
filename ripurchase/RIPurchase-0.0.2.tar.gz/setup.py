import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="RIPurchase", # Replace with your own username
    version="0.0.2",
    author="Sanjay John",
    author_email="sjohn@ibm.com",
    description="Package for AWS EC2 Reserved Instances",
    long_description=long_description,
    long_description_content_type="text/markdown",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.6',
)
