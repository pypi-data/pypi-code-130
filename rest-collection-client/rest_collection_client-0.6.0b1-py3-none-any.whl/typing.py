import sys
from typing import Dict, List, Mapping, Sequence, Union

__all__ = [
    'JsonContentOrText',
    'SequenceOfMapping',
    'RawRestCollectionResponse',
    'RestCollectionJoinHowType',
]

JsonContentOrText = Union[Dict, List, str, int, float, None]
SequenceOfMapping = Sequence[Mapping]
RawRestCollectionResponse = Mapping[str, SequenceOfMapping]

if sys.version_info >= (3, 8):
    from typing import Literal

    RestCollectionJoinHowType = Literal['left', 'right', 'outer', 'inner']

else:
    RestCollectionJoinHowType = str
