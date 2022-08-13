# Copyright 2012-2020 The Meson development team
# Copyright © 2020 Intel Corporation

# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at

#     http://www.apache.org/licenses/LICENSE-2.0

# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

from functools import lru_cache
import collections
import enum
import os
import re
import typing as T

from . import mesonlib

if T.TYPE_CHECKING:
    from .linkers import StaticLinker
    from .compilers import Compiler

UNIXY_COMPILER_INTERNAL_LIBS = ['m', 'c', 'pthread', 'dl', 'rt']  # type: T.List[str]
# execinfo is a compiler lib on FreeBSD and NetBSD
if mesonlib.is_freebsd() or mesonlib.is_netbsd():
    UNIXY_COMPILER_INTERNAL_LIBS.append('execinfo')


class Dedup(enum.Enum):

    """What kind of deduplication can be done to compiler args.

    OVERRIDDEN - Whether an argument can be 'overridden' by a later argument.
        For example, -DFOO defines FOO and -UFOO undefines FOO. In this case,
        we can safely remove the previous occurrence and add a new one. The
        same is true for include paths and library paths with -I and -L.
    UNIQUE - Arguments that once specified cannot be undone, such as `-c` or
        `-pipe`. New instances of these can be completely skipped.
    NO_DEDUP - Whether it matters where or how many times on the command-line
        a particular argument is present. This can matter for symbol
        resolution in static or shared libraries, so we cannot de-dup or
        reorder them.
    """

    NO_DEDUP = 0
    UNIQUE = 1
    OVERRIDDEN = 2


