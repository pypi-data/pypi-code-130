import pytest

from pytest_extensions.comparators.strings import startswith, endswith, contains


def test_startswith():
    assert "abc" == startswith("a")
    assert "abc" != startswith("c")

    with pytest.raises(AssertionError) as e:
        assert "a" == startswith("b")

    assert "An object that startswith('b')" in str(e)


def test_endswith():
    assert "abc" == endswith("c")
    assert "abc" != endswith("a")


def test_contains():
    assert repr(contains('a')) == "'a' in None"

    assert "ab" == contains("b")
    assert "abc" != contains("d")

    with pytest.raises(AssertionError) as e:
        assert "abce" == contains("d")
    assert "'d' in 'abce'" in str(e)
