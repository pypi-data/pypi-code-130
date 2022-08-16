from setuptools import setup, find_packages

classifiers = [
    'Development Status :: 5 - Production/Stable',
    'Intended Audience :: Education',
    'Operating System :: Microsoft :: Windows :: Windows 10',
    'License :: OSI Approved :: MIT License',
    'Programming Language :: Python :: 3'
]

setup(
    name = 'helloworldah',
    version='0.0.1',
    description='prints hello world',
    Long_description = open('README.txt').read() + '\n\n' + open('CHANGELOG.txt').read(),
    url='',
    author='Ashim Khanal',
    author_email = 'ashimkhanal18@gmail.com ',
    license = 'MIT',
    classifiers=classifiers,
    keywords='printhelloworld',
    packages=find_packages(),
    install_requires=['']
)