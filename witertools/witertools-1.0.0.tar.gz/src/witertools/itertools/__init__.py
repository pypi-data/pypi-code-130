"""Export a function for each  finite iterators from itertools.  """
import itertools as i
from .. import iterator_to_list_function, iterator_name_to_list_function
import sys
this_module=sys.modules[__name__]
finite_iterators = [ 'accumulate', 'chain', 'combinations', 'combinations_with_replacement', 'compress', 'dropwhile', 'filterfalse', 
'groupby', 'islice', 'permutations', 'product',  'starmap', 'takewhile', 'tee', 'zip_longest']


for fn in finite_iterators:
    setattr(this_module,fn,iterator_name_to_list_function(i,fn))

 