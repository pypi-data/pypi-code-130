from setuptools import setup, find_packages
import codecs
import os

VERSION = '0.0.a'
DESCRIPTION = 'This package is for Data augmentation of image dataset'
LONG_DESCRIPTION = 'It is a model for augmentation of image dataset. Augmentation of image is carried out by the process' \
                   ' of resize, scale, rotate, translation, transpose, blurring, and by adding noise to the image. ' \
                   'Dataset(X_train) can be augmented to 10x of its original size while saving y_train data for each image.'

# Setting up
setup(
    name="imgaugmentation",
    version=VERSION,
    author="Sumit Singh",
    author_email="<iamsumit1904@gmail.com>",
    description=DESCRIPTION,
    long_description_content_type="text/markdown",
    long_description=LONG_DESCRIPTION,
    packages=find_packages(),
    install_requires=['opencv-python', 'numpy', 'matplotlib'],
    keywords=['python', 'augmentation', 'image', 'data augmentation', 'image dataset'],
    classifiers=[
        "Development Status :: 1 - Planning",
        "Intended Audience :: Developers",
        "Programming Language :: Python :: 3",
        "Operating System :: Unix",
        "Operating System :: MacOS :: MacOS X",
        "Operating System :: Microsoft :: Windows",
    ]
)
