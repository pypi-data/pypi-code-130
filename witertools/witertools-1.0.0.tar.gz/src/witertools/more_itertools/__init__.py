"""Export a function for each  finite iterator from more-itertools.  """
import more_itertools as mi
import itertools as i
from .. import iterator_to_list_function, iterator_name_to_list_function
import sys
this_module=sys.modules[__name__]

#the result of dir on more_itertools
more_itertools_dir=['AbortThread', 'SequenceView', 'UnequalIterablesError', '__builtins__', '__cached__', '__doc__', '__file__', '__loader__', '__name__', '__package__', '__path__', '__spec__', '__version__', 'adjacent', 'all_equal', 'all_unique', 'always_iterable', 'always_reversible', 'before_and_after', 'bucket', 'callback_iter', 'chunked', 'chunked_even', 'circular_shifts', 'collapse', 'collate', 'combination_index', 'consecutive_groups', 'consume', 'consumer', 'convolve', 'count_cycle', 'countable', 'difference', 'distinct_combinations', 'distinct_permutations', 'distribute', 'divide', 'dotproduct', 'duplicates_everseen', 'duplicates_justseen', 'exactly_n', 'filter_except', 'first', 'first_true', 'flatten', 'groupby_transform', 'grouper', 'ichunked', 'iequals', 'ilen', 'interleave', 'interleave_evenly', 'interleave_longest', 'intersperse', 'is_sorted', 'islice_extended', 'iter_except', 'iterate', 'last', 'locate', 'longest_common_prefix', 'lstrip', 'make_decorator', 'map_except', 'map_if', 'map_reduce', 'mark_ends', 'minmax', 'more', 'ncycles', 'nth', 'nth_combination', 'nth_or_last', 'nth_permutation', 'nth_product', 'numeric_range', 'one', 'only', 'pad_none', 'padded', 'padnone', 'pairwise', 'partition', 'partitions', 'peekable', 'permutation_index', 'powerset', 'prepend', 'product_index', 'quantify', 'raise_', 'random_combination', 'random_combination_with_replacement', 'random_permutation', 'random_product', 'recipes', 'repeat_each', 'repeat_last', 'repeatfunc', 'replace', 'rlocate', 'roundrobin', 'rstrip', 'run_length', 'sample', 'seekable', 'set_partitions', 'side_effect', 'sliced', 'sliding_window', 'sort_together', 'split_after', 'split_at', 'split_before', 'split_into', 'split_when', 'spy', 'stagger', 'strictly_n', 'strip', 'subslices', 'substrings', 'substrings_indexes', 'tabulate', 'tail', 'take', 'time_limited', 'triplewise', 'unique_everseen', 'unique_in_window', 'unique_justseen', 'unique_to_each', 'unzip', 'value_chain', 'windowed', 'windowed_complete', 'with_iter', 'zip_broadcast', 'zip_equal', 'zip_offset']
more_itertools_no_dunder = i.filterfalse(lambda s: "__" in s, more_itertools_dir )


for fn in more_itertools_no_dunder:
    setattr(this_module,fn,iterator_name_to_list_function(mi,fn))

 