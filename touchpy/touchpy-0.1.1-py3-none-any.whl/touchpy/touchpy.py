#!/usr/bin/env python

from datetime import datetime
import os, sys

if len(sys.argv)==2:
	script_name = sys.argv[1] 
else:
	script_name = input('Enter script name:')


path = os.path.join(os.getcwd(), script_name if script_name.endswith('.py') else script_name+'.py')
if os.path.isfile(path):
	print(f'File {path} already exists. Exit!')
	sys.exit(1)

short_desc= input('Enter short description:')
long_desc=input('Enter long description:')
author=input('Enter your name:')
email=input('Enter your email:')
project=input('Enter project name:')
today=datetime.now().strftime('%Y-%m-%d')
year=datetime.now().strftime('%Y')

format = f'''#!/usr/bin/env python
"""{short_desc}

{long_desc}
"""

# Created On: {today} using touchpy 

# built-in modules

# third-party modules

__author__ = "{author}"
__copyright__ = "Copyright {year}, {project}"
__credits__ = ["{author}"] # add your name in this list if you have made improvements in this script
__license__ = None
__version__ = "0.0.1"
__maintainer__ = "{author}"
__email__ = "{email}"
__status__ = "Development"



if __name__=="__main__":
	pass
'''

with open(path, 'w') as f:
	f.write(format)
print(f'Created {path}!')
