from setuptools import setup, find_packages

def readfile(name):
    with open(name) as f:
        return f.read()

setup(
    name = "lime_trading_api",
    version = readfile('version.txt'),
    author = "Lime Financial",
    author_email = "support@lime.co",
    description = ("Official python API wrapper for Lime Direct"),
    keywords = "Lime Financial Trading Brokerage API",
    url = "https://docs.lime.co/python",
    package_dir = {"": "src"},
    packages = ["lime_trading_api"],
    include_package_data = True,
    package_data = {
        '':['*.dll', '*.so', '*.dylib'],
    },
    project_urls = {},
    license = readfile('LICENSE'),
    long_description = readfile('README_PACKAGE.md'),
    long_description_content_type = "text/markdown",
) 
  

