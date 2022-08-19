from setuptools import setup
import pypandoc


try:  
    long_description = pypandoc.convert_file('README.md', 'rst')
except(IOError, ImportError):
    long_description = open('README.md').read()

setup(
    name='prediction_sys',
    version='0.0.4',    
    description='A example Python package',
    url='https://github.com/shuds13/prediction_sys',
    author='Merah Alaeddine',
    author_email='aladinemire@gmail.com',
    license='BSD 2-clause',
    packages=['prediction_sys'],
    install_requires=['sklearn'],
    long_description=long_description,
    classifiers=[
        'Development Status :: 1 - Planning',
        'Intended Audience :: Science/Research',
        'License :: OSI Approved :: BSD License',  
        'Operating System :: POSIX :: Linux',        
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
    ],
)