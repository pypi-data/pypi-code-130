import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="dogcputils", # Replace with your own username
    version="1.0.0",
    author="Prawit Pimmasarn",
    author_email="prawit.pimmasarn@gmail.com",
    license='MIT',
    description="A core repository of do utilities class",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/Deep-Ocean-Fund/do-core",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3.9",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.9',
)