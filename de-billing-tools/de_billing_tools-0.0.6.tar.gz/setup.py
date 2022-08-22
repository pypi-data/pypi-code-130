import setuptools

# Reads the content of your README.md into a variable to be used in the setup below
with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setuptools.setup(
    name='de_billing_tools',                           # should match the package folder
    packages=['de_billing_tools'],                     # should match the package folder
    version='0.0.6',                                # important for updates
    license='MIT',                                  # should match your chosen license
    description='Python tools for the billing team at Diamond Energy',
    long_description=long_description,              # loads your README.md
    long_description_content_type="text/markdown",  # README.md is of type 'markdown'
    author='Jason Mack',
    author_email='jason.mack@y7mail.com',
    url='https://github.com/meermeerkat/DE-Billing-Tools', 
    project_urls = {                                # Optional
    },
    install_requires=['pandas', 'lxml'],                  # list all packages that your package uses
    keywords=["diamond energy", "billing"], #descriptive meta-data
    classifiers=[                                   # https://pypi.org/classifiers
        'Development Status :: 3 - Alpha',
        'Intended Audience :: Developers',
        'Topic :: Software Development :: Documentation',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3.9',
        'Programming Language :: Python :: 3.10'
    ],
    
    download_url="https://github.com/meermeerkat/DE-Billing-Tools/archive/refs/tags/0.0.6.tar.gz",
)