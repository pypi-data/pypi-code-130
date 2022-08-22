import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="progkids",                     # This is the name of the package
    version="0.1.5",                        # The initial release version
    author="ProgKids Inc.",                     # Full name of the author
    description="Online coding school for kids - ProgKids",
    # Long description read from the the readme file
    long_description=long_description,
    long_description_content_type="text/markdown",
    # List of all python modules to be installed
    packages=['progkids'],
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "Intended Audience :: Education",
        "Intended Audience :: Developers",
        "Topic :: Education",
        "Topic :: Games/Entertainment",
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent"
    ],                                      # Information to filter the project on PyPi website
    python_requires='>=3.6',                # Minimum version requirement of the package
    py_modules=["progkids"],             # Name of the python package
    install_requires=[
        'python-socketio[client]==4.6.1',
        'nanoid'
    ]                     # Install other dependencies if any
)
