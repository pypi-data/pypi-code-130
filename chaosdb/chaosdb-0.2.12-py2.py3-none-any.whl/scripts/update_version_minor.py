#!/usr/bin/env python
import os
import re

package = 'chaosdb'
initfile = '../'+package+'/__init__.py'

def update_version(initfile):
    with open(initfile) as x: 
        text = x.readlines()
        for line in text:
            if re.match("^__version__", line.strip()):
                version=(line.split('='))[1]
                version = version.replace("'",'')
                digits = version.split('.')
                minor = int(digits[-1]) + 1
                separator = '.'
                new_version = "{}.{}".format(separator.join(digits[0:-1]), minor)
                return new_version
    return none



if os.path.isfile(initfile) is False:
    exit()

new_version = update_version(initfile)
print(new_version)




