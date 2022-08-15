from setuptools import setup

setup(
    name='onlinecsat',
    version='0.1.1',    
    description='OnlineCSAT use case',
    author='John Harney',
    author_email='John.Harney@Dell.com',
    packages=['onlinecsat'],
    install_requires=[
                      'pandas',
                      'numpy',    
                      'scipy',
                      'nltk',
                      'sklearn'
                      ],

    classifiers=[
        'Development Status :: 1 - Planning',
        'Intended Audience :: Science/Research',
        'License :: OSI Approved :: BSD License',  
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
    ],
)