#!/usr/bin/env python3

import argparse

parser = argparse.ArgumentParser()
parser.add_argument('--bar')
args = parser.parse_args()

if 'foo' in args:
    print('foo in args')
if 'bar' in args:
    print('bar in args')
