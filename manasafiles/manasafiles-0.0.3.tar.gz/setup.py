import setuptools

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setuptools.setup(
    name='manasafiles',
    version='0.0.3',
    author='manasa',
    author_email='manasabalagoni1@gmail.com',
    description='Testing installation of Package',
    long_description=long_description,
    long_description_content_type="text/markdown",
    url='https://github.com/manasabalagoni/python-second',
    project_urls = {
        "Bug Tracker": "https://github.com/manasabalagoni/python-second/issues"
    },
    license='MIT',
    packages=['manasafiles'],
    install_requires=['requests'],
    
    download_url="https://github.com/manasabalagoni/python-second/archive/refs/tags/0.0.3.tar.gz",
)
