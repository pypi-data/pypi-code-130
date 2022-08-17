from pytest_extensions.comparators.types import (
    an_int,
    a_callable,
    a_numeric,
    an_ellipsis,
    a_str,
    a_float,
    a_bool,
    an_iterable,
    a_complex,
    a_sequence,
    a_list,
    a_tuple,
    a_range,
    a_bytes,
    a_bytearray,
    a_set,
    a_frozenset,
    a_dict,
    a_type,
    an_object,
    anything,
)


class Klass:
    pass


def test_a_numeric():
    assert 1 == a_numeric
    assert 1.0 == a_numeric
    assert 1j == a_numeric

    assert "a" != a_numeric


def test_an_int():
    assert 1 == an_int

    # Corner case :santa: bool is a subclass of int
    assert False == an_int

    assert 1.0 != an_int
    assert "a" != an_int


def test_a_float():
    assert 1.0 == a_float

    assert 1 != a_float
    assert "a" != a_float


def test_a_complex():
    assert 1j == a_complex

    assert 1 != a_complex
    assert 1.0 != a_complex


def test_an_iterable():
    assert [] == an_iterable
    assert "abc" == an_iterable

    assert 1 != an_iterable


def test_a_sequence():
    assert [] == a_sequence
    assert "" == a_sequence
    assert (1,) == a_sequence

    assert 1 != an_iterable


def test_a_list():
    assert [] == a_list
    assert [1, 2, 3] == a_list

    assert (1,) != a_list


def test_a_tuple():
    assert tuple() == a_tuple
    assert (1,) == a_tuple

    assert [] != a_tuple


def test_a_range():
    assert range(1,10) == a_range

    assert [] != a_range


def test_a_str():
    assert "" == a_str
    assert "abc" == a_str

    assert 1 != a_str


def test_a_bytes():
    assert b"" == a_bytes
    assert b"abc" == a_bytes

    assert "" != a_bytes


def test_a_bytearray():
    assert bytearray([]) == a_bytearray
    assert bytearray([1, 2, 3]) == a_bytearray

    assert [] != a_bytearray


def test_a_set():
    assert set() == a_set
    assert {1, 2, 3} == a_set

    assert frozenset() != a_set


def test_a_frozenset():
    assert frozenset() == a_frozenset
    assert frozenset([1, 2, 3]) == a_frozenset


def test_a_dict():
    assert {} == a_dict
    assert {1: 2} == a_dict

    assert {1} != a_dict


def test_a_callable():
    assert test_a_callable == a_callable


def test_a_type():
    assert int == a_type
    assert Klass == a_type
    assert 1 != a_type


def test_ellipsis():
    assert ... == Ellipsis
    assert ... == an_ellipsis

    assert [..., ..., ...] == [an_ellipsis, an_ellipsis, an_ellipsis]
    assert [..., ..., ...] == [Ellipsis, Ellipsis, Ellipsis]


def test_an_object():
    # Everything is an object :pokerface:
    assert Klass() == an_object
    assert Klass == an_object
    assert 1 == an_object
    assert id == an_object


def test_anything():
    assert Klass() == anything
    assert Klass == anything
    assert 1 == anything
    assert id == anything


def test_a_bool():
    assert False == a_bool

    assert 1 != a_bool
