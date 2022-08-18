import pytest


def test_argument_check_exception():
    with pytest.raises(ZeroDivisionError):
        s = 1 / 0

