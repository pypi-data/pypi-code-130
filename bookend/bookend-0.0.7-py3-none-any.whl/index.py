#!/usr/bin/env python3
# -*- coding: utf-8, vim: expandtab:ts=4 -*-

# previous license:
# Copyright (c) 2016 Anthony Pizzimenti - The MIT License (MIT)

# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at http://mozilla.org/MPL/2.0/.

# imports: library
import json
import os.path

# imports: project
from bookend.book import Book
from bookend.bookencoder import BookEncoder


def init():

    path = os.path.join(os.path.dirname(os.path.realpath(__file__)), 'lists.json')

    # no lists exist -> make a new list
    if not os.path.isfile(path):

        print('You don\'t have any booklists!')

        books = {
            'books': []
        }

        with open(path, 'w', encoding='UTF-8') as fh_list:
            json.dump(books, fh_list)

        path_last = path.split(os.pathsep)[-1]
        print('Created new list file at ', path_last)


def arg_search(term):

    search_term = term.lower()

    decoder = BookEncoder()
    decoder.decode()
    results = []

    for book in decoder.collection:

        if search_term in book['title'].lower():
            results.append(Book.formatbook(book, 'title'))
        elif search_term in book['author'].lower():
            results.append(Book.formatbook(book, 'author'))
        elif search_term in book['booklist'].lower():
            results.append(Book.formatbook(book, 'booklist'))

    for book in results:
        print(book)


def arg_list():

    decoder = BookEncoder()
    decoder.decode()

    for book in decoder.collection:
        print(Book.formatbook(book))


def arg_add():

    book = Book()
    encoder = BookEncoder()
    encoder.encode(book.__dict__)


def arg_checkout(title):

    decoder = BookEncoder()
    decoder.remove(title)
