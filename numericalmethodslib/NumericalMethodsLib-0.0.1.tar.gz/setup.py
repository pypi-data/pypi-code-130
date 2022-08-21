from setuptools import setup, find_packages

classifiers = [
    'Development Status :: 5 - Production/Stable',
    'Intended Audience :: Science/Research',
    'Operating System :: Microsoft :: Windows :: Windows 11',
    'License :: OSI Approved :: MIT License',
    'Programming Language :: Python :: 3'
]

setup(
    name='NumericalMethodsLib',
    version='0.0.1',
    description='Numerical method functions',
    Long_description=open('README.txt').read() + '\n\n' + open('CHANGELOG.txt').read(),
    url='',
    author='Terry Slevin',
    author_email='TerrenceSlevin1999@gmail.com',
    license='MIT',
    classifiers=classifiers,
    keywords='numerical methods',
    packages=find_packages(),
    install_requires=['']
)