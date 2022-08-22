import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="pyprogressbars",
    version="0.0.3",
    author="Karthik E C",
    author_email="eckarthik39@gmail.com",
    description="A minimalistic progress indicators library for usage in CLI based python projects",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/eckarthik/pyprogressbars",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.0',
    py_modules=['pyprogressbars']
)