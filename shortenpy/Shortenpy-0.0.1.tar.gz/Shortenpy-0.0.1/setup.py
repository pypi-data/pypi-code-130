import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="Shortenpy", ## 소문자 영단어
    version="0.0.1", ##
    author="PentalYale", ## ex) Sunkyeong Lee
    author_email="geniusboy0225@gmail.com", ##
    description="Make the function shorter to use fast", ##
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/PentalYale/Shortenpy.git", ##
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.6',
)