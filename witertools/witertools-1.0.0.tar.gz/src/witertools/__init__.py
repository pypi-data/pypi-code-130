"""Witertools - Tools to wrap iterator functions, to consume the whole iterator and return a list.  Avoid sprinklist list(...)
throughout your code when you need a list instead of an interator.  

"""
__version__="1.0.0"

import builtins
from .iterator_to_list import iterator_to_list_function,iterator_name_to_list_function
import sys
import builtins as b
built_in_iterators=["filter","map","zip"]
this_module=sys.modules[__name__]
for fn in built_in_iterators:
    setattr(this_module,fn,iterator_name_to_list_function(b,fn))