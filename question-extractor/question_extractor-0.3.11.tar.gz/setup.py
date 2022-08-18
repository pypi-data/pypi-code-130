from setuptools import setup, find_packages

setup(
    name='question_extractor',
    version='0.3.11',
    license='MIT',
    author='Krishna Moorthy Babu',
    packages=find_packages('src'),
    package_dir={'':'src'},
    url='',
    keywords= 'question_extractor',
    package_data={'': ['data/*', 'models/*']},
    install_requires=[
        'numpy',
        'keras',
        'tensorflow',
    ],

)