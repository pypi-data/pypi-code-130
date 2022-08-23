#!/usr/bin/env python3
# _*_ coding: utf-8 _*_
"""
Converts the data which the alicona generates
for usage by the commercial software which finds the flow factors.
The needed data is 2D surface data.
This data can be exported by using Alicona's function 'export as .txt2'

usage:
    ./alicona_converter -h # this prints the usage to the terminal
"""
from __future__ import annotations

from re import match
from functools import wraps
from typing import Callable, Optional, Iterator, Union, Any
from pathlib import Path
from textwrap import dedent

from numba import jit
import numpy as np

from python_module.types_ import Matrix, Vector

__version__ = "1.0.7"


def single_time_callable(func: Callable[..., None]) -> Callable[..., None]:
    """decorator:
    make a function or method only a single time
    callable. Pass in all other instances"""
    @wraps(func)
    def _func(*_args: Any, **kwargs: Any) -> None:
        """Single-Time-callable version of func"""
        if not _func.called:  # type: ignore
            _func.called = True  # type: ignore
            func(*_args, **kwargs)
        else:
            pass
    _func.called = False  # type: ignore
    return _func


@jit(nopython=True, nogil=True, cache=True)
def resize(old_array: Vector, size: int) -> Vector:
    """Change the size of the input array."""
    new: Vector
    if size <= old_array.size:
        new = old_array[:size]  # type: ignore
        return new
    # else
    new = np.empty(size)
    new[:old_array.size] = old_array  # type: ignore
    return new


@jit(nopython=True, nogil=True)
def mean(X: Matrix) -> float:
    """calculates the mean of the third value in a list of tuples
    @param X list of tuples (x,y,z)
    @return mean of z"""
    result: float
    result = sum(X[:, 2]) / len(X)  # type: ignore
    return result


@jit(nopython=True)
def get_x_values(data: Matrix) ->\
        tuple[Vector, int]:
    """
    This function calculates the first fields of the new transformed
    output-matrix. It finds the x-values and the first y and
    z-values. It also returns the index, at which the y-evaluation
    has to start.
    @param data input data
    @return x-values, start_index
    """
    _x: Vector = np.empty(data.shape[0])
    first_y = data[0, 1]
    # first iteration determines x and and n_x
    second_line_index = -1
    length = 0
    for i, point in enumerate(data):
        if point[1] != first_y:
            second_line_index = i
            break
        _x[i] = point[0]
        length += 1
    assert second_line_index >= 0
    # check for the length of the second line, to see if it is much longer
    second_x: Vector = np.empty(data.shape[0])
    second_y: float = data[second_line_index, 1]
    second_length = 0
    for i, point in enumerate(data[second_line_index:]):
        if point[1] != second_y:
            break
        second_x[i] = point[0]
        second_length += 1
    # skip the first line if the second line
    # has ~ 1.5 times the size of the first line
    start_index = 0
    if second_length > 1.5 * length:
        start_index = second_line_index
        _x = resize(second_x, second_length)
    else:
        _x = resize(_x, length)
    # sometimes the dimension of the data changes during the scan
    # therefore chose the largest rectangle
    # in y-direction which is completely inside the data
    # drop other values
    return _x, start_index


@jit(nopython=True)
def convert_data(data: Matrix) ->\
        tuple[Matrix, Vector, Vector, int, int]:
    """Convert between the different input data formats."""
    # pylint: disable=too-many-locals
    _x: Vector
    _y: Vector = np.empty(data.shape[0])
    _z: Matrix

    start_index: int
    _x, start_index = get_x_values(data)
    _z = np.empty((_x.size, _x.size))

    jump_index: int = 0
    n_x: int = len(_x)  # just the first value for n_x
    n_y: int = 0
    index: int = start_index
    size = len(data)
    while index < size:
        # define new jump-index
        if index + n_x + jump_index < size:
            if data[index, 0] != data[index + n_x + jump_index, 0]:
                jump_index = 0
                while data[index, 0] != data[index + n_x + jump_index, 0]:
                    jump_index += 1
                    if index + n_x + jump_index >= data.shape[0]:
                        break  # skip the last unfinished row
            _y[n_y] = data[index, 1]
            n_y += 1
        else:
            break
        # fill in values for z
        _z[:, n_y-1] = data[index:index+n_x, 2]

        if n_y >= _z.shape[1]:
            # resize z
            new = np.empty((n_x, n_y*2))
            new[:, :n_y] = _z
            _z = new

        index = index + n_x + jump_index

    # substract the mean from z
    mu_z = mean(data)
    _y = resize(_y, n_y)
    _z = _z[:, :n_y]
    _z = _z - mu_z

    # save the x and y dimensions
    return _z, _x, _y, n_x, n_y


