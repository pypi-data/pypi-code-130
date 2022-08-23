from setuptools import setup
from pathlib import Path

# read the contents of your README file
this_directory = Path(__file__).parent
long_description = (this_directory / "README.md").read_text()

setup(
    name='Distribution_1_3',
    version='0.2',
    description='Probability Distributions',
    long_description=long_description,
    long_description_content_type='text/markdown',
    author='Tomi_Abdul',
    packages=['Distribution'],
    author_email='amusatomisin65@gmail.com',
    zip_safe=False
)
