from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name='keys_school',
    version='0.1.1',
    author='N/A',
    author_email='joshua.haught@rollinghills.k12.oh.us',
    url='https://github.com/jagg3127/lib',
    project_urls = {"Bug Tracker": "https://github.com/jagg3127/lib/issues"},
    packages=find_packages('src'),
    package_dir={'': 'src'},
    install_requires=['getkey']
)