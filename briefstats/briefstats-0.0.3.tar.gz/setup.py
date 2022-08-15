from setuptools import setup, find_packages
import briefstats

setup(
    name='briefstats',
    version=briefstats.__version__,
    description=(
        'A brief statistics tool for Chinese.'
    ),
    long_description=open('README.md', 'r', encoding='utf-8').read(),
    long_description_content_type="text/markdown",
    author='Kang Zhou',
    author_email='zkSpongeBob@126.com',
    maintainer='Kang Zhou',
    maintainer_email='zkSpongeBob@126.com',
    license='MIT License',
    packages=find_packages(),
    platforms=["all"],
    install_requires=[
        "numpy >= 1.23.1",
        "prettytable >= 3.3.0",
    ]
)