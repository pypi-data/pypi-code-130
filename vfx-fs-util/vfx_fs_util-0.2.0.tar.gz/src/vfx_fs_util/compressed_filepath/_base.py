import os
import re
from glob import glob
from sre_constants import error as RegexError
from collections import defaultdict, OrderedDict
from itertools import chain, zip_longest
from .tokenize import Tokenizer
from .errors import (
    IterationPaddingMisMatch, MergeError,
    StringReprFormatError, IterationSetParseError,
    FilesNotLocal
)
from .iteration import IterationSet
from ..config import ITERATION_FORMATTING


class PartitionedFilepath(object):
    """A representation of a filepath that's split into interation sets and strings.
    
    The PartitionedFilepath class takes a filepath string and 
     splits it into sections of strings and sections of digits.
     
    The digits are stored in IterationSets so when merged, the 
     iteration sets can be combined.

    Args:
        filepath (str): '/path/to/dir/or/file.txt'
    """

    def __init__(self, filepath_string):

        self._strings = OrderedDict()
        self._iteration_sets = OrderedDict()

        self._setup(filepath_string)
        
    def _setup(self, filepath_string):

        num_string = ''
        alpha_string = ''

        counter = 0
        for item in filepath_string:

            if isinstance(item, str):

                if item.isdigit():
                    if alpha_string:
                        self._strings[counter] = alpha_string
                        counter += 1
                        alpha_string = ''

                    num_string += item

                else:
                    if num_string:
                        iteration_set = IterationSet(num_string)
                        self._iteration_sets[counter] = iteration_set
                        counter += 1
                        num_string = ''

                    alpha_string += item

        # If there were any partitions building before the loop ended
        if num_string:
            iteration_set = IterationSet(num_string)
            self._iteration_sets[counter] = iteration_set
            counter += 1

        if alpha_string:
            self._strings[counter] = alpha_string
            counter += 1

    def __str__(self):
        return ''.join([str(item) for item in self])

    def __repr__(self):
        return str(self)

    def __len__(self):
        return len(self._strings) + len(self._iteration_sets)

    def __iter__(self):
        """
        The strings and iteration sets are kept in different DefaultDicts,
         iterating over a partitioned path reassembles the 2 DefaultDicts and,
        yields them.
        """
        merged_items = self._strings.copy()
        merged_items.update(self._iteration_sets)

        for i in sorted(merged_items.keys()):
            yield merged_items[i]

    def items(self):
        for item in self:
            yield item

    @staticmethod
    def from_items(items):
        new_partitioned_path = PartitionedFilepath('')
        for i, item in enumerate(items):
            if isinstance(item, IterationSet):
                new_partitioned_path._iteration_sets[i] = item
            else:
                new_partitioned_path._strings[i] = item

        return new_partitioned_path

    @staticmethod
    def from_str_repr(formatted_string, iteration_format_string):

        items = PartitionedFilepath.split(formatted_string, iteration_format_string)
        return PartitionedFilepath.from_items(items)

    @staticmethod
    def split(input_string, format_string):
        """Splits a string by iteration sets.
        
        This method expects strings of a certain format.
        
        It will parse the string for certain template patterns,
         convert those into regex and split the string via re.split

        Args:
            formatted_string (str): A string to be split

        Returns:
            list: list of strings representing IterationSets
            list: list of strings
        """
        
        # Parses the input string for all potential IterationSets
        # This will produce a list of IterationSets, created from string
        iteration_strings = Tokenizer.find_all(input_string, format_string)

        # Splits the input string by the format string
        # This will produce all the strings that are not potential IterationSets
        iteration_format = Tokenizer.to_regex(format_string)
        strings = re.split(iteration_format, input_string, flags=re.I)
            
        iteration_sets = [
            IterationSet.from_string(x, format_string) for x in iteration_strings
        ]
        
        # Take both the list of IterationSets and strings and,
        # reassemble them into a single sequential list
        if strings and input_string.startswith(strings[0]):
            items = [
                x
                for x in chain(
                    *zip_longest(strings, iteration_sets)
                ) if x is not None
            ]
        else:
            items = [
                x
                for x in chain(
                    *zip_longest(iteration_sets, strings)
                ) if x is not None
            ]

        return items

    @staticmethod
    def merge(partitioned_path1, partitioned_path2, iteration_set_index=0):
        """
        Merge 2 PartitionedFilepaths together by comparing the strings and iteration sets.
        If the strings do not equal each other, a MergeError is thrown.
        IterationSets will throw a MergeError or IterationPaddingMisMatch error
         if 2 FrameSets cannot be merged.
        """
        
        if len(partitioned_path1) != len(partitioned_path2):
            raise MergeError('Partitioned paths are different length')

        merged = []
        iteration_set_counter = 0
        for item1, item2 in zip(partitioned_path1, partitioned_path2):
            if isinstance(item1, IterationSet) and isinstance(item2, IterationSet):

                to_append = item1
                if iteration_set_counter == iteration_set_index:
                    merged_iteration_set = IterationSet.merge(item1, item2)
                    to_append = merged_iteration_set
                elif item1 != item2:
                    raise MergeError('Cannot merge "{}" -> "{}", \n{}\n->{}'.format(
                        item1, 
                        item2,
                        partitioned_path1,
                        partitioned_path2
                    ))

                merged.append(to_append)
                iteration_set_counter += 1

            elif item1 != item2:
                raise MergeError('Cannot merge "{}" -> "{}", \n{}\n->{}'.format(
                    item1, 
                    item2,
                    partitioned_path1,
                    partitioned_path2
                ))
            else:
                merged.append(item1)

        new_partitioned_path = PartitionedFilepath.from_items(merged)

        return new_partitioned_path

    @staticmethod
    def compress_partitions(partitioned_filepaths, iteration_set_index=0):
        
        already_merged = []
        for partitioned_path in partitioned_filepaths:

            if not already_merged:
                already_merged.append(partitioned_path)
                continue

            merged = False
            for i, merged_path in enumerate(already_merged):
                try:
                    new_partition = PartitionedFilepath.merge(
                        partitioned_path, 
                        merged_path, 
                        iteration_set_index=iteration_set_index
                    )
                    already_merged[i] = new_partition
                    merged = True
                    break
                except MergeError:
                    pass
            
            if not merged:
                already_merged.append(partitioned_path)

        return already_merged

    def iteration_sets(self):
        return list(self._iteration_sets.values())

    def strings(self):
        return self._strings.values()

    def template(self):
        ret_str = ''
        for item in self:
            if isinstance(item, IterationSet):
                ret_str += '<iteration_set>'
            else:
                ret_str += '<string>'
        return ret_str


