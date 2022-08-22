from setuptools import setup, find_packages

setup(
    name='shorter-py',
    version='0.1.0',
    packages=find_packages(),
    package_dir={'shorter-py': 'shorterpy'},
    include_package_data=True,
    license='MIT',
    description='A Python library for interacting with the Shorter protocol',
    long_description=open('README.md').read(),
    long_description_content_type='text/markdown',
    author='Naveen Veluswamy',
    author_email='velnaveen99@gmail.com',
    url='https://github.com/DeveloperInProgress/ShorterPy',
    keywords=['ethereum', 'blockchain', 'shorter', 'contract', 'python'],
    install_requires=[
        'web3',
        'eth-account',
    ],

    classifiers=[
        'Development Status :: 3 - Alpha',
        'Intended Audience :: Developers',
        'Topic :: Software Development :: Build Tools',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3.9',
    ],
)