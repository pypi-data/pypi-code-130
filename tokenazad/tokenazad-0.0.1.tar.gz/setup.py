from setuptools import setup, find_packages

setup(
    name='tokenazad',
    packages=find_packages(include=['tokenazad']),
    version='0.0.1',
    description='A simple tool to get Azure AD Tokens with MSAL and set them as environment variables',
    long_description=open('README.md').read(),
    long_description_content_type='text/markdown',
    author='Dagoberto Romer',
    author_email="dagoromer85@gmail.com",
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.8',
    install_requires=[
        'msal>=1.17.0',
        'python-dotenv>=0.20.0',
    ],
    setup_requires=['pytest-runner'],
    tests_require=[
        'pytest==7.1.2',
        'pytest-cov==3.0.0',
    ],
    test_suite='tests',
)