class SurfaceData:
    """this class' instances contain all relevant surface-data"""
    _z: Matrix
    _x: Vector
    _y: Vector
    _n_x: int
    _n_y: int
    filename: Union[str, Path]
    # data: list[tuple[float, ...]]
    data: Matrix

    def __init__(self, filename: Union[str, Path],
                 N: Optional[int] = None):
        """Fill the instance with the needed data. Constructor of this class.
        @param filename name of the Alicona-data-file"""
        self.data = parse_alicona_data(filename, N)
        self.filename = filename
        # perform the conversion only once and only if needed

    def __getitem__(self, key: int) -> Vector:
        """acces the instance's elements by key, like object[2] etc."""
        if key >= len(self):
            raise IndexError(f"Tried accessing index {key} out of {len(self)}")
        result: Vector
        result = self.data[key]  # type: ignore
        return result

    def __len__(self) -> int:
        """returns the number of data-points"""
        return len(self.data)

    def __iter__(self) -> Iterator[tuple[float, ...]]:
        """Iterate over all items."""
        for value in self.data:
            yield value

    @single_time_callable
    def convert_data(self) -> None:
        """converts the data in (x,y,z)-form to data in ordered (z)-form"""
        self._z, self._x, self._y, self._n_x, self._n_y = convert_data(
            self.data)

    def write_flow_factor_data(
            self, filename: Union[str, Path], description: str = "", *,
            E: float = 0, nu: float = 0, yield_pressure: float = 0,
            N: Optional[int] = None)\
            -> None:
        """writes the flow factor software input file
        based on the contained data
        @param filename name of the file which shall be created"""
        self.convert_data()
        if not E or not nu or not yield_pressure:
            print(dedent("""E, nu and the yield pressure are
                         needed for an input-file
                         for Tribo-X. If not all of them are given,
                         the input file
                         cannot be used in Tribo-X."""))

        with open(filename, "w", encoding="utf-8") as output_file:
            output_file.write(";MicroSim data\n")
            output_file.write(";\n")
            output_file.write("[general]\n")
            output_file.write(";\n")
            output_file.write(f"description={description}\n")
            output_file.write(";\n")
            output_file.write("[data]\n")
            if E:
                output_file.write(f"E_[N/mm^2]={E*1e3}\n")
            if nu:
                output_file.write(f"nue={nu}\n")
            output_file.write(";plastic flow pressure\n")
            if yield_pressure:
                output_file.write(f"pc_lim_[N/mm^2]={yield_pressure}\n")
            output_file.write(";\n")
            # number of points
            output_file.write(f"nx={len(self._x) if N is None else N}\n")
            output_file.write(f"ny={len(self._y) if N is None else N}\n")
            # distance of points
            output_file.write(f"dx_[ym]={abs(self._x[1]-self._x[0])}\n")
            output_file.write(f"dy_[ym]={abs(self._y[1]-self._y[0])}\n")
            output_file.write(";\n")
            output_file.write("<data_start>\n")
            if N is not None:
                for row in self._z[:N]:
                    output_file.write("\t".join(f"{value}"
                                      for value in row[:N]) + "\n")
            else:
                for row in self._z:
                    output_file.write("\t".join(f"{value}"
                                      for value in row) + "\n")
            output_file.write("<data_end>")

    def write_1d_data(self, filename: Union[str, Path],
                      y_direction: bool = True) -> None:
        """writes the data into a file which only contains a single line
        it uses data from the center of the file
        @param filename file onto which the data is written to
        @param y_direction if set to false,
            data in x direction is used rather than data in y direction
        """
        self.convert_data()
        if y_direction:
            line_data_x = tuple(self._y)
            line_data_y = tuple(self._z[self._n_x // 2])
        else:
            line_data_x = tuple(self._x)
            line_data_y = tuple(row[self._n_y // 2] for row in self.data)
        min_x = min(line_data_x)
        line_data_x = tuple(value - min_x for value in line_data_x)
        # change the direction of the data if it is in inverse direction
        if line_data_x[1] < line_data_x[0]:
            line_data_x = line_data_x[::-1]
            line_data_y = line_data_y[::-1]
        mean_y = sum(line_data_y) / len(line_data_y)
        line_data_y = tuple(y - mean_y for y in line_data_y)
        self._write_data_to_file(filename, line_data_x, [line_data_y],
                                 use_multiples=False)

    @staticmethod
    def _write_data_to_file(filename: Union[str, Path], Y: tuple[float, ...],
                            Z: list[tuple[float, ...]],
                            use_multiples: bool = False) -> None:
        """
        this function writes the data, which has been calculated
        previously to an external file
        @param Y x-value or y-value
        @param Z z-value
        @param multiples print multiple lines of Z-values if set to true"""
        with open(filename, "w", encoding="utf-8") as output_file:
            if not use_multiples:
                for y, z in zip(Y, Z[0]):
                    output_file.write(f"{y*1e-3} {z*1e-3}\n")
            else:
                for row in zip(Y, *Z):
                    row_mm = [r * 1e-3 for r in row]
                    output_string = f"{row_mm[0]}"
                    for r in row_mm[1:]:
                        output_string += f"\t{r}"
                    output_string += "\n"
                    output_file.write(output_string)

    def write_1d_data_holes(self, filename: Union[str, Path],
                            multiples: bool = False)\
            -> None:
        """write the data to a 1D file.
        use this version if the measured surface contains many holes
        @param filename name of the file to
            which the 1D line-scan should be written to
        @param multiples plot one column for each of the hole-free rows"""
        sorted_data: dict[float, list[tuple[float, float]]] = {}
        for d in self.data:
            if d[0] not in sorted_data:
                sorted_data[d[0]] = []
            sorted_data[d[0]] += [(d[1], d[2])]
        max_key = self._find_maximal_key(sorted_data)
        Y, _ = zip(*sorted_data[max_key[0]])
        Z = []
        for key in max_key:
            _, Zi = zip(*sorted_data[key])
            mean_Z = sum(Zi) / len(Zi)
            Zi = tuple(z - mean_Z for z in Zi)
            Z += [Zi]

        min_Y = min(Y)
        Y = tuple(y - min_Y for y in Y)
        if Y[1] < Y[0]:
            Y = Y[::-1]
            for i, _ in enumerate(Z):
                Z[i] = Z[i][::-1]
        self._write_data_to_file(filename, Y, Z, use_multiples=multiples)

    _Value = list[tuple[float, float]]

    @staticmethod
    def _find_maximal_key(sorted_data: dict[float, _Value]) -> list[float]:
        """
        return a list of keys, on which the length of the first value
        in each tuple has the maximal length
        """
        max_key = []
        max_len = 0
        for item in sorted_data.values():
            if len(item) > max_len:
                max_len = len(item)
        # find all lines with this length
        for column_index, value in sorted_data.items():
            if len(value) == max_len:
                max_key += [column_index]
        return max_key


def parse_alicona_data(filename: Union[str, Path], N: Optional[int] = None)\
        -> Matrix:
    """read the data from an Alicona-output to python data types
    @param filename name of the alicona-data-file
    @return list of tuples: (x,y,z)"""
    list_ = []
    max_y_length = 0  # counts repititions
    max_x_length = 0
    current_y_value = None
    current_x_length = 0
    with open(filename, "r", encoding="utf-8") as input_file:
        first_line = input_file.readline()
        if not match(
            "GPoint3DVector", first_line
        ):  # slightly different format without header and fooder
            list_ += [tuple(float(value) for value in first_line.split())]
        for _, line in enumerate(input_file):
            if match("{|}", line):
                break
            list_ += [tuple(float(value) for value in line.split())]
            if N is not None:
                if current_y_value is None:
                    current_y_value = list_[-1][1]
                if list_[-1][1] == current_y_value:
                    current_x_length += 1
                    max_x_length = max(current_x_length, max_x_length)
                else:
                    if current_x_length >= N:
                        max_y_length += 1
                    current_x_length = 0
                    current_y_value = list_[-1][1]
                if max_x_length > N and max_y_length > N:
                    break
    if N is not None:
        if max_y_length < N or max_x_length < N:
            raise IndexError(
                "The dimension of the input data is not large enough")

    return np.array(list_)
