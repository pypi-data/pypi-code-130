import typing

from mutwo import common_generators


__all__ = ("euclidean_interlocking",)


def euclidean_interlocking(
    *sequence_to_interlock: typing.Sequence[typing.Any],
) -> tuple[typing.Any, ...]:
    """Interlock sequences

    :param sequence_to_interlock: Any sequence with n elements.
    :return: A tuple where all given sequences have been mixed in
        by making an as balanced order as possible.

    **Example:**

    >>> from mutwo import zimmermann_generators
    >>> zimmermann_generators.euclidean_interlocking([0, 0, 0], [1, 1])
    (0, 1, 0, 0, 1)
    """

    # Avoid corner case error
    if not sequence_to_interlock:
        return tuple([])

    sequence_count_list = [len(sequence) for sequence in sequence_to_interlock]
    index_list = [0 for _ in range(sequence_count_list[0])]

    for index, sequence_count in enumerate(sequence_count_list[1:]):
        current_length = len(index_list)
        index_list_iterator = iter(index_list)
        current_index = index + 1
        index_list = [
            next(index_list_iterator) if distribution else current_index
            for distribution in common_generators.euclidean(
                current_length, current_length + sequence_count
            )
        ]

    iterator_list = [iter(sequence) for sequence in sequence_to_interlock]
    return tuple(next(iterator_list[index]) for index in index_list)
