from setuptools import setup
import textmul

DESCRIPTION = "kusozako_text_multiplication: くそざこ文字列掛け算ツール"
NAME = 'kusozako_text_multiplication'
AUTHOR = 'nikawamikan'
URL = 'https://github.com/nikawamikan/textmul'
LICENSE = 'MIT'
VERSION = textmul.__version__
PYTHON_REQUIRES = ">=3.10"


setup(
    name=NAME,
    author=AUTHOR,
    maintainer=AUTHOR,
    description=DESCRIPTION,
    LICENSE=LICENSE,
    url=URL,
    version=VERSION,
    download_url=URL,
)
