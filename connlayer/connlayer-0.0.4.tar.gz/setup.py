from distutils.core import setup

from setuptools import find_packages

setup(
    name='connlayer',  # How you named your package folder (MyLib)
    packages=['connlayer'],  # Chose the same as "name"
    version='0.0.4',  # Start with a small number and increase it with every change you make
    license='MIT',  # Chose a license from here: https://help.github.com/articles/licensing-a-repository
    description='Just an example of connection layer',  # Give a short description about your library
    author='Kazi Javed Alam',  # Type in your name
    author_email='qazijavedjim007@gmail.com',  # Type in your E-Mail
    url='https://github.com/qazijaved/abstractlayer',  # Provide either the link to your github or to your website
    download_url='https://github.com/qazijaved/abstractlayer/archive/refs/heads/main.zip',  # I explain this later on
    keywords=['connection layer', 'abstract layer for different connection', 'abstract'],  # Keywords that define your package best
    classifiers=[
        'Development Status :: 3 - Alpha',
        # Chose either "3 - Alpha", "4 - Beta" or "5 - Production/Stable" as the current state of your package
        'Intended Audience :: Developers',  # Define that your audience are developers
        'Topic :: Software Development :: Build Tools',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.9',
    ],
)
