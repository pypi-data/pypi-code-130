
from setuptools import setup, find_packages
with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name = 'LUASprites',
    version = '0.0.12',
    author = 'AJ Steinhauser',
    author_email = 'ajsteinhauser11@gmail.com',
    license = 'MIT License',
    description = 'Generate spritesheets and lua modules for easy image reference',
    long_description = long_description,
    long_description_content_type = "text/markdown",
    url = 'https://github.com/AJSteinhauser/LUASprites',
    packages = find_packages(),
    install_requires = [
        'certifi==2022.6.15',
        'charset-normalizer==2.1.1',
        'idna==3.3',
        'Pillow==9.2.0',
        'requests==2.28.1',
        'urllib3==1.26.11'
    ],
    python_requires='>=3.7',
    classifiers=[
        "Programming Language :: Python :: 3.8",
        "Operating System :: OS Independent",
    ],
    entry_points = '''
        [console_scripts]
        luasprite=spritesheet.cli:main
    '''
)
