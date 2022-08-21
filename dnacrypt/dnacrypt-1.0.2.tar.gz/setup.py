from setuptools import setup

setup(
    name = 'dnacrypt',
    version = '1.0.2',
    author = 'Rodrigo Forti',
    author_email = 'rodrigofort14@gmail.com',
    packages = ['dnacrypt'],
    description = "A simple code for encryption based on the genetic code of DNA",
    long_description = 'A simple code for encryption based on the genetic code of DNA '
                        + 'you can also use to decrypt too ',
    url = 'https://github.com/FortiHub/dnacrypt',
    project_urls = {
        'Código fonte': 'https://github.com/FortiHub/dnacrypt',
        'Download': 'https://github.com/FortiHub/dnacrypt/archive/refs/heads/main.zip'
    },
    license = 'MIT',
    keywords = 'Encrypt based DNA code',
    classifiers = [
        'Development Status :: 5 - Production/Stable',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Natural Language :: Portuguese (Brazilian)',
        'Operating System :: OS Independent',
        'Topic :: Software Development :: Internationalization',
        'Topic :: Scientific/Engineering :: Physics'
    ]
)

