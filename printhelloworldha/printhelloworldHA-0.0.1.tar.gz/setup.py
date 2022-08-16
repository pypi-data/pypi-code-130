from setuptools import setup, find_packages



VERSION = '0.0.1'
DESCRIPTION = 'Print Hello World'
LONG_DESCRIPTION = "A Package that print Hello WOrld Statement"

classifiers = [
    'Development Status :: 5 - Production/Stable',
    'Intended Audience :: Education',
    'Operating System :: Microsoft :: Windows :: Windows 10',
    'Operating System :: MacOS :: MacOS X',
    'License :: OSI Approved :: MIT License',
    'Programming Language :: Python :: 3'
]

setup(
    name='printhelloworldHA',
    version=VERSION,
    author = "Ashim Khanal,Hanieh Rastegar",
    author_email = "<ashimkhanal18@gmail.com>", 
    #description='A sample Python project that pritns hello world',
    #long_description=open('README.txt').read()+ '\n\n' + open('CHANGELOG.txt').read(),
    description = DESCRIPTION,
    long_description = LONG_DESCRIPTION,
    
    url='',
    license='MIT',
    classifiers=classifiers,
    keywords='HelloWorld',
    packages=find_packages(),
    install_requires=[]
)