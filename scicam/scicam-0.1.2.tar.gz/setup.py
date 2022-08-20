import pathlib
import warnings
from setuptools import setup, find_packages
import shlex
import subprocess
import re

# The directory containing this file
HERE = pathlib.Path(__file__).parent

# The text of the README file
README = (HERE / "README.md").read_text()

# name of package and name of folder containing it

# attention. you need to update the numbers ALSO in the imgstore/__init__.py file
with open("scicam/__init__.py", "r") as fd:
    version = re.search(
        r'^__version__\s*=\s*[\'"]([^\'"]*)[\'"]', fd.read(), re.MULTILINE
    ).group(1)


def check_ffmpeg():
    try:
        output=subprocess.Popen(shlex.split("ffmpeg -version"), stdout=subprocess.PIPE)
        data=output.communicate()[0].decode()
        return "--enable-cuda-nvcc" in data
    except:
        return False


# This call to setup() does all the work
setup(
    name="scicam",
    version=version,
    packages=find_packages(),
    install_requires=[
        "numpy==1.19.5",
        "pandas>=1.2.4",
        "joblib>=1.1.0",
        "opencv-python==4.5.1.48",
        "pyaml>=6.0",
        "pypylon>=1.8.0",
        "simple_pyspin>=0.1.1",
        "imgstore-shaliulab>=0.4.8",
        "scikit-video>=1.1.11",
        "arrayqueues>=1.3.0",
    ],
    python_requires=">=3.8",
    entry_points={
        "console_scripts": [
            "scicam=scicam.bin.__main__:main",
            "scicam-test=scicam.bin.test:main",
        ]
    },
)

if not check_ffmpeg():
    warnings.warn(
        "You have not installed ffmpeg or it is installed but without CUDA support,"\
        "which means you cannot use the h264_nvenc/mp4 format (h264_nvenc codec)"
    )
