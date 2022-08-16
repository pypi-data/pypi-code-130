from setuptools import setup


with open('README.md') as f:
    long_description = f.read()

setup(
    name='markdown_editing',
    version='0.2.0',
    description='Markdown extension for editing marks and comments',
    long_description=long_description,
    long_description_content_type='text/markdown',
    author='Madison Scott-Clary',
    author_email='makyo@drab-makyo.com',
    packages=['markdown_editing'],
    install_requires=['markdown'],
    url='https://github.com/makyo/markdown-editing',
    classifiers=[
        'Development Status :: 4 - Beta',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
        'Topic :: Text Processing',
        'Programming Language :: Python :: 3',
    ])
