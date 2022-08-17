import pytest

from pytest_extensions.comparators.types import an_int, a_str, a_bool, a_float


def test_dict_equality():
    data = {
        "a": 1,
        "b": ...,
    }

    assert data == {
        "a": an_int,
        "b": Ellipsis,
    }


def test_list_equality():
    data = [
        "a",
        True,
        1,
        1.0,
    ]

    assert data == [
        a_str,
        a_bool,
        an_int,
        a_float,
    ]


def test_tuple_equality():
    data = (
        "a",
        True,
        1,
        1.0,
    )

    assert data == (
        a_str,
        a_bool,
        an_int,
        a_float,
    )


@pytest.mark.xfail(reason="TypeError: unhashable type: 'TypeComparator'")
def test_set_equality():
    data = {
        "a",
        True,
        1,
        1.0,
    }

    assert data == {
        a_str,
        a_bool,
        an_int,
        a_float,
    }