class CompilerArgs(collections.abc.MutableSequence):
    '''
    List-like class that manages a list of compiler arguments. Should be used
    while constructing compiler arguments from various sources. Can be
    operated with ordinary lists, so this does not need to be used
    everywhere.

    All arguments must be inserted and stored in GCC-style (-lfoo, -Idir, etc)
    and can converted to the native type of each compiler by using the
    .to_native() method to which you must pass an instance of the compiler or
    the compiler class.

    New arguments added to this class (either with .append(), .extend(), or +=)
    are added in a way that ensures that they override previous arguments.
    For example:

    >>> a = ['-Lfoo', '-lbar']
    >>> a += ['-Lpho', '-lbaz']
    >>> print(a)
    ['-Lpho', '-Lfoo', '-lbar', '-lbaz']

    Arguments will also be de-duped if they can be de-duped safely.

    Note that because of all this, this class is not commutative and does not
    preserve the order of arguments if it is safe to not. For example:
    >>> ['-Ifoo', '-Ibar'] + ['-Ifez', '-Ibaz', '-Werror']
    ['-Ifez', '-Ibaz', '-Ifoo', '-Ibar', '-Werror']
    >>> ['-Ifez', '-Ibaz', '-Werror'] + ['-Ifoo', '-Ibar']
    ['-Ifoo', '-Ibar', '-Ifez', '-Ibaz', '-Werror']

    '''
    # Arg prefixes that override by prepending instead of appending
    prepend_prefixes = ()  # type: T.Tuple[str, ...]

    # Arg prefixes and args that must be de-duped by returning 2
    dedup2_prefixes = ()   # type: T.Tuple[str, ...]
    dedup2_suffixes = ()   # type: T.Tuple[str, ...]
    dedup2_args = ()       # type: T.Tuple[str, ...]

    # Arg prefixes and args that must be de-duped by returning 1
    #
    # NOTE: not thorough. A list of potential corner cases can be found in
    # https://github.com/mesonbuild/meson/pull/4593#pullrequestreview-182016038
    dedup1_prefixes = ()  # type: T.Tuple[str, ...]
    dedup1_suffixes = ('.lib', '.dll', '.so', '.dylib', '.a')  # type: T.Tuple[str, ...]
    # Match a .so of the form path/to/libfoo.so.0.1.0
    # Only UNIX shared libraries require this. Others have a fixed extension.
    dedup1_regex = re.compile(r'([\/\\]|\A)lib.*\.so(\.[0-9]+)?(\.[0-9]+)?(\.[0-9]+)?$')
    dedup1_args = ()  # type: T.Tuple[str, ...]
    # In generate_link() we add external libs without de-dup, but we must
    # *always* de-dup these because they're special arguments to the linker
    # TODO: these should probably move too
    always_dedup_args = tuple('-l' + lib for lib in UNIXY_COMPILER_INTERNAL_LIBS)  # type : T.Tuple[str, ...]

    def __init__(self, compiler: T.Union['Compiler', 'StaticLinker'],
                 iterable: T.Optional[T.Iterable[str]] = None):
        self.compiler = compiler
        self._container = list(iterable) if iterable is not None else []  # type: T.List[str]
        self.pre = collections.deque()    # type: T.Deque[str]
        self.post = collections.deque()   # type: T.Deque[str]

    # Flush the saved pre and post list into the _container list
    #
    # This correctly deduplicates the entries after _can_dedup definition
    # Note: This function is designed to work without delete operations, as deletions are worsening the performance a lot.
    def flush_pre_post(self) -> None:
        new = list()                      # type: T.List[str]
        pre_flush_set = set()             # type: T.Set[str]
        post_flush = collections.deque()  # type: T.Deque[str]
        post_flush_set = set()            # type: T.Set[str]

        #The two lists are here walked from the front to the back, in order to not need removals for deduplication
        for a in self.pre:
            dedup = self._can_dedup(a)
            if a not in pre_flush_set:
                new.append(a)
                if dedup is Dedup.OVERRIDDEN:
                    pre_flush_set.add(a)
        for a in reversed(self.post):
            dedup = self._can_dedup(a)
            if a not in post_flush_set:
                post_flush.appendleft(a)
                if dedup is Dedup.OVERRIDDEN:
                    post_flush_set.add(a)

        #pre and post will overwrite every element that is in the container
        #only copy over args that are in _container but not in the post flush or pre flush set
        if pre_flush_set or post_flush_set:
            for a in self._container:
                if a not in post_flush_set and a not in pre_flush_set:
                    new.append(a)
        else:
            new.extend(self._container)
        new.extend(post_flush)

        self._container = new
        self.pre.clear()
        self.post.clear()

    def __iter__(self) -> T.Iterator[str]:
        self.flush_pre_post()
        return iter(self._container)

    @T.overload                                # noqa: F811
    def __getitem__(self, index: int) -> str:  # noqa: F811
        pass

    @T.overload                                                     # noqa: F811
    def __getitem__(self, index: slice) -> T.MutableSequence[str]:  # noqa: F811
        pass

    def __getitem__(self, index: T.Union[int, slice]) -> T.Union[str, T.MutableSequence[str]]:  # noqa: F811
        self.flush_pre_post()
        return self._container[index]

    @T.overload                                             # noqa: F811
    def __setitem__(self, index: int, value: str) -> None:  # noqa: F811
        pass

    @T.overload                                                       # noqa: F811
    def __setitem__(self, index: slice, value: T.Iterable[str]) -> None:  # noqa: F811
        pass

    def __setitem__(self, index: T.Union[int, slice], value: T.Union[str, T.Iterable[str]]) -> None:  # noqa: F811
        self.flush_pre_post()
        self._container[index] = value  # type: ignore  # TODO: fix 'Invalid index type' and 'Incompatible types in assignment' errors

    def __delitem__(self, index: T.Union[int, slice]) -> None:
        self.flush_pre_post()
        del self._container[index]

    def __len__(self) -> int:
        return len(self._container) + len(self.pre) + len(self.post)

    def insert(self, index: int, value: str) -> None:
        self.flush_pre_post()
        self._container.insert(index, value)

    def copy(self) -> 'CompilerArgs':
        self.flush_pre_post()
        return type(self)(self.compiler, self._container.copy())

    @classmethod
    @lru_cache(maxsize=None)
    def _can_dedup(cls, arg: str) -> Dedup:
        """Returns whether the argument can be safely de-duped.

        In addition to these, we handle library arguments specially.
        With GNU ld, we surround library arguments with -Wl,--start/end-gr -> Dedupoup
        to recursively search for symbols in the libraries. This is not needed
        with other linkers.
        """

        # A standalone argument must never be deduplicated because it is
        # defined by what comes _after_ it. Thus dedupping this:
        # -D FOO -D BAR
        # would yield either
        # -D FOO BAR
        # or
        # FOO -D BAR
        # both of which are invalid.
        if arg in cls.dedup2_prefixes:
            return Dedup.NO_DEDUP
        if arg in cls.dedup2_args or \
           arg.startswith(cls.dedup2_prefixes) or \
           arg.endswith(cls.dedup2_suffixes):
            return Dedup.OVERRIDDEN
        if arg in cls.dedup1_args or \
           arg.startswith(cls.dedup1_prefixes) or \
           arg.endswith(cls.dedup1_suffixes) or \
           re.search(cls.dedup1_regex, arg):
            return Dedup.UNIQUE
        return Dedup.NO_DEDUP

    @classmethod
    @lru_cache(maxsize=None)
    def _should_prepend(cls, arg: str) -> bool:
        return arg.startswith(cls.prepend_prefixes)

    def to_native(self, copy: bool = False) -> T.List[str]:
        # Check if we need to add --start/end-group for circular dependencies
        # between static libraries, and for recursively searching for symbols
        # needed by static libraries that are provided by object files or
        # shared libraries.
        self.flush_pre_post()
        if copy:
            new = self.copy()
        else:
            new = self
        return self.compiler.unix_args_to_native(new._container)

    def append_direct(self, arg: str) -> None:
        '''
        Append the specified argument without any reordering or de-dup except
        for absolute paths to libraries, etc, which can always be de-duped
        safely.
        '''
        self.flush_pre_post()
        if os.path.isabs(arg):
            self.append(arg)
        else:
            self._container.append(arg)

    def extend_direct(self, iterable: T.Iterable[str]) -> None:
        '''
        Extend using the elements in the specified iterable without any
        reordering or de-dup except for absolute paths where the order of
        include search directories is not relevant
        '''
        self.flush_pre_post()
        for elem in iterable:
            self.append_direct(elem)

    def extend_preserving_lflags(self, iterable: T.Iterable[str]) -> None:
        normal_flags = []
        lflags = []
        for i in iterable:
            if i not in self.always_dedup_args and (i.startswith('-l') or i.startswith('-L')):
                lflags.append(i)
            else:
                normal_flags.append(i)
        self.extend(normal_flags)
        self.extend_direct(lflags)

    def __add__(self, args: T.Iterable[str]) -> 'CompilerArgs':
        self.flush_pre_post()
        new = self.copy()
        new += args
        return new

    def __iadd__(self, args: T.Iterable[str]) -> 'CompilerArgs':
        '''
        Add two CompilerArgs while taking into account overriding of arguments
        and while preserving the order of arguments as much as possible
        '''
        tmp_pre = collections.deque()  # type: T.Deque[str]
        if not isinstance(args, collections.abc.Iterable):
            raise TypeError(f'can only concatenate Iterable[str] (not "{args}") to CompilerArgs')
        for arg in args:
            # If the argument can be de-duped, do it either by removing the
            # previous occurrence of it and adding a new one, or not adding the
            # new occurrence.
            dedup = self._can_dedup(arg)
            if dedup is Dedup.UNIQUE:
                # Argument already exists and adding a new instance is useless
                if arg in self._container or arg in self.pre or arg in self.post:
                    continue
            if self._should_prepend(arg):
                tmp_pre.appendleft(arg)
            else:
                self.post.append(arg)
        self.pre.extendleft(tmp_pre)
        #pre and post is going to be merged later before a iter call
        return self

    def __radd__(self, args: T.Iterable[str]) -> 'CompilerArgs':
        self.flush_pre_post()
        new = type(self)(self.compiler, args)
        new += self
        return new

    def __eq__(self, other: object) -> T.Union[bool]:
        self.flush_pre_post()
        # Only allow equality checks against other CompilerArgs and lists instances
        if isinstance(other, CompilerArgs):
            return self.compiler == other.compiler and self._container == other._container
        elif isinstance(other, list):
            return self._container == other
        return NotImplemented

    def append(self, arg: str) -> None:
        self.__iadd__([arg])

    def extend(self, args: T.Iterable[str]) -> None:
        self.__iadd__(args)

    def __repr__(self) -> str:
        self.flush_pre_post()
        return f'CompilerArgs({self.compiler!r}, {self._container!r})'
