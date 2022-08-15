"""String enum module."""

# Copyright (c) 2020-2022 ObserverOfTime
#
# This software is provided 'as-is', without any express or implied
# warranty. In no event will the authors be held liable for any damages
# arising from the use of this software.
#
# Permission is granted to anyone to use this software for any purpose,
# including commercial applications, and to alter it and redistribute it
# freely, subject to the following restrictions:
#
# 1. The origin of this software must not be misrepresented; you must not
#   claim that you wrote the original software. If you use this software
#   in a product, an acknowledgment in the product documentation would be
#   appreciated but is not required.
# 2. Altered source versions must be plainly marked as such, and must not be
#   misrepresented as being the original software.
# 3. This notice may not be removed or altered from any source distribution.

from enum import Enum


class StrEnum(str, Enum):
    """
    Enum class that be used as a string.

    Examples:
        >>> class StrExample(StrEnum):
        ...     A = 'Alice'
        >>> StrExample.A.upper()
        'ALICE'

    .. autoattribute:: __class__
        :annotation:

        alias of :class:`enum.EnumMeta`

    .. automethod:: __str__() -> str
    """
    def __str__(self) -> str:
        """
        Return the instance as a string.

        Returns:
            :obj:`str`: The value of the instance.

        Examples:
            >>> str(StrExample.A)
            'Alice'
        """
        return self.value
