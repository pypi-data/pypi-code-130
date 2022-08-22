from math import sqrt
from ..exceptions import InvalidArgumentValueException


def isprime(integer):
    if (
        integer == 2 or
        integer == 3
    ):
        return True
    if (
        integer < 2 or
        integer % 2 == 0 or
        integer % 3 == 0
    ):
        return False

    sqrtval = int(sqrt(integer))
    for i in range(5, sqrtval + 1, 6):
        if (
            integer % i == 0 or
            integer % (i + 2) == 0
        ):
            return False
    return True


def factorization(integer):
    def _compact(base):
        nonlocal integer
        res = 0
        while integer % base == 0:
            res += 1
            integer //= base
        return res
    _prime_divs = {}
    _2 = _compact(2)
    if _2:
        _prime_divs[2] = _2
    _3 = _compact(3)
    if _3:
        _prime_divs[3] = _3

    sqrtval = int(sqrt(integer))
    for i in range(5, sqrtval + 1, 6):
        _i = _compact(i)
        if _i:
            _prime_divs[i] = _i

    if integer > 0:
        _prime_divs[integer] = 1
    return _prime_divs


def divisors(integer):
    _head = []
    _revtail = []

    sqrtval = int(sqrt(integer))
    for i in range(2, sqrtval + 1):
        if integer % i == 0:
            _head.append(i)
            _revtail.append(integer // i)

    if _head[-1] == _revtail[-1]:
        _revtail.pop()

    return _head + _revtail[::-1]


def Eratosthenes(start, end=None):
    if end is not None:
        if end - start > 1_000_000:
            raise InvalidArgumentValueException(
                '|end - start| > 1,000,000 (hiệu 2 đối số này không được vượt quá 1,000,000).')
        _res = {i: True for i in range(start, end + 1)}
        end_sqrt = int(sqrt(end))
        for i in range(2, end_sqrt + 1):
            j = max(i*i, (start + i - 1) / i*i)
            while j <= end:
                _res[j - start] = False
                j += i
        if 1 >= start:
            _res[1 - start] = False
        return _res
    end = start
    _res = {i: True for i in range(end + 1)}
    _res[0] = False
    _res[1] = False
    for i in range(4, end + 1, 2):
        _res[i] = False
    for i in range(9, end + 1, 3):
        _res[i] = False

    end_sqrt = int(sqrt(end))
    for base in range(5, end_sqrt + 1, 6):
        if _res[base]:
            for i in range(base * base, end + 1, base):
                _res[i] = False
        if _res[base + 2]:
            for i in range((base + 2) * (base + 2), end + 1, base + 2):
                _res[i] = False

    return _res
