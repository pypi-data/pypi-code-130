#!/usr/bin/env Python3
# pylint: disable=too-many-locals,too-many-arguments
"""
This module contains a few functions, which can be used to
generate plots quickly and with useful defaults"""
from __future__ import annotations
from pathlib import Path
from functools import wraps
from typing import TypeVar, List, Tuple, Union, Callable, Optional

import matplotlib as mpl
import matplotlib.pyplot as plt
from numpy import amin, amax

from .plot_settings import figure
from .types_ import Vector, Matrix

mpl.use("Agg")

In = TypeVar("In", List[float], Tuple[float],
             Vector)

In2D = TypeVar("In2D", list[list[float]], list[Vector], tuple[Vector],
               Matrix)


def plot_fit(X: In, Y: In,
             fit_function: Callable[..., float],
             xlabel: str, ylabel: str, filename: Union[str, Path],
             args: Optional[Tuple[float]] = None,
             logscale: bool = False) -> None:
    """craetes a plot of data and a fit and saves it to 'filename'"""
    N_fit = 1000

    _fit_function: Callable[[float], float]
    if args is not None:

        @wraps(fit_function)
        def _fit_function(x: float) -> float:
            """This is the function, which has been fitted"""
            return _fit_function(x, *args)
    else:
        _fit_function = fit_function

    with figure() as _:
        plt.plot(X, Y, label="data")
        X_fit = [min(X) + (max(X) - min(X)) * i / (N_fit - 1)
                 for i in range(N_fit)]
        Y_fit = [_fit_function(x) for x in X_fit]
        plt.plot(X_fit, Y_fit, label="fit")
        if logscale:
            plt.xscale("log")
            plt.yscale("log")
        plt.xlim(min(X), max(X))
        if logscale:
            plt.ylim(min(Y) * 0.97, max(Y) * 1.02)
        else:
            plt.ylim(
                min(Y) - (max(Y) - min(Y)) * 0.02,
                max(Y) + (max(Y) - min(Y)) * 0.02
            )
        plt.ylabel(ylabel)
        plt.xlabel(xlabel)
        plt.legend()
        plt.tight_layout()
        plt.savefig(filename)


def plot_surface(X: In2D, Y: In2D, Z: In2D,
                 xlabel: str, ylabel: str, zlabel: str,
                 filename: Union[str, Path],
                 log_scale: bool = False,
                 set_z_lim: bool = True) -> None:
    """create a 2D surface plot of meshgrid-like valued Xs, Ys and Zs"""
    with figure() as fig:
        plt.set_cmap("rwth_gradient")
        ax = fig.add_subplot(projection="3d")
        ax.plot_surface(X, Y, Z, cmap="rwth_gradient")

        ax.set_xlabel(xlabel)
        ax.set_ylabel(ylabel)
        ax.set_zlabel(zlabel)

        ax.set_xlim(amin(X), amax(X))  # type: ignore
        ax.set_ylim(amin(Y), amax(Y))  # type: ignore

        if set_z_lim:
            if not log_scale:
                ax.set_zlim(
                    amin(Z) - (amax(Z) - amin(Z)) * 0.02,  # type: ignore
                    amax(Z) + (amax(Z) - amin(Z)) * 0.02  # type: ignore
                )
            else:
                ax.set_zlim(
                    amin(Z) * 0.97, amax(Z) * 1.02)  # type: ignore

        if log_scale:
            ax.set_yscale("log")
            ax.set_xscale("log")
            ax.set_zscale("log")

        for spine in ax.spines.values():
            spine.set_visible(False)
        # plt.tight_layout()

        def empty_function() -> None:
            """dummy function"""

        plt.tight_layout = empty_function
        fig.subplots_adjust(bottom=0.18)
        fig.subplots_adjust(right=0.85)
        ax.dist = 13
        plt.savefig(filename)


def plot(X: In, Y: In, xlabel: str, ylabel: str,
         filename: Union[Path, str], logscale: bool = False,
         ylim: Optional[tuple[float, float]] = None) -> None:
    """Create a simple 1D plot"""
    if len(X) <= 1 or len(Y) <= 1:
        raise ValueError(
            f"The data for plot {filename} contains empty rows!")

    with figure() as _:
        plt.plot(X, Y)
        plt.xlabel(xlabel)
        plt.ylabel(ylabel)
        if logscale:
            plt.xscale("log")
            plt.yscale("log")
            if ylim is None:
                plt.ylim(min(Y) * 0.97, max(Y) * 1.02)
        elif ylim is None:
            plt.ylim(
                min(Y) - (max(Y) - min(Y)) * 0.02,
                max(Y) + (max(Y) - min(Y)) * 0.02
            )
        if ylim is not None:
            plt.ylim(*ylim)
        plt.xlim(min(X), max(X))
        plt.tight_layout()
        plt.savefig(filename)


