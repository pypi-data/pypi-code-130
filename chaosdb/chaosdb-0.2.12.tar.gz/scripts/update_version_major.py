#!/usr/bin/env python
import os
import re

package = 'chaosdb'
initfile = '../'+package+'/__init__.py'
if os.path.isfile(initfile) is False:
    exit()
with open(initfile) as x: 
    text = x.readlines()
    for line in text:
        if re.match("^__version__", line.strip()):
            version=(line.split('='))[1]
            version = version.replace("'",'')
            digits = version.split('.')
            major = int(digits[-2]) + 1
            separator = '.'
            new_version = "{}.{}.{}".format(
                    separator.join(digits[0:-2]), 
                    major,
                    digits[-1])
            print(new_version)

