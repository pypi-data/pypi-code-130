from distutils.core import setup


with open('README.md', 'r', encoding="utf-8") as readmefile:
    readme = readmefile.read()


setup(
    name = 'televiewshka',
    version = '0.0.1',
    description = 'A framework to develop UI & logic for telegram bots with class based views',
    author='Akim Mukhtarov',
    author_email = 'akim.int80h@gmail.com',
    url = 'https://github.com/akim-mukhtarov/televiewshka',
    packages = [
        'televiewshka',
        'televiewshka/storage'
        ],
    install_requires = [],
    classifiers = [
        "Programming Language :: Python",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3 :: Only",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Topic :: Software Development :: Libraries :: Python Modules",
        ],
    long_description_content_type='text/markdown',
    long_description=readme,
)