#!/usr/bin/env python

from io import open
from setuptools import setup

"""
:authors: two-it2022
:license: Apache License, Version 0.5, see LICENSE file
:copyright: (c) 2022 two-it2022
"""

version = '0.0.5'
'''
with open('__readme__.md', encoding='utf-8') as f:
      long_description = f.read()
'''

long_description = '''1. Installing
Open the CMD. And enter: pip install speaker_listener or pip install speaker_listener==[nevest_version]
Create the file [your_file_name].py and write in file: import speaker_listener or from speaker import *

2. Commands

speak(text*, speed*, gender*) - This command reads text, you can choose voice gender and read speed.
listen(pausetime*, language*) - This command can listen to the user and understand what he said. You can choose the language and pause time.


'''


setup(
      name='speaks',
      version=version,

      author='two-it2022',
      author_email='kodland.group@gmail.com',

      description="text-to-speech module for Python",
      long_description=long_description,
      #long_description_content_type='text/markdown',

      url='https://github.com/TwoIt202/Speaker',
      download_url='https://github.com/TwoIt202/Speaker/raw/89a99b41e4c3565c661691dfae0054e5ea600a13/speaker.zip'.format(
            version
      ),

      license='Apache License, Version 0.5, see LICENSE file',

      packages=['speaks'],
      install_requires=['gtts', 'SpeechRecognition==3.8.1', 'playsound', 'pyaudio'],

      classifiers=[
            'License :: OSI Approved :: Apache Software License',
            'Operating System :: OS Independent',
            'Intended Audience :: End Users/Desktop',
            'Intended Audience :: Developers',
            'Programming Language :: Python',
            'Programming Language :: Python :: 3',
            'Programming Language :: Python :: 3.6',
            'Programming Language :: Python :: 3.7',
            'Programming Language :: Python :: 3.8',
            'Programming Language :: Python :: Implementation :: PyPy',
            'Programming Language :: Python :: Implementation :: CPython',
      ]

)