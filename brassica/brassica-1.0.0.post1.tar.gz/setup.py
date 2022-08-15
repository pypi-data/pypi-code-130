import setuptools

setuptools.setup(
    name = 'brassica',
    version = '1.0.0.post1',
    author = 'Mike Lee',
    author_email = 'random.deviate@gmail.com',
    description = 'Interpreter for 1975 Altair/Microsoft BASIC',
    long_description = open('README.md').read(),
    long_description_content_type = 'text/markdown',
    packages = setuptools.find_packages(),
    classifiers = [
                  'Development Status :: 5 - Production/Stable',
                  'Environment :: Console',
                  'Intended Audience :: Education',
                  'Intended Audience :: End Users/Desktop',
                  'Intended Audience :: Other Audience',
                  'License :: OSI Approved :: GNU General Public License v3 or later (GPLv3+)',
                  'Natural Language :: English',
                  'Operating System :: OS Independent',
                  'Programming Language :: Basic',
                  'Programming Language :: Python :: 3.9',
                  'Programming Language :: Python :: 3.10',
                  'Topic :: Education',
                  'Topic :: Games/Entertainment',
                  'Topic :: Software Development :: Interpreters'
                  ],
    python_requires = '>=3.9',
    include_package_data = True,
    package_data = {'': ['BASIC/*.bas']},
    zip_safe = True
)
