'''Functionality for length conversion and length equality checks.
Values of two different temperatures recorded in different measurements are considered equal
if the converted values within a relative tolerance or absolute tolerance of float_point_tol.
The default for float_point_tol is 1e-05.
'''

from math import isclose
from measuring_tools import Measurement

def __dir__():
    return ('Length', 'MARATHON', '__builtins__', '__cached__', '__doc__', '__file__', '__loader__', '__name__', '__package__', '__spec__')

class Length(Measurement):
    '''Length Converter for Metric and English Imperial Units'''

    def __init__(self, value: int | float, measurement: str='meters'):
        if not measurement in ('meters', 'kilometers', 'yards', 'miles'):
            raise ValueError('Value must be meters, miklometers, yards, or miles')
        super().__init__(value, measurement)

    def __round__(self, ndigits):
        return Length(round(self.value, ndigits=ndigits), self.measurement)

    def __abs__(self):
        return Length(abs(self.value), self.measurement)

    def __eq__(self, other):
        match self.measurement:
            case 'meters':
                return isclose(self.value, other.to_meters().value, rel_tol=self.float_point_tol, abs_tol=self.float_point_tol)
            case 'yards':
                return isclose(self.value, other.to_yards().value, rel_tol=self.float_point_tol, abs_tol=self.float_point_tol)
            case 'miles':
                return isclose(self.value, other.to_miles().value, rel_tol=self.float_point_tol, abs_tol=self.float_point_tol)
            case 'kilometers':
                return isclose(self.value, other.to_kilometers().value, rel_tol=self.float_point_tol, abs_tol=self.float_point_tol)
        
    def __ne__(self, other):
        match self.measurement:
            case 'meters':
                return not isclose(self.value, other.to_meters().value, rel_tol=self.float_point_tol, abs_tol=self.float_point_tol)
            case 'yards':
                return not isclose(self.value, other.to_yards().value, rel_tol=self.float_point_tol, abs_tol=self.float_point_tol)
            case 'miles':
                return not isclose(self.value, other.to_miles().value, rel_tol=self.float_point_tol, abs_tol=self.float_point_tol)
            case 'kilometers':
                return not isclose(self.value, other.to_kilometers().value, rel_tol=self.float_point_tol, abs_tol=self.float_point_tol)

    def __lt__(self, other):
        if self == other:
            return False
        match self.measurement:
            case 'meters':
                return self.value < other.to_meters().value
            case 'yards':
                return self.value < other.to_yards().value
            case 'miles':
                return self.value < other.to_miles().value
            case 'kilometers':
                return self.value < other.to_kilometers().value

    def __le__(self, other):
        return self == other or self < other

    def __gt__(self, other):
        if self == other:
            return False
        match self.measurement:
            case 'meters':
                return self.value > other.to_meters().value
            case 'yards':
                return self.value > other.to_yards().value
            case 'miles':
                return self.value > other.to_miles().value
            case 'kilometers':
                return self.value > other.to_kilometers().value

    def __ge__(self, other):
        return self == other or self > other

    def __add__(self, other):
        match self.measurement:
            case 'meters':
                total = self.value + other.to_meters().value
            case 'yards':
                total = self.value + other.to_yards().value
            case 'miles':
                total = self.value + other.to_miles().value
            case 'kilomters':
                total = self.value + other.to_kilometers().value
        return Length(total, self.measurement)

    def __sub__(self, other):
        match self.measurement:
            case 'meters':
                diff = self.value - other.to_meters().value
            case 'yards':
                diff = self.value - other.to_yards().value
            case 'miles':
                diff = self.value - other.to_miles().value
            case 'kilomters':
                diff = self.value - other.to_kilometers().value
        return Length(diff, self.measurement)

    def __mul__(self, other):
        match self.measurement:
            case 'meters':
                product = self.value * other.to_meters().value
            case 'yards':
                product = self.value * other.to_yards().value
            case 'miles':
                product = self.value * other.to_miles().value
            case 'kilomters':
                product = self.value * other.to_kilometers().value
        return Length(product, self.measurement)

    def __truediv__(self, other):
        match self.measurement:
            case 'meters':
                result = self.value / other.to_meters().value
            case 'yards':
                result = self.value / other.to_yards().value
            case 'miles':
                result = self.value / other.to_miles().value
            case 'kilomters':
                result = self.value / other.to_kilometers().value
        return Length(result, self.measurement)

    def __floordiv__(self, other):
        match self.measurement:
            case 'meters':
                result = self.value // other.to_meters().value
            case 'yards':
                result = self.value // other.to_yards().value
            case 'miles':
                result = self.value // other.to_miles().value
            case 'kilomters':
                result = self.value // other.to_kilometers().value
        return Length(result, self.measurement)

    def to_meters(self):
        '''Convert the length to meters'''
        measure = 'meters'
        match self.measurement:
            case 'meters':
                return self
            case 'yards':
                return Length((self.value * 0.9144), measurement=measure)
            case 'miles':
                return Length((self.value * 1_609.344), measurement=measure)
            case 'kilometers':
                return Length((self.value * 1_000), measurement=measure)

    def to_yards(self):
        '''Convert the length to yards'''
        measure = 'yards'
        match self.measurement:
            case 'yards':
                return self
            case 'meters':
                return Length((self.value / 0.9144), measurement=measure)
            case 'miles':
                return Length((self.value * 1_760), measurement=measure)
            case 'kilometers':
                return Length((self.value * 1_093.613), measurement=measure)

    def to_miles(self):
        '''Convert the length to miles'''
        measure = 'miles'
        match self.measurement:
            case 'miles':
                return self
            case 'meters':
                return Length((self.value / 1_609.344), measurement=measure)
            case 'yards':
                return Length((self.value / 1_760), measurement=measure)
            case 'kilometers':
                return Length((self.value / 1.609344), measurement=measure)

    def to_kilometers(self):
        '''Convert the length to kilometers'''
        measure = 'kilometers'
        match self.measurement:
            case 'kilometers':
                return self
            case 'meters':
                return Length((self.value / 1_000), measurement=measure)
            case 'yards':
                return Length((self.value / 1_093.613), measurement=measure)
            case 'miles':
                return Length((self.value * 1.609344 ), measurement=measure)

MARATHON = Length(42.195, measurement='kilometers')