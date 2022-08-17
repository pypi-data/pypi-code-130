from setuptools import setup

"""
:authors: ymoth
:copyright: (c) 2022 ymoth
"""

version = "1.1.3"

setup(
    name="quote_depencives",
    version=version,

    author="ymoth",
    author_email="tophanbig@gmail.com",
    description="Easy create quote image by agrmunets in class options",

    url="https://github.com/ymoth/quote-manager",
    packages=["quote_depencives", "quote_depencives/default_dependencies"],
    requires=["aiohttp", "requests", "Pillow"],
)
