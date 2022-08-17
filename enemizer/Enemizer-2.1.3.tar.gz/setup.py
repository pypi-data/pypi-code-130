VERSION = "2.1.3"  # Version const for publish script

from setuptools import setup

with open(".\\README.md", "r") as fs:
    long_description = fs.read()

setup(
    name="Enemizer",
    version=VERSION,
    author="Echocolat",
    author_email="",
    description="Breath of the Wild Enemy Randomizer v2 by Echocolat",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/Echocolat/EnemyRandomizerComplete",
    include_package_data=True,
    packages=["enemizer"],
    package_dir={"enemizer": "src"},
    entry_points={
        "console_scripts": [
            "enemize = enemizer.__main__:main",
        ],
    },
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "Environment :: Console",
        "License :: OSI Approved :: GNU General Public License v3 or later (GPLv3+)",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3 :: Only",
    ],
    python_requires=">=3.7",
    install_requires=[
        "bcml>=3.8.6",
        "oead~=1.2.0",
        "botw_flag_util>=0.3.5",
    ],
    zip_safe=False,
)
