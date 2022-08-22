from random import (
    choices as randchoices,
    randint,
    triangular,
    randrange,
    uniform,
    choice as randchoice,
    shuffle as randshuffle,
    sample,
    random as randrd
)
from typing import Dict, Sequence
from ..exceptions import InvalidArgumentValueException, TypeException

_ONE = 1


class ItRandom:
    def __init__(self):
        pass

    def lucky(self, true_percent=0.5):
        return randchoices((True, False), cum_weights=(true_percent, 1))[0]

    def rdint(self, start, end=None, step=_ONE, /):
        if end is None:
            if step is not _ONE:
                raise TypeException(
                    "Missing a non-None 'end' argument (Thiếu đối số 'end').")
            return randrange(0, start + 1)
        if start > end:
            start, end = end, start
        return randrange(start, end + 1, step)

    def rdfloat(self, start=None, end=None, gather_at=None, /):
        if end is None:
            if start is None:
                if gather_at is not None:
                    raise TypeException(
                        "Missing a non-None 'start' and 'end' arguments (Thiếu 2 đối số 'start', 'end').")
                return randrd()
            if gather_at is not None:
                return triangular(0, start, gather_at)
            return uniform(0, start)
        if start > end:
            start, end = end, start
        if gather_at is not None:
            return triangular(start, end, gather_at)
        return uniform(start, end)

    def choices(self, population, length, probabilities=None):
        if probabilities:
            if isinstance(probabilities, Sequence):
                _probabilities = list(probabilities)
                if len(_probabilities) < len(population):
                    _probabilities.extend(
                        [1] * (len(population) - len(_probabilities)))
                return randchoices(population, weights=_probabilities, k=length)
            if isinstance(probabilities, Dict):
                _population = set(population)
                _population = tuple(_population)
                _probabilities = probabilities.copy()
                for ele in _population:
                    if _probabilities.get(ele):
                        continue
                    _probabilities[ele] = 1
                _probabilities = [_probabilities[ele] for ele in _population]
                return randchoices(population, weights=_probabilities, k=length)
            raise TypeException(
                "'probabilities' must be a tuple/list/dict ('probabilities' phải là tuple/list/dict).")
        return randchoices(population, k=length)

    def choice(self, population, probabilities=None):
        if probabilities:
            return self.choices(population, 1, probabilities)[0]
        return randchoice(population)

    def shuffle(self, sequence):
        randshuffle(sequence)

    def once(self, population, length, probabilities=None):
        if probabilities:
            if isinstance(probabilities, Sequence):
                _population = tuple(_population)
                _probabilities = list(probabilities)
                if len(_probabilities) < len(population):
                    _probabilities.extend(
                        [1] * (len(population) - len(_probabilities)))
            if isinstance(probabilities, Dict):
                _population = set(population)
                _population = tuple(_population)
                _probabilities = probabilities.copy()
                for ele in _population:
                    if _probabilities.get(ele):
                        continue
                    _probabilities[ele] = 1
                _probabilities = [_probabilities[ele] for ele in _population]
                return randchoices(population, weights=_probabilities, k=length)
            raise TypeException(
                "'probabilities' must be a tuple/list/dict ('probabilities' phải là tuple/list/dict).")

        if length > len(_population):
            raise InvalidArgumentValueException(
                "Can't return a list 'length' sized, the maximum length that can be achieved is %d ('length' không được lớn hơn %d)" % (len(_population), len(_population)))
        if probabilities:
            res = []
            idx = tuple(range(len(_population)))
            while len(res) < length:
                i = self.choice(idx, _probabilities)
                _probabilities[i] = 0
                res.append(_population[i])
            return res
        return sample(_population, length)

    def withsum(self, sumvalue, length, *, lowerbound=0, upperbound=None):
        if upperbound is not None:
            if lowerbound >= upperbound:
                raise InvalidArgumentValueException(
                    "'upperbound' cannot be less than or equal to 'lowerbound'('lowerbound' phải nhỏ hơn hoặc bằng 'upperbound').")
            if upperbound * length < sumvalue:
                raise InvalidArgumentValueException(
                    "Can't create a list with sum is 'sumvalue' because 'upperbound' is too small ('upperbound' quá nhỏ để tạo list có tổng bằng 'sumvalue').")
        if lowerbound >= 0:
            if lowerbound * length > sumvalue:
                raise InvalidArgumentValueException(
                    "Can't create a list with sum is 'sumvalue' because 'lowerbound' is too big ('lowerbound' quá lớn để tạo list có tổng bằng 'sumvalue').")
            _res = [lowerbound] * length
            sumvalue -= lowerbound * length
            _ready = list(range(length))
            while sumvalue > 0:
                i = randchoice(_ready)
                if _res[i] == upperbound:
                    _ready.remove(i)
                    continue
                _res[i] += 1
                sumvalue -= 1
        else:
            if upperbound is not None:
                max_of_lowele = (upperbound * length -
                                 sumvalue) / (upperbound - lowerbound)
            else:
                max_of_lowele = length - 1

            lowsize = randint(0, int(max_of_lowele))
            minlow = lowerbound * lowsize
            if upperbound is not None:
                maxhigh = upperbound * (length - lowsize)
                highsum = randint(sumvalue, min(maxhigh, sumvalue - minlow))
            else:
                highsum = randint(sumvalue, sumvalue - minlow)
            lowsum = sumvalue - highsum

            _low = [-1] * lowsize
            lowsum += lowsize
            _ready = list(range(lowsize))
            while lowsum < 0:
                i = randchoice(_ready)
                if _low[i] == lowerbound:
                    _ready.remove(i)
                    continue
                _low[i] -= 1
                lowsum += 1
            _high = [0] * (length - lowsize)
            _ready = list(range(length - lowsize))
            while highsum > 0:
                i = randchoice(_ready)
                if _high[i] == upperbound:
                    _ready.remove(i)
                    continue
                _high[i] += 1
                highsum -= 1
            _res = _low + _high
            shuffle(_res)
        return _res


_inst = ItRandom()
def lucky(*arg, **kwargs): return _inst.lucky(*arg, **kwargs)
def rdint(*arg, **kwargs): return _inst.rdint(*arg, **kwargs)
def rdfloat(*arg, **kwargs): return _inst.rdfloat(*arg, **kwargs)
def choices(*arg, **kwargs): return _inst.choices(*arg, **kwargs)
def choice(*arg, **kwargs): return _inst.choice(*arg, **kwargs)
def shuffle(*arg, **kwargs): return _inst.shuffle(*arg, **kwargs)
def once(*arg, **kwargs): return _inst.once(*arg, **kwargs)


def withsum(*arg, **kwargs):
    try:
        return _inst.withsum(*arg, **kwargs)
    except TypeError as e:
        if 'positional arguments but' in str(e):
            raise TypeException(
                "'lowerbound' and 'upperbound' must be keyword arguments ('lowerbound', 'upperbound' phải được truyền dưới dạng từ khóa).")
        raise e
