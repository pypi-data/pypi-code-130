from setuptools import setup

with open('README.md') as f:
    long_description = f.read()

setup(
  name = 'OSDU-OnePF-BE',         # How you named your package folder (TSIClient)
  packages = ['OSDU-OnePF-BE'],   # Chose the same as "name"
  version = '1.0.0',      # Start with a small number and increase it with every change you make
  license='MIT',        # Chose a license from here: https://help.github.com/articles/licensing-a-repository
  long_description=long_description,
  long_description_content_type='text/markdown',  # This is important!
  author = 'Varshini',                   # Type in your name
  author_email = 'varshini.prasanna@accenture.com',      # Type in your E-Mail
  url = 'https://osdu-CoE@dev.azure.com/osdu-CoE/OSDU/_git/OSDU-OnePF-BE',   # Provide either the link to your github or to your website
  #download_url = 'NA',    # If you create releases through Github, then this is important
  keywords = ['Schema Mapping', 'OSDU', 'ONE PLATFORM'],   # Keywords that define your package best
  install_requires=[            # I get to this in a second
          'alive-progress','anyio','argcomplete','attrs','Authlib','azure-core','azure-storage-blob','boto3','botocore','cachelib','certifi','cffi','chardet','charset-normalizer','click','colorama','coloredlogs','crc32c','cryptography','cycler','Cython','docopt','docopt-subcommands','et-xmlfile','exit-codes','Flask','Flask-Cors','Flask-Session','fonttools','gensim','h11','httpcore','httpx','humanfriendly','idna','importlib-metadata','importlib-resources','isodate','itsdangerous','Jinja2','jmespath','joblib','jsonschema','kiwisolver','knack','lasio','MarkupSafe','matplotlib','msrest','nltk','numpy','oauthlib','openpyxl','packaging','pandas','pbr','Pillow','pyarrow','pycparser','Pygments','pymongo','pyparsing','pyreadline3','pyrsistent','python-dateutil','python-dotenv','pytz','PyYAML','regex','requests','requests-oauthlib','rfc3986','s3transfer','scikit-learn','scipy','seaborn','segpy','segyio','six','sklearn','smart-open','sniffio','stevedore','tabulate','threadpoolctl','tqdm','typing_extensions','urllib3','wbdutil','Werkzeug','zipp','jsonschema','lasio','pytest','coloredlogs'
      ],
  classifiers=[
    'Development Status :: 3 - Alpha',      # Chose either "3 - Alpha", "4 - Beta" or "5 - Production/Stable" as the current state of your package
    'Intended Audience :: Developers',      # Define that your audience are developers
    'Topic :: Software Development :: Build Tools',
    'License :: OSI Approved :: MIT License',   # Again, pick a license
    'Programming Language :: Python :: 3.9'      #Specify which pyhton versions that you want to support
  ],
)