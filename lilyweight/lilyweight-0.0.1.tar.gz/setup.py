from setuptools import setup, find_packages

VERSION = '0.0.1'
DESCRIPTION = 'Hypixel SkyBlock Weight Calculator.'

# Setting up
setup(
    name="lilyweight",
    version=VERSION,
    author="timnoot",
    author_email="<hypixelskyhub@gmail.com>",
    description=DESCRIPTION,
    long_description_content_type="text/markdown",
    packages=find_packages(),
    install_requires=['aiohttp'],
    keywords=['python', 'hypixel', 'skyblock', 'lily weight', 'weight', 'lappysheep', "lilly"],
    classifiers=[
        "Programming Language :: Python :: 3",
    ]
)