def two_plots(x1: In, y1: In, label1: str,
              x2: In, y2: In, label2: str,
              xlabel: str, ylabel: str,
              filename: Union[Path, str],
              logscale: bool = False) -> None:
    """Create a simple 1D plot with two different graphs inside of a single
    plot and a single y-axis."""
    if len(x1) <= 1 or len(y1) <= 1 or len(y2) <= 1 or len(x2) <= 1:
        raise ValueError(
            f"The data for plot {filename} contains empty rows!")

    with figure() as _:
        plt.plot(x1, y1, label=label1)
        plt.plot(x2, y2, label=label2, linestyle="dashed")
        plt.xlabel(xlabel)
        plt.ylabel(ylabel)
        min_ = min(min(y1), min(y2))
        max_ = max(max(y1), max(y2))
        if not logscale:
            plt.ylim(
                min_ - (max_ - min_) * 0.02,
                max_ + (max_ - min_) * 0.02
            )
        else:
            plt.xscale("log")
            plt.yscale("log")
            plt.ylim(
                min_ * 0.97, max_ * 1.02)
        plt.xlim(min(x1), max(x1))
        plt.legend()
        plt.tight_layout()
        plt.savefig(filename)


def three_plots(x1: In, y1: In, label1: str,
                x2: In, y2: In, label2: str,
                x3: In, y3: In, label3: str,
                xlabel: str, ylabel: str,
                filename: Union[Path, str],
                logscale: bool = False,
                xmin: Optional[float] = None,
                xmax: Optional[float] = None) -> None:
    """Create a simple 1D plot with three different graphs inside of a single
    plot and a single y-axis."""
    if (len(x1) <= 1 or len(y1) <= 1
            or len(y2) <= 1 or len(x2) <= 1
            or len(y3) <= 1 or len(x3) <= 1):
        raise ValueError(
            f"The data for plot {filename} contains empty rows!")

    with figure() as _:
        plt.plot(x1, y1, label=label1)
        plt.plot(x2, y2, label=label2, linestyle="dashed")
        plt.plot(x3, y3, label=label3, linestyle="dotted")
        plt.xlabel(xlabel)
        plt.ylabel(ylabel)
        min_ = min(min(y1), min(y2), min(y3))
        max_ = max(max(y1), max(y2), max(y3))
        if not logscale:
            plt.ylim(
                min_ - (max_ - min_) * 0.02,
                max_ + (max_ - min_) * 0.02
            )
        else:
            plt.xscale("log")
            plt.yscale("log")
            plt.ylim(
                min_ * 0.97, max_ * 1.02)
        if xmin is not None and xmax is not None:
            plt.xlim(xmin, xmax)
        else:
            plt.xlim(min(x1), max(x1))
        plt.legend()
        plt.tight_layout()
        plt.savefig(filename)


def two_axis_plots(x1: In, y1: In, label1: str,
                   x2: In, y2: In, label2: str,
                   xlabel: str, ylabel: str,
                   ylabel2: str,
                   filename: Union[Path, str],
                   ticks: Optional[tuple[list[float], list[str]]] = None,
                   xlim: Optional[tuple[float, float]] = None,
                   color: tuple[int, int] = (0, 1))\
        -> None:
    """Create a simple 1D plot with two different graphs inside of a single
    plot with two y-axis.
    The variable "ticks" sets costum y-ticks on the second y-axis. The first
    argument gives the position of the ticks and the second argument gives the
    values to be shown.
    Color selects the indeces of the chosen color-wheel, which should be taken
    for the different plots. The default is (1,2)."""
    if len(x1) <= 1 or len(y1) <= 1 or len(y2) <= 1 or len(x2) <= 1:
        raise ValueError(
            f"The data for plot {filename} contains empty rows!")

    with figure() as fig:
        ax1 = fig.add_subplot(111)
        # access colour
        prop_cycle = plt.rcParams["axes.prop_cycle"]
        colors = prop_cycle.by_key()["color"]

        # first plot
        lines = ax1.plot(x1, y1, label=label1,
                         color=colors[color[0]])
        ax1.set_xlabel(xlabel)
        ax1.set_ylabel(ylabel)
        ax1.set_ylim(
            min(y1) - (max(y1) - min(y1)) * 0.02,
            max(y1) + (max(y1) - min(y1)) * 0.02
        )

        # second plot
        ax2 = ax1.twinx()
        lines += ax2.plot(x2, y2, label=label2,
                          color=colors[color[1]],
                          linestyle="-.")
        ax2.set_ylabel(ylabel2)
        ax2.set_ylim(
            min(y2) - (max(y2) - min(y2)) * 0.02,
            max(y2) + (max(y2) - min(y2)) * 0.02
        )

        # general settings
        if xlim is None:
            plt.xlim(min(x1), max(x1))
        else:
            plt.xlim(*xlim)
        labels = [line.get_label() for line in lines]
        plt.legend(lines, labels)
        # ticks
        if ticks is not None:
            ax2.set_yticks(ticks[0])
            ax2.set_yticklabels(ticks[1])
        plt.tight_layout()
        plt.savefig(filename)
