import os
import pathlib

from relay import __version__
from setuptools import find_packages
from setuptools import setup

CURRENT_PATH = str(pathlib.Path(__file__).parent.resolve())
README_FILE = os.path.join(CURRENT_PATH, "..", "README.md")
BUILD_DEPENDENCIES = ["wheel"]
DEPENDENCIES = BUILD_DEPENDENCIES

# Get the long description from the README file
try:
    import pypandoc
    from pypandoc.pandoc_download import download_pandoc

    # see the documentation how to customize the installation path
    # but be aware that you then need to include it in the `PATH`
    download_pandoc()

    LONG_DESCRIPTION = pypandoc.convert_file(README_FILE, "rst")
except ImportError:
    with open(README_FILE, encoding="utf-8") as f:
        LONG_DESCRIPTION = f.read()

setup(
    name="msg-relay",
    version=__version__,
    description="Lightweight Python publish/subscribe event bus",
    long_description=LONG_DESCRIPTION,
    author="Roberto Crespo",
    author_email="rcrespoa@alumni.nd.edu",
    packages=find_packages("."),
    install_requires=DEPENDENCIES,
    url="https://github.com/rcrespoa/msgrelay",
    keywords="pubsub message bus pub sub event",
    classifiers=[
        # How mature is this project? Common values are
        #   3 - Alpha
        #   4 - Beta
        #   5 - Production/Stable
        "Development Status :: 3 - Alpha",
        # Indicate who your project is intended for
        "Intended Audience :: Developers",
        "Topic :: Software Development :: Build Tools",
        # Pick your license as you wish (should match "license" above)
        "License :: OSI Approved :: MIT License",
        # Specify the Python versions you support here. In particular, ensure
        # that you indicate whether you support Python 2, Python 3 or both.
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
    ],
)