class CompressedFilepath(object):

    TEMPLATE_STRINGS = ()
    STR_REPR_FORMAT = ''

    def __init__(self, partitioned_filepath):
        self._partitioned_filepath = partitioned_filepath
        self._size = 0

    def __str__(self):
        return str(self._partitioned_filepath)

    def __repr__(self):
        return str(self._partitioned_filepath)

    def __len__(self):
        # length = 0
        # for iteration_set in self._partitioned_filepath.iteration_sets():
        #     length += len(iteration_set)
        # return length
        return len(self.expand())

    def __iter__(self):
        for item in self.expand():
            yield item

    @classmethod
    def compress(cls, strings, include=None, exclude=None):

        strings = filter_string_list(strings, include=include, exclude=exclude)

        partitioned_filepaths = map(PartitionedFilepath, strings)

        sorted_partitions = defaultdict(list)

        for partitioned_path in partitioned_filepaths:
            sorted_partitions[len(partitioned_path.iteration_sets())].append(partitioned_path)

        total_merged = []
        for num_of_iteration_sets, partitioned_paths in sorted_partitions.items():
            for i in reversed(range(num_of_iteration_sets)):
                partitioned_paths = PartitionedFilepath.compress_partitions(partitioned_paths, i)
            total_merged.extend(partitioned_paths)

        return [cls(partitioned_path) for partitioned_path in total_merged]

    @staticmethod
    def expand_many(compressed_filepaths):
        expanded = []

        for compressed_path in compressed_filepaths:
            expanded.extend(compressed_path.expand())

        return expanded

    @classmethod
    def parse(
        cls, input_string, iteration_set_format='{first}-{last}', check_disk=True
    ):

        partitioned_filepath = PartitionedFilepath.from_str_repr(
            input_string,
            iteration_set_format
        )

        items = []
        has_empty_iteration_sets = False
        if check_disk:
            for item in partitioned_filepath:
                if isinstance(item, IterationSet):
                    if item.is_empty():
                        has_empty_iteration_sets = True
                        items.append('*')
                else:
                    items.append(item)

        if has_empty_iteration_sets:
            glob_path = ''.join(items)
            compressed = cls.compress(glob(glob_path))

            if not compressed:
                raise FilesNotLocal('{} cannot be found locally'.format(glob_path))

            return compressed[0]

        return cls(partitioned_filepath)

    def format(self, iteration_set_format):
        return ''.join([
            item.format(iteration_set_format)
            for item in self._partitioned_filepath
        ])

    def expand(self):
        path_strings = []
        for item in self._partitioned_filepath:

            if not path_strings:
                if isinstance(item, IterationSet):
                    path_strings.extend(list(item.str_iter()))
                else:
                    path_strings.append(item)
                continue

            if isinstance(item, IterationSet):
                new_strings = []
                for iteration in item.str_iter():
                    new_strings.extend(
                        ['{}{}'.format(x, iteration) for x in path_strings]
                    )
                path_strings = new_strings
            else:
                path_strings = ['{}{}'.format(x, item) for x in path_strings]

        return path_strings

    def has(self, string):
        return string in self.expand()
        # partitioned_string = PartitionedFilepath(string)
        # for item1, item2 in zip(partitioned_string, self):
        #     if isinstance(item1, IterationSet) and isinstance(item2, IterationSet):
        #         try:
        #             # This should be a single item iteration set.
        #             # Returning it in string form to check it's padding.
        #             item = next(item1.str_iter())
        #             return item2.has(item)
        #         except StopIteration:
        #             # This should not happen
        #             return False
        #     elif item1 != item2:
        #         return False

    def relative(self):
        return os.path.relpath(str(self))

    def absolute(self):
        return os.path.abspath(str(self))

    def realpath(self):
        return os.path.realpath(str(self))

    def str_repr(self, iteration_format=None):

        if not self.STR_REPR_FORMAT:
            return self.format(iteration_format)

        try:
            return self.STR_REPR_FORMAT.format(**self._filepath_attributes)
        except KeyError:
            return self.format(iteration_format)

    def size(self):
        if self._size:
            return self._size

        for item in self.expand():
            try:
                self._size += os.stat(item).st_size
            except OSError:
                # This isn't assuming the filepaths are local
                pass

        return self._size


def filter_string_list(string_list, include=None, exclude=None):
    """
    Filter a list of filepaths based on include and exclude patterns
    The current behavior:
        includes:
            loop through the includes:
                each include is applied to the set of paths that is the result of the previous filter
        excludes:
            loop through the excludes:
                each exclude is applied to the set of paths that is the result of the previous filter
        if there is a conflict between the includes and the excludes, the exclude wins

    :param sequence_item_list: list of filepath strings
    :type sequence_item_list: list
    :param include: list of regexes to include in the return
    :type include: list
    :param exclude: list of regexes to exclude in the return
    :type exclude: list
    :return:
    """

    to_include = set(string_list)
    if include:
        if not isinstance(include, (list, set)):
            raise TypeError('include must be a list of strings/regexes')

        for inc in include:
            try:
                to_include = (set(x for x in to_include if re.search(inc, x, re.I)))
            except RegexError:
                continue

    if exclude:
        if not isinstance(exclude, (list, set)):
            raise TypeError('exclude must be a list of strings/regexes')

        for exc in exclude:
            try:
                to_include = set(x for x in to_include if not re.search(exc, x, re.I))
            except RegexError:
                continue

    return list(to_include)
