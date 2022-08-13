#!/usr/bin/python

from setuptools import setup, Extension

Version = '1.0'

longDesk = '''
ENG:

enscrypt(text) -> encrypt text

decrypt(text) -> decrypt the text

Encryption example:
    text = encrypt('this is text')

    print(text)

Conclusion:
    l2=z116S%$L8=!104S%$lv=y105S%$ln=5115S%$S%=632S%$Lb==105S%$...

decryption example:
    text = decrypt('l2=z116S%$L8=!104S%$lv=y105S%$ln=5115S%$S%=632S%$Lb==105S%$...')

    print(text)

Conclusion:
    this is text

RU:

enscrypt(text) -> шифрует текст

decrypt(text) -> расшифровает текст

Пример enscryption:
    text = enscrypt('this is text')

    print(text)

Вывод:
    l2=z116S%$L8=!104S%$lv=y105S%$ln=5115S%$S%=632S%$Lb==105S%$...

Пример decryption:
    text = decrypt('l2=z116S%$L8=!104S%$lv=y105S%$ln=5115S%$S%=632S%$Lb==105S%$...')

    print(text)

Вывод:
    this is text

'''

setup(
    name='encoderPy',
    version=Version,

    author='AlmazCode',
    author_email='diamondplay43@gmail.com',

    description='Simple encoder & text decryptor',
    long_description=longDesk,

    license='Apache License, Version 2.0, see LICENSE file',

    packages=['encoderPy'],

    classifiers=['License :: OSI Approved :: Apache Software License',
                'Operating System :: OS Independent',
                'Intended Audience :: End Users/Desktop',
                'Intended Audience :: Developers',
                'Programming Language :: Python',
                'Programming Language :: Python :: 3',
                'Programming Language :: Python :: 3.6',
                'Programming Language :: Python :: 3.7',
                'Programming Language :: Python :: 3.8',
                'Programming Language :: Python :: 3.9',
                'Programming Language :: Python :: 3.10',
                'Programming Language :: Python :: Implementation :: PyPy',
                'Programming Language :: Python :: Implementation :: CPython'
                ]
)