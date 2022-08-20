from setuptools import setup, find_packages

classifiers = [
    'Development Status :: 5 - Production/Stable',
    'Intended Audience :: Education',
    'Operating System :: Microsoft :: Windows :: Windows 10',
    'License :: OSI Approved :: MIT License',
    'Programming Language :: Python :: 3'
]

with open('README.md') as f:
    lines = f.readlines()
    
readme = "\n".join(lines)

description = readme

setup(
    name='nait',
    version='3.0.8',
    description='Machine learning library',
    long_description=description,
    long_description_content_type='text/markdown',
    author='DanishDeveloper',
    license='MIT', 
    classifiers=classifiers,
    keywords='nait',
    packages=['nait']
)