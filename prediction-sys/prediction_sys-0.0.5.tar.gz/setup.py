from setuptools import setup
import pypandoc
import io

with io.open('README.md', encoding="utf-8") as f:
    long_description = f.read()

setup(
    name='prediction_sys',
    version='0.0.5',    
    description='A example Python package',
    url='https://github.com/shuds13/prediction_sys',
    author='Merah Alaeddine',
    author_email='aladinemire@gmail.com',
    license='BSD 2-clause',
    packages=['prediction_sys'],
    install_requires=['sklearn'],
    long_description=long_description,
    long_description_content_type='text/markdown',
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