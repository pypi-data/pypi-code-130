#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""Baicaoyuan

Usage:
  baicaoyuan init [(-v|-d)] [<directory>]
  baicaoyuan ghost <url> <username> <password>
  baicaoyuan [(-v|-d)] [-c | --config <config_file_path>] [<directory>]
  baicaoyuan (-h | --help)
  baicaoyuan --version

Options:
  -c --config   Config file path.
  -v            Visiable.
  -d            Show Debug.
  -h --help     Show help.
  --version     Show version.
"""

import logging
from docopt import docopt

import baicaoyuan
from baicaoyuan import site
from baicaoyuan.logger import init_logger

def main():
    """Read command line arguments and generate site
    """
    args = docopt(__doc__, version='Baicaoyuan Community '+baicaoyuan.version)

    directory = args.get('<directory>', './') or './'
    config_path = args.get('<config_file_path>', None)

    visiable = args.get('-v', False)
    debug = args.get('-d', False)

    if debug:
        init_logger(logging.DEBUG)
    elif visiable:
        init_logger(logging.VISIABLE)
    else:
        init_logger(logging.INFO)

    if args['init']:
        logging.info('Init Baicaoyuan environments')
        site.Site.init(directory)
        exit(0)

    blog = site.Site(directory)

    logging.info('Loading configurations...')
    try:
        blog.load_config(config_path)
    except Exception as e:
        logging.critical(e.args[0])
        exit(-1)
        
    if args['ghost']:
        url = args.get('<url>')
        user = args.get('<username>')
        password = args.get('<password>')
        if not url or not user or not password:
            logging.critical('Invalid arguments')
            exit(-1)
        blog.push(url, user, password)
        exit(0)

    logging.info('Generating...')
    blog.generate()

if __name__ == '__main__':
    main()
