#!/usr/bin/env python3
# -*- coding: utf-8, vim: expandtab:ts=4 -*-

# previous license:
# Copyright (c) 2016 Anthony Pizzimenti - The MIT License (MIT)

# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at http://mozilla.org/MPL/2.0/.

# imports: library
from termcolor import colored


class Book:

    def __init__(self):

        self.title = input('Title: ')
        self.author = input('Author: ')
        self.callnumber = input('Call Number: ')
        self.booklist = input('List Name: ')

    @staticmethod
    def formatbook(book, param=None):

        title = colored(book['title'], 'green') if param == 'title' else book['title']
        author = colored(book['author'], 'green') if param == 'author' else book['author']
        booklist = colored(book['booklist'], 'green') if param == 'booklist' else book['booklist']

        formatted = f'''
        Title:\t\t{title}
        Author:\t\t{author}
        Call Number:\t{book["callnumber"]}
        List:\t\t{booklist}
        '''

        return formatted
