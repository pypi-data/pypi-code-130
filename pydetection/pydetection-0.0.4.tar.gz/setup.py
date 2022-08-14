import setuptools

with open("README.md", "r", encoding="utf-8") as fh:
    long_description =  fh.read()

setuptools.setup(
    name = "pydetection",
    version = "0.0.4",
    author = "Ayaan Imran",
    author_email = "miskiacuberayaan2509@gmail.com",
    description = "This package will allow users to detect objects, such as hands and fingers, in a very simple way.",
    long_description = long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/Ayaan-Imran/pydetection",
    packages=setuptools.find_packages(),
    classifiers=[
    "Programming Language :: Python",
    "License :: OSI Approved :: MIT License",
    "Operating System :: OS Independent"
    ],
    python_requires="<=3.7",
    include_package_data=True
)