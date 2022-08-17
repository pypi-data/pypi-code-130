import pytest

from pytest_extensions.comparators import FuncComparator


def test_FuncComparator_repr():
    def nope(*args, **kwargs):
        return False

    func = FuncComparator(nope)
    with pytest.raises(AssertionError) as e:
        assert func("yolo", "badum", test=1, test2="A") is True

    assert "An object that nope('yolo', 'badum', test=1, test2='A')" in str(e)

