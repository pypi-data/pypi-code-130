from setuptools import setup

with open("andreo/README.md", "r") as fh:
    long_description = fh.read()

setup(
    name="andreo1",
    version="0.0.01",
    author="Andreo Naymayer",
    author_email='andreocelular@gmail.com',
    description="Read text or text in images inside a pdf and turn it into string",
    long_description=long_description,
    long_description_content_type="text/markdown",
    packages=["andreo"],
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: Other/Proprietary License",
        "Operating System :: OS Independent",
        "Natural Language :: Portuguese (Brazilian)",
    ],
    keywords='EN: convert pdf to text with option to cut images. BR: converte pdf para texto podendo cortar as imagens',
    install_requires=['numpy','pytesseract','opencv-python'],
    )