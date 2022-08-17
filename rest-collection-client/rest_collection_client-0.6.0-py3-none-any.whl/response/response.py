from functools import partial
from itertools import chain
from operator import itemgetter
from typing import Any, Callable, Dict, Hashable, Iterator, Sequence, Tuple, \
    cast

from collections_extension import Map
from pandas import DataFrame, concat

from rest_collection_client.typing import RawRestCollectionResponse
from .deserialize import RestCollectionDeserializeMap
from .rename import RestCollectionRenameFactory

__all__ = [
    'RestCollectionResponse',
]


def _replace_values_with_dataframes(
    data: RawRestCollectionResponse,
    **dataframe_params: Any,
) -> Dict[str, DataFrame]:
    return {
        key: DataFrame(list(value), **dataframe_params)
        for key, value in data.items()
        if value
    }


def _concat_chunked_response(
    chunked_response: Tuple[Dict[str, DataFrame], ...],
) -> Iterator[Tuple[str, DataFrame]]:

    # Calculate all keys, that in all chunks exist.
    response_keys = frozenset(chain.from_iterable(chunked_response))

    # We concatenate DataFrames for each key vertically and drop
    # duplicates, if they appear after concatenation.
    for key in response_keys:
        try:
            concatenated = concat(
                # We collect for each key all DataFrames from all chunks,
                # were this key exists.
                tuple(
                    map(
                        itemgetter(key),
                        # pylint: disable=cell-var-from-loop
                        filter(
                            lambda chunk: key in chunk,
                            chunked_response,
                        ),
                    ),
                ),
                ignore_index=True,
                copy=False,
            )
        except ValueError:
            # No objects to concatenate
            continue

        concatenated.drop_duplicates(inplace=True)
        concatenated.reset_index(drop=True, inplace=True)

        yield key, concatenated


class RestCollectionResponse(Map[str, DataFrame]):
    """Response container."""
    __slots__ = ()

    def rename(
        self,
        rename_factory: RestCollectionRenameFactory,
    ) -> 'RestCollectionResponse':
        return self.__class__(
            {
                key: value.rename(
                    cast(Callable[[Hashable], Hashable], rename_factory[key]),
                    axis='columns',
                )
                for key, value in self._data.items()
            },
        )

    @classmethod
    def from_raw_response(
        cls,
        data: RawRestCollectionResponse,
        **dataframe_params: Any,
    ) -> 'RestCollectionResponse':
        return cls(_replace_values_with_dataframes(data, **dataframe_params))

    @classmethod
    def deserialize(
        cls,
        data: RawRestCollectionResponse,
        deserialize_map: RestCollectionDeserializeMap,
        **dataframe_params: Any,
    ) -> 'RestCollectionResponse':
        return cls.from_raw_response(
            deserialize_map.deserialize_response(data),
            **dataframe_params,
        )

    @classmethod
    def deserialize_chunked(
        cls,
        data: Sequence[RawRestCollectionResponse],
        deserialize_map: RestCollectionDeserializeMap,
        **dataframe_params: Any,
    ) -> 'RestCollectionResponse':
        # Deserialize chunks and replace theirs values with DataFrames.
        chunked_response = tuple(
            map(
                partial(_replace_values_with_dataframes, **dataframe_params),
                deserialize_map.deserialize_chunked_response(data),
            ),
        )

        return cls(
            dict(
                _concat_chunked_response(chunked_response),
            ),
        )
