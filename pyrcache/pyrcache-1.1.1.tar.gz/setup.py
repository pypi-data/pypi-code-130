import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="pyrcache",
    version="1.1.1",
    author="Yamac Eren Ay",
    author_email="yamacerenay2001@gmail.com",
    description="Python API for accessing RedisCache",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/yamaceay/pyrcache",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent"
    ],
    install_requires=[
          'requests==2.28.1'
      ],
    python_requires='>=3.8',
)