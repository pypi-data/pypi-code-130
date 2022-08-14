from setuptools import setup, find_packages

VERSION = '0.0.4'
DESCRIPTION = 'A Library With shrtco.de Api'

with open("README.md", "r") as f:
    LONG_DESCRIPTION = f.read()

setup(
    name="miniurls",
    version=VERSION,
    author="hero",
    author_email="mrhero4006@gmail.com",
    description=DESCRIPTION,
    long_description_content_type="text/markdown",
    long_description=LONG_DESCRIPTION,
    packages=find_packages(),
    install_requires=[],
    keywords=['miniurls', 'Api', 'miniurl', 'hero', 'heromr'],
)