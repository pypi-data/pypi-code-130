from ..config import ITERATION_FORMATTING
from .tokenize import Tokenizer
from .errors import (
    MergeError,
    IterationPaddingMisMatch,
    IterationSetParseError,
    StringReprFormatError
)


class IterationRange(object):

    def __init__(self, first, last):
        self.first = first
        self.last = last

    def __str__(self):
        return '{first}-{last}'.format(first=self.first, last=self.last)

    def __repr__(self):
        return str(self)


class IterationSet(object):

    def __init__(self, *iterations, step=1, padding=0):
        self._iteration_range_groups = {}
        self.step = step
        self.padding = padding

        for iteration in iterations:
            self.add(iteration)

    def __str__(self):
        joined_ranges = self.str_ranges()

        if self.is_single():
            return joined_ranges
        else:
            return '{{{}}}'.format(joined_ranges)

    def __repr__(self):
        return str(self)

    def __iter__(self):
        for iteration_range in self.iteration_ranges():
            for iteration_int in range(
                iteration_range.first,
                iteration_range.last + 1,
                self.step
            ):
                yield iteration_int

    def str_iter(self):
        for item in self:
            yield str(item).zfill(self.padding)

    def str_ranges(self):
        string_ranges = []
        for iteration_range in self.iteration_ranges():
            if self.is_single():
                iteration = str(iteration_range.first).zfill(self.padding)
                string_ranges.append('{iteration}'.format(iteration=iteration))
            else:
                first = str(iteration_range.first).zfill(self.padding)
                last = str(iteration_range.last).zfill(self.padding)
                if first == last:
                    string_ranges.append('{first}'.format(first=first))
                else:
                    string_ranges.append('{first}-{last}'.format(first=first, last=last))

        return ','.join(string_ranges)

    def __len__(self):
        length = 0
        for group in self.iteration_ranges():
            group_length = group.last - group.first + 1
            length += group_length
        return length

    def __eq__(self, other):

        if not isinstance(other, IterationSet):
            return False

        # Check if the groups are the same length
        if len(self) != len(other):
            return False

        # Iterate over the iteration range groups and make sure they are equal
        for group1, group2 in zip(self.iteration_ranges(), other.iteration_ranges()):
            if group1.first != group2.first or group1.last != group2.last:
                return False
 
        return True

    @staticmethod
    def build(range_groups, padding=0):

        # TODO: protect against bad groups
        iteration_set = IterationSet(padding=padding)

        for range_group in range_groups:
            first = range_group[0]
            last = range_group[-1]

            if first is None or last is None:
                raise ValueError(
                    'When building an IterationSet, each frame group must '
                    'have a value first and last value. '
                    'Recieved: first: {}, last: {}'.format(first, last)
                )
                
            if not isinstance(first, int) or not isinstance(last, int):
                raise TypeError(
                    'When building an IterationSet, '
                    'each first and last item of a frame group '
                    'must be ints'
                )
                
            if not first <= last:
                raise ValueError(
                    'When building an IterationSet, '
                    'first int of a frame group must be '
                    'less than or equal to the last'
                )
            
            iteration_set._iteration_range_groups[first] = IterationRange(first, last)
            
        return iteration_set

    @staticmethod
    def from_string(input_string, token_string="{range_groups:[\d\-\,]+}"):

        parsed = Tokenizer.tokenize(input_string, [token_string])

        # Parse padding
        padding = int(parsed.get('padding', 0))
        
        # Handle when first and last are parsed tokens
        first = parsed.get('first')
        last = parsed.get('last')
        if first or last:
            if not first or not last:
                raise IterationSetParseError(
                    'First and last tokens must be used together. '
                    'Parsed tokens: {}'.format(parsed.keys())
                )
            
            if not padding:
                if len(first) != len(last):
                    raise IterationPaddingMisMatch(
                        'Parsed first frame padding != parsed last frame padding. '
                        'Recieved: first_frame: {}, padding: {}'
                        'last_frame: {} padding: {}'.format(
                            first, len(first), last, len(last)
                        )
                    )
                padding = len(first)
            
            first = int(first)
            last = int(last)
            if not first <= last:
                raise IterationSetParseError(
                    'First must be less than last. '
                    'Recieved: first: {}, last: {}'.format(first, last)
                )
            
        # If first/last isn't included
        else:
            first = 0
            last = 0
        
        # Handle range groups
        range_groups_repr = parsed.get('range_groups')

        range_groups = []
        if range_groups_repr:
            # expect a string like: 1004-1007,1009,1011-1020
            groups = range_groups_repr.split(",")
            for group in groups:
                range_groups.append(tuple(int(x) for x in group.split('-')))
        else:
            range_groups.append((first, last))
        
        # If there isn't a first, last or range group token, then this will be empty
        # We need range groups to build a useable IterationSet
        if not range_groups:
            raise IterationSetParseError(
                'Unable to parse iteration set information such as: '
                'first, last, or even range groups'
                )

        return IterationSet.build(range_groups, padding=padding)

    @property
    def first(self):
        iteration_range_start_points = self.iteration_range_group_keys()

        if not iteration_range_start_points:
            return 0

        return iteration_range_start_points[0]

    @property
    def last(self):
        iteration_range_start_points = self.iteration_range_group_keys()

        if not iteration_range_start_points:
            return 0

        return self.get_iteration_range_group(iteration_range_start_points[-1]).last

    @staticmethod
    def merge(iteration_set_1, iteration_set_2):

        if iteration_set_1.padding != iteration_set_2.padding:
            raise MergeError('IterationSet1 (padding: {padding1}) and IterationSet2 (padding: {padding2}) do not match'.format(
                padding1=iteration_set_1.padding,
                padding2=iteration_set_2.padding
            ))

        resulting_iteration_set = IterationSet(padding=iteration_set_1.padding)
        resulting_iteration_set.add(*iteration_set_1)
        resulting_iteration_set.add(*iteration_set_2)

        return resulting_iteration_set

    def token_data(self):
        return dict(
            first=str(self.first).zfill(self.padding),
            last=str(self.last).zfill(self.padding),
            unpadded_first=self.first,
            unpadded_last=self.last,
            padding=self.padding,
            range_groups=self.str_ranges(),
        )

    def is_single(self):

        iteration_ranges = list(self.iteration_ranges())
        if len(iteration_ranges) > 1 or len(iteration_ranges) <= 0:
            return False

        iteration_range = iteration_ranges[0]
        return iteration_range.first == iteration_range.last

    def is_empty(self):
        return self.is_single() and self.first == 0 and self.last == 0

    def format(self, iteration_format):

        if not iteration_format or self.is_single():
            return str(self)
        
        try:
            return Tokenizer.format(iteration_format, self.token_data())
        except ValueError as e:
            raise StringReprFormatError(e)

    def sanitize_item(self, item):
        """
        IterationSets can accept ints or strings representing ints.
         This method is used to ensure that.
        """

        # Supporting only adding string digits to iteration sets for now
        if not isinstance(item, (str, int)):
            raise TypeError('Expecting padded digits or ints -- recieved: {}'.format(
                type(item))
            )

        # Set up padding if not set up (new iteration set init)
        if isinstance(item, str) and not item.isdigit():
            raise ValueError(
                'The item is a string but, not a digit -- received: {} -- {}'.format(
                    item, type(item))
                )

        if isinstance(item, str) and self.padding and self.padding != len(item):
            raise IterationPaddingMisMatch(
                'Iteration "{iteration}" and this IterationSet have a padding mis-match -- '
                'IterationSet = {iteration_set_padding}, Iteration = {iteration_padding}'.format(
                    iteration=item, 
                    iteration_set_padding=self.padding,
                    iteration_padding=len(item)
                ))

        return int(item)

    def add(self, *iterations):

        for iteration in iterations:

            # Post validation adding a iteration
            iteration_int = self.sanitize_item(iteration)

            # Set up padding if not set up (new iteration set init)
            if isinstance(iteration, str) and not self.padding:
                self.padding = len(iteration)

            if not self.get_iteration_range_group(iteration_int):
                self._iteration_range_groups[iteration_int] = IterationRange(
                    first=iteration_int,
                    last=iteration_int
                )

            # Consolidate IterationRange groups
            previous_index = None
            for current_index in self.iteration_range_group_keys():
                
                move_previous_pointer = True
                if isinstance(previous_index, int):

                    previous_group = self.get_iteration_range_group(previous_index)
                    current_group = self.get_iteration_range_group(current_index)

                    if previous_group and current_group:
                        # If the current group's first iteration is in the range of the previous iteration range, consolodate them
                        if previous_group.last + 1 >= current_group.first and current_group.first >= previous_group.first:

                            # Whichever group has the largest last iteration will become the last iteration of the consolodated group
                            consolodated_last = previous_group.last if previous_group.last > current_group.last else current_group.last

                            previous_group.last = consolodated_last

                            del self._iteration_range_groups[current_index]
                            move_previous_pointer = False

                if move_previous_pointer:
                    previous_index = current_index

    def iteration_range_group_keys(self):
        # Sorting by keys to ensure the correct iteration group ordering (all keys should be ints)
        return sorted(self._iteration_range_groups.keys())

    def iteration_ranges(self):
        for start_iteration in self.iteration_range_group_keys():
            yield self._iteration_range_groups.get(start_iteration)

    def get_iteration_range_group(self, index):
        return self._iteration_range_groups.get(index)

    def has(self, item):
        """
        Iterate over the range groups and see if the item exists in any of them
        """

        try:
            item = self.sanitize_item(item)
        except (ValueError, TypeError, IterationPaddingMisMatch):
            return False

        for range_group in self.iteration_ranges():
            if item >= range_group.first and item <= range_group.last:
                return True
        return False
