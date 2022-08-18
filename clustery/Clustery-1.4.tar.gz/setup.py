from distutils.core import setup

setup(
    name = "Clustery",
    packages = ["clustery"],
    version = "1.4",
    description = "Database system that makes life way easier than SQL.",
    long_description = open("README.md", "r").read(),
    long_description_content_type = "text/markdown",
    author = "JKlijzing",
    author_email = "jklijzing@shrp.tv",
    keywords = ["clustery", "db", "database"],
    install_requires = [
        "typing",
        "pyAesCrypt"
    ],
    classifiers = [
        "Development Status :: 5 - Production/Stable",
        "Intended Audience :: Developers",
        "Topic :: Database :: Database Engines/Servers",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12"
    ]
)