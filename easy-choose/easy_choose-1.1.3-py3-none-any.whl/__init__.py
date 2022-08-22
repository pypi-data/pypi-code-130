# Import functions from chooser.py

from .chooser import chooser
from .chooser import sortchooser
from .chooser import revchooser

# Import functions from tests.py

from .tests import testnumbers
from .tests import testalphabet_lower
from .tests import testalphabet_upper
from .tests import testascii

__version__ = '1.1.3'

# Tests
def tests(num: int=1, only: bool=False, number: int=10, low: int=32, up: int=127):
    '''Test all test functions in the test.py
    number: See testnumbers()
    low/up: See testascii()'''
    testlist = ['testnumbers', 'testalphabet_lower',
    'testalphabet_upper', 'testascii']
    print('Test all test functions in the test.py')
    print('Testing: testnumbers()')
    print('Result(s): '+testnumbers(number, num, only))
    print('Testing: testalphabet_lower()')
    print('Result(s): '+testalphabet_lower(num, only))
    print('Testing: testalphabet_upper()')
    print('Result(s): '+testalphabet_upper(num, only))
    print('Testing: testascii()')
    print('Result(s): '+testascii(num, only, low, up))
    print()
    print('All functions tested.')