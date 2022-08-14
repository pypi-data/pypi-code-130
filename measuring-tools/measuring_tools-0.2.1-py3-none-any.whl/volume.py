'''Functionality for volume conversion and volume equality checks.
Values of two different temperatures recorded in different measurements are considered equal
if the converted values within a relative tolerance or absolute tolerance of float_point_tol.
The default for float_point_tol is 1e-05.
'''

from math import isclose
from measuring_tools import Measurement

def __dir__():
    return ('Volume', '__builtins__', '__cached__', '__doc__', '__file__', '__loader__', '__name__', '__package__', '__spec__')

class Volume(Measurement):
    '''Volume class comparing and converting Metric, British Imperial Units, and US Units'''

    def __init__(self, value: int | float, measurement: str='liters'):
        if not measurement in ('liters', 'gallons', 'gallons_us'):
            raise ValueError('Value must be liters, gallons, gallons_us')
        super().__init__(value, measurement)

    def __round__(self, ndigits):
        return Volume(round(self.value, ndigits=ndigits), self.measurement)

    def __abs__(self):
        return Volume(abs(self.value), self.measurement)

    def __eq__(self, other):
        match self.measurement:
            case 'liters':
                return isclose(self.value, other.to_liters().value, rel_tol=self.float_point_tol, abs_tol=self.float_point_tol)
            case 'gallons':
                return isclose(self.value, other.to_gallons().value, rel_tol=self.float_point_tol, abs_tol=self.float_point_tol)
            case 'gallons_us':
                return isclose(self.value, other.to_gallons_us().value, rel_tol=self.float_point_tol, abs_tol=self.float_point_tol)

    def __ne__(self, other):
        match self.measurement:
            case 'liters':
                return not isclose(self.value, other.to_liters().value, rel_tol=self.float_point_tol, abs_tol=self.float_point_tol)
            case 'gallons':
                return not isclose(self.value, other.to_gallons().value, rel_tol=self.float_point_tol, abs_tol=self.float_point_tol)
            case 'gallons_us':
                return not isclose(self.value, other.to_gallons_us().value, rel_tol=self.float_point_tol, abs_tol=self.float_point_tol)

    def __lt__(self, other):
        if self == other:
            return False
        match self.measurement:
            case 'liters':
                return self.value < other.to_liters().value
            case 'gallons':
                return self.value < other.to_gallons().value
            case 'gallons_us':
                return self.value < other.to_gallons_us().value

    def __le__(self, other):
        return self == other or self < other

    def __gt__(self, other):
        if self == other: return False
        match self.measurement:
            case 'liters':
                return self.value > other.to_liters().value
            case 'gallons':
                return self.value > other.to_gallons().value
            case 'gallons_us':
                return self.value > other.to_gallons_us().value

    def __ge__(self, other):
        return self == other or self > other

    def __add__(self, other):
        match self.measurement:
            case 'liters':
                total = self.value + other.to_liters().value
            case 'gallons':
                total = self.value + other.to_gallons().value
            case 'gallons_us':
                total = self.value + other.to_gallons_us().value
        return Volume(total, self.measurement)

    def __sub__(self, other):
        match self.measurement:
            case 'liters':
                diff = self.value - other.to_liters().value
            case 'gallons':
                diff = self.value - other.to_gallons().value
            case 'gallons_us':
                diff = self.value - other.to_gallons_us().value
        return Volume(diff, self.measurement)

    def __mul__(self, other):
        match self.measurement:
            case 'liters':
                product = self.value * other.to_liters().value
            case 'gallons':
                product = self.value * other.to_gallons().value
            case 'gallons_us':
                product = self.value * other.to_gallons_us().value
        return Volume(product, self.measurement)

    def __truediv__(self, other):
        match self.measurement:
            case 'liters':
                result = self.value / other.to_liters().value
            case 'gallons':
                result = self.value / other.to_gallons().value
            case 'gallons_us':
                result = self.value / other.to_gallons_us().value
        return Volume(result, self.measurement)

    def __floordiv__(self, other):
        match self.measurement:
            case 'liters':
                result = self.value // other.to_liters().value
            case 'gallons':
                result = self.value // other.to_gallons().value
            case 'gallons_us':
                result = self.value // other.to_gallons_us().value
        return Volume(result, self.measurement)

    def to_liters(self):
        '''Convert the volume to liters'''
        measure = 'liters'
        match self.measurement:
            case 'liters':
                return self
            case 'gallons':
                return Volume((self.value * 4.54609513), measurement=measure)
            case 'gallons_us':
                return Volume((self.value * 3.78541178), measurement=measure)

    def to_gallons(self):
        '''Convert the volume to British Imperial Gallons'''
        measure = 'gallons'
        match self.measurement:
            case 'gallons':
                return self
            case 'liters':
                return Volume((self.value * 0.219969157), measurement=measure)
            case 'gallons_us':
                return Volume((self.value * 0.8326741846), measurement=measure)

    def to_gallons_us(self):
        '''Convert the volume to US Gallons'''
        measure = 'gallons_us'
        match self.measurement:
            case 'gallons_us':
                return self
            case 'liters':
                return Volume((self.value * 0.264172052), measurement=measure)
            case 'gallons':
                return Volume((self.value * 1.200949925), measurement=measure)
