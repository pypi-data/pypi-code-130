from distutils.core import setup

setup(
    name = 'Hamen',         # How you named your package folder (MyLib)
    packages = ['Hamen'],   # Chose the same as "name"
    version = '1.0.0',      # Start with a small number and increase it with every change you make
    license='GNU',        # Chose a license from here: https://help.github.com/articles/licensing-a-repository
    description = 'Hamen is an API',   # Give a short description about your library
    author = 'Hamen',                   # Type in your name
    author_email = 'hamen.connect@gmail.com',      # Type in your E-Mail
    url = 'https://hamen.tech/api',   # Provide either the link to your github or to your website
    download_url = 'https://github.com/user/reponame/archive/v_01.tar.gz',    # I explain this later on
    keywords = ['hamen', 'tools', 'tool', 'efficient', 'fast', 'faster', 'easy'],   # Keywords that define your package best
    install_requires=[            # I get to this in a second
            'colorsys'
        ],
    classifiers=[
        'Development Status :: 5 - Production/Stable',      # Chose either "3 - Alpha", "4 - Beta" or "5 - Production/Stable" as the current state of your package
        'Intended Audience :: Developers',      # Define that your audience are developers
        'Topic :: Software Development :: Build Tools',
        'License :: OSI Approved :: MIT License',   # Again, pick a license
        'Programming Language :: Python :: 3',      #Specify which pyhton versions that you want to support
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3.9',
        'Programming Language :: Python :: 3.10',
    ],
)