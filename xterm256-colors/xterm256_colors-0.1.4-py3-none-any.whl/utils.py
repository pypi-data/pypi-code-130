from __future__ import annotations

import statistics
from collections import defaultdict
from contextlib import contextmanager
from typing import Any, Iterable

from ._compat import Sequence, requires_colormath
from .colors import Fore256, XtermCodes, XtermColor


__all__ = [
    'print_colors',
    'print_all_colors',
    'print_differentiated_colors',
    'print_color_table',
    'calculate_distance_matrix',
    'find_differentiated_colors',
]


def print_colors(colors: Iterable[XtermColor]):
    """Print swatch, code, and name for each of the specified colours"""
    for color in colors:
        label = f'{color.code:>4d} {color.name}'
        if color.is_background and color.is_bright:
            label = Fore256.BLACK(label)
        print(color.swatch, color(label))


def print_all_colors(codes: XtermCodes = Fore256):
    """Print swatch, code, and name for all xterm-256 colours"""
    print_colors(codes.all_colors.values())


def print_differentiated_colors(codes: XtermCodes = Fore256):
    """Print swatch, code, and name for each of the curated "differentiated" colours"""
    print_colors(codes.differentiated_colors)


def print_color_table(colors: Iterable[XtermColor], sort: bool = True):
    """Print a table displaying color swatch pairs for all combinations of colors"""
    if sort:
        colors = sorted(colors, key=lambda color: color.code)
    elif not isinstance(colors, Sequence):
        colors = tuple(colors)

    @contextmanager
    def row(title: Any = '', *headers):
        print_cell(title)
        for cell in headers:
            print_cell(cell)

        yield
        print()

    def th():
        return row('', '')

    def print_cell(s: Any = '') -> None:
        print(f'{s:^4}', end='')

    def swatch(color: XtermColor, n: int, c: str = '▇') -> str:
        return color.swatch(n=n, c=c)

    def print_comparison(a: XtermColor, b: XtermColor) -> None:
        print_cell(f' {swatch(a, 1)}{swatch(b, 1)} ')

    # Header
    with th():
        for color in colors:
            print_cell(swatch(color, 4))

    with th():
        for color in colors:
            print_cell(color.code)

    # Body
    for row_color in colors:
        with row(swatch(row_color, 4), row_color.code):
            for col_color in colors:
                if row_color is not col_color:
                    print_comparison(row_color, col_color)
                else:
                    print_cell()


ColorDistanceMatrix = dict[XtermColor, dict[XtermColor, float]]


@requires_colormath
def calculate_distance_matrix(colors: Iterable[XtermColor]) -> ColorDistanceMatrix:
    """Calculate the Delta-E 2000 colour distance between each of the specified colours

    Note that both the forward and backward directions are stored in the resulting
    dictionary — i.e. dist_mat[RED][YELLOW] == dist_mat[YELLOW][RED]
    """
    from colormath.color_diff import delta_e_cie2000  # type: ignore[import]

    if not isinstance(colors, Sequence):
        colors = tuple(colors)

    dist_mat: ColorDistanceMatrix = defaultdict(dict)
    for i, a in enumerate(colors):
        for b in colors[i + 1:]:
            dist = delta_e_cie2000(a.as_lab_color, b.as_lab_color)
            dist_mat[a][b] = dist_mat[b][a] = dist

    return dist_mat


def find_differentiated_colors(
    colors: Iterable[XtermColor],
    n: int,
    dist_mat: ColorDistanceMatrix | None = None,
    min_dist: float = float('-Inf'),
) -> set[XtermColor]:
    """Find N colors most(-ish) different from each other

    :param colors:
        Population of colours to select differentiated subset from.

    :param n:
        Number of colours to include in returned subset.

    :param dist_mat:
        A pre-calculated colour distance matrix to use. If not supplied, one
        will be calculated.

    :param min_dist:
        Minimum distance each colour must have between each other in the subset.

    """
    if not isinstance(colors, Sequence):
        colors = tuple(colors)

    if dist_mat is None:
        dist_mat = calculate_distance_matrix(colors)

    best_pair: tuple[XtermColor, XtermColor] | tuple = ()
    max_dist = 0.0

    for i, a in enumerate(colors):
        for b in colors[i + 1:]:
            if (dist := dist_mat[a][b]) > max_dist:
                max_dist = dist
                best_pair = (a, b)

    subset: set[XtermColor] = {*best_pair}

    while len(subset) < n:
        max_avg_dist = 0.0
        v_avg_best: XtermColor | None = None

        for v in colors:
            if v in subset:
                continue

            dists = []
            is_below_min_dist = False
            for v_prime in subset:
                dist = dist_mat[v][v_prime]
                if dist < min_dist:
                    is_below_min_dist = True
                    break

                dists.append(dist)

            if is_below_min_dist:
                continue

            if (avg_dist := statistics.mean(dists)) > max_avg_dist:
                max_avg_dist = avg_dist
                v_avg_best = v

        if v_avg_best:
            subset.add(v_avg_best)

    return subset
