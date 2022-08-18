import setuptools

with open("README.md", "r", encoding="utf-8") as readme:
	longDescription = readme.read()

with open("LICENSE.txt", "r", encoding="utf-8") as licens:
	myLicense = licens.read()

setuptools.setup(
    name = "fps-debut-package",
    version = "0.0.1",
    author = "fps",
    author_email = "anthony.nnaemeka.umeh@gmail.com",
    license = myLicense,
    description = "First Package",
    long_description = longDescription,
    long_description_content_type = "text/markdown",
    url = "https://github.com/0xfps/first-python-package",
    project_urls = {
        "fps-package": "https://github.com/0xfps/first-python-package",
        "0xfps": "https://github.com/0xfps",
    },
    classifiers = [
        "Programming Language :: Python :: 3",
        "Operating System :: OS Independent",
        "License :: OSI Approved :: MIT License",
    ],
    packages = ["fps_debut_package"],
    python_requires = ">=3.6",
    zip_safe = False
)