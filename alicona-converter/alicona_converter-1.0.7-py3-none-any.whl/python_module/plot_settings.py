#!/usr/bin/env python3
"""
This module contains the settings for the various plots.
Plots can be created using the 'figure' deocorator from this module.
Multiple plots for various cases will be created and saved to
the hard drive
"""
from __future__ import annotations

from contextlib import contextmanager
from math import sqrt
import os.path
from copy import copy
from functools import wraps
from typing import (
    Generator, Optional, Union, Callable, TypeVar, Any)
from pathlib import Path

import matplotlib as mpl
import matplotlib.pyplot as plt
from matplotlib.pyplot import Axes
from matplotlib.figure import Figure
from matplotlib import colors
from matplotlib import cm

from .utilities import mkdir_p, translate

mpl.use("Agg")

SPINE_COLOR = "black"
FIGSIZE = (4.0, 4.0 * (sqrt(5) - 1.0) / 2.0)
_savefig = copy(plt.savefig)  # backup the old save-function


def linestyles() -> Generator[str, None, None]:
    """get the line-stiles as an iterator"""
    yield "-"
    yield "dotted"
    yield "--"
    yield "-."


rwth_colorlist: list[tuple[int, int, int]] = [(0, 84, 159), (246, 168, 0),
                                              (161, 16, 53), (0, 97, 101)]
rwth_cmap = colors.ListedColormap(rwth_colorlist, name="rwth_list")
cm.register_cmap(name="rwth_list", cmap=rwth_cmap)

rwth_gradient: dict[str, tuple[tuple[float, float, float],
                               tuple[float, float, float]]] = {
    "red": ((0.0, 0.0, 0.0), (1.0, 142 / 255, 142 / 255)),
    "green": ((0.0, 84 / 255.0, 84 / 255), (1.0, 186 / 255, 186 / 255)),
    "blue": ((0.0, 159 / 255, 159 / 255), (1.0, 229 / 255, 229 / 255)),
}


def make_colormap(seq: list[tuple[tuple[Optional[float], ...],
                                  float,
                                  tuple[Optional[float], ...]]],
                  name: str = "rwth_gradient")\
        -> colors.LinearSegmentedColormap:
    """Return a LinearSegmentedColormap
    seq: a sequence of floats and RGB-tuples. The floats should be increasing
    and in the interval (0,1).
    """
    cdict: dict[str, list[tuple[float,
                                Optional[float],
                                Optional[float]
                                ]
                          ]] =\
        {"red": [], "green": [], "blue": []}
    for item in seq:
        r1, g1, b1 = item[0]
        r2, g2, b2 = item[2]

        cdict["red"].append((item[1], r1, r2))
        cdict["green"].append((item[1], g1, g2))
        cdict["blue"].append((item[1], b1, b2))
    return colors.LinearSegmentedColormap(name, cdict)


def partial_rgb(*x: float) -> tuple[float, ...]:
    """return the rgb value as a fraction of 1"""
    return tuple(v / 255.0 for v in x)


hks_44 = partial_rgb(0.0, 84.0, 159.0)
hks_44_75 = partial_rgb(64.0, 127.0, 183.0)
rwth_orange = partial_rgb(246.0, 168.0, 0.0)
rwth_orange_75 = partial_rgb(250.0, 190.0, 80.0)
rwth_gelb = partial_rgb(255.0, 237.0, 0.0)
rwth_magenta = partial_rgb(227.0, 0.0, 102.0)
rwth_bordeux = partial_rgb(161.0, 16.0, 53.0)


rwth_gradient_map = make_colormap(
    [
        ((None, None, None), 0., hks_44),
        (hks_44_75, 0.33, hks_44_75),
        (rwth_orange_75, 0.66, rwth_orange),
        (rwth_bordeux, 1., (None, None, None))
    ]
)
cm.register_cmap(name="rwth_gradient", cmap=rwth_gradient_map)


def latexify(fig_width: Optional[float] = None,
             fig_height: Optional[float] = None,
             columns: int = 1, font_size: int = 10) -> None:
    """Set up matplotlib's RC params for LaTeX plotting.
    Call this before plotting a figure.

    Parameters
    ----------
    fig_width : float, optional, inches
    fig_height : float,  optional, inches
    columns : {1, 2}
    """

    if fig_width is None:
        fig_width = 3.39 if columns == 1 else 6.9  # width in inches

    if fig_height is None:
        golden_mean = (sqrt(5) - 1.0) / 2.0  # Aesthetic ratio
        fig_height = fig_width * golden_mean  # height in inches

    MAX_HEIGHT_INCHES = 8.0
    if fig_height > MAX_HEIGHT_INCHES:
        print(
            "WARNING: fig_height too large:"
            + f"{fig_height}"
            + " so will reduce to"
            + f"{MAX_HEIGHT_INCHES}"
            + " inches."
        )
        fig_height = MAX_HEIGHT_INCHES

    params: dict[str, Union[
        int,
        list[float],
        str]]
    params = {
        "axes.labelsize": font_size,  # fontsize for x and y labels (was 10)
        # 'text.latex.preamble': [r'\usepackage{gensymb}'],
        "axes.titlesize": font_size,
        # 'text.fontsize': 8, # was 10
        "font.size": font_size,
        "legend.fontsize": font_size - 2,  # was 10
        "xtick.labelsize": font_size - 2,
        "ytick.labelsize": font_size - 2,
        # 'text.usetex': True,
        "figure.figsize": [fig_width, fig_height],
        "font.family": "serif",
    }

    mpl.rcParams.update(params)


def format_axes(ax: Axes) -> Axes:
    """format the axes for a latex-plot"""
    for spine in ["top", "right"]:
        ax.spines[spine].set_visible(False)

    for spine in ["left", "bottom"]:
        ax.spines[spine].set_color(SPINE_COLOR)
        ax.spines[spine].set_linewidth(0.5)

    ax.xaxis.set_ticks_position("bottom")
    ax.yaxis.set_ticks_position("left")

    for axis in [ax.xaxis, ax.yaxis]:
        axis.set_tick_params(direction="out", color=SPINE_COLOR)
    return ax


def new_save(filename: Union[Path, str],
             dpi: Optional[int] = None,
             bbox_inches: Optional[str] = None
             )\
        -> None:
    """overwrite the save command in order to
    also create a plot using a different style"""
    fig = plt.gcf()
    ax = fig.gca()
    if not hasattr(ax, "zaxis"):
        bbox_inches = "tight"
    _savefig(filename, dpi=dpi)  # regular save

    # half-width journal save
    half_width_journal(filename, ax, fig, bbox_inches)

    # comparison full width journal save
    comparison_width_journal(filename, ax, fig, bbox_inches)

    # dissertation plot
    dissertation_plot(filename, ax, fig, bbox_inches)

    # arial plots
    arial_journal(filename, ax, fig, bbox_inches)

    # presentation plot
    presentation_plot(filename, ax, fig, bbox_inches)

    # german plots

    with germanify(ax):
        arial_journal(str(filename).replace(".pdf", "_german.pdf"),
                      ax, fig, bbox_inches)
        presentation_plot(str(filename).replace(".pdf", "_german.pdf"),
                          ax, fig, bbox_inches)
        dissertation_plot(str(filename).replace(".pdf", "_german.pdf"),
                          ax, fig, bbox_inches)


Return = TypeVar("Return")


def revert_settings(func: Callable[..., None])\
        -> Callable[..., None]:
    """ revert to the default settings after creating
    a plot"""

    @wraps(func)
    def inner_function(*args: Any) -> None:
        """this is the plotting-function"""
        func(*args)

        mpl.rcParams.update(mpl.rcParamsDefault)
        plt.style.use("default")

    return inner_function


File = Union[str, Path]


@revert_settings
def dissertation_plot(filename: File, ax: Axes, fig: Figure,
                      bbox_inches: Optional[str]) -> None:
    """Create a black and white plot for the dissertation."""
    plt.style.use("grayscale")
    plt.set_cmap("gray")
    latexify()
    path_name = os.path.join(
        os.path.dirname(filename), "dissertation")
    mkdir_p(path_name)
    if not hasattr(ax, "zaxis"):
        plt.tight_layout()
    fig.canvas.draw()
    _savefig(os.path.join(
        path_name, os.path.basename(filename)),
             bbox_inches=bbox_inches)


@revert_settings
def half_width_journal(filename: File, ax: Axes, fig: Figure,
                       bbox_inches: Optional[str]) -> None:
    """create and save plots for a half width journal column"""
    half_width_size = (3.34, 3.34 * (sqrt(5) - 1.0) / 2.0)
    fig.set_size_inches(*half_width_size)
    latexify(
        fig_width=half_width_size[0],
        fig_height=half_width_size[1], font_size=10
    )
    if not hasattr(ax, "zaxis"):
        plt.tight_layout()
    half_width_pathname = os.path.join(os.path.dirname(filename),
                                       "half_width")
    mkdir_p(half_width_pathname)
    half_width_name = os.path.join(half_width_pathname,
                                   os.path.basename(filename))
    fig.canvas.draw()
    _savefig(half_width_name, bbox_inches=bbox_inches)
    _savefig(
        half_width_name.replace(".pdf", ".png"), dpi=300,
        bbox_inches=bbox_inches)
    # png better for MS-word documents


@revert_settings
def comparison_width_journal(filename: File, ax: Axes,
                             fig: Figure, bbox_inches: Optional[str])\
        -> None:
    """
    create and save plots to be shown next to each other in a
    full width journal
    """
    half_width_size = (2.7, 3.34 * (sqrt(5) - 1.0) / 2.0)
    fig.set_size_inches(*half_width_size)
    latexify(
        fig_width=half_width_size[0],
        fig_height=half_width_size[1], font_size=10
    )
    if not hasattr(ax, "zaxis"):
        plt.tight_layout()
    half_width_pathname = os.path.join(os.path.dirname(filename),
                                       "comparison")
    mkdir_p(half_width_pathname)
    half_width_name = os.path.join(half_width_pathname,
                                   os.path.basename(filename))
    fig.canvas.draw()
    _savefig(half_width_name, bbox_inches=bbox_inches)


@revert_settings
def arial_journal(filename: File, ax: Axes, fig: Figure,
                  bbox_inches: Optional[str]) -> None:
    """create plots using a sans-serif-font (not actually
    arial, but helvetica)"""
    mpl.rc("font", family="sans-serif")
    mpl.rcParams["text.usetex"] = False
    mpl.rcParams["mathtext.fontset"] = "stixsans"

    # font = {'size'   : 10}
    # mpl.rc('font', **font)
    mpl.rcParams["font.family"] = "sans-serif"
    mpl.rcParams["font.size"] = 10
    mpl.rc("mathtext", default="regular")
    fig = plt.gcf()
    ax = plt.gca()
    mkdir_p(os.path.join(os.path.dirname(filename), "arial"))
    fig.set_size_inches(*FIGSIZE)
    mpl.rc("font", family="sans-serif")
    # needed twice in order to
    # change all visible ticks and not leave some out
    try:
        if not hasattr(ax, "zaxis"):
            plt.tight_layout()
    except IndexError:
        pass
    for axi in ax.figure.axes:
        # axi.ticklabel_format(useMathText=False)
        items = [
            axi.xaxis.label,
            axi.yaxis.label,
            *axi.get_xticklabels(),
            *axi.get_yticklabels(),
        ]
        if axi.get_legend():
            items += [*axi.get_legend().texts]
        for item in items:
            item.set_fontname("sans-serif")
            # item.set_fontsize(10)
        try:  # z-axis
            assert axi.zaxis
            for item in [axi.zaxis.label, *axi.get_zticklabels()]:
                item.set_fontname("sans-serif")
                # item.set_fontsize(10)
        except AttributeError:
            pass
        except AssertionError:
            pass
    try:
        if not hasattr(ax, "zaxis"):
            plt.tight_layout()
    except IndexError:
        pass
    new_name = os.path.join(
        os.path.dirname(filename),
        "arial",
        os.path.basename(filename).replace(".pdf", ".svg"),
    )
    fig.canvas.draw()
    _savefig(new_name, bbox_inches=bbox_inches)
    new_name = new_name.replace(".svg", ".png")
    _savefig(new_name, bbox_inches=bbox_inches)
    new_name = new_name.replace(".png", ".pdf")
    _savefig(new_name, bbox_inches=bbox_inches)


def _germanify(ax: Axes, reverse: bool = False) -> None:
    """
    translate a figure from english to german.
    The direction can be reversed, if reverse it set to True
    Use the decorator instead
    """
    for axi in ax.figure.axes:
        # axi.ticklabel_format(useMathText=False)
        items = [
            axi.xaxis.label,
            axi.yaxis.label,
            *axi.get_xticklabels(),
            *axi.get_yticklabels(),
        ]
        if axi.get_legend():
            items += [*axi.get_legend().texts]
        for item in items:
            item.set_text(translate(item.get_text(),
                                    reverse=reverse))
    try:
        if not hasattr(ax, "zaxis"):
            plt.tight_layout()
    except IndexError:
        pass


@contextmanager
def germanify(ax: Axes) -> Generator[None, None, None]:
    """
    Translate the plot to german and reverse
    the translation in the other direction
    """
    try:
        _germanify(ax)
        yield
    except Exception as e:
        print("Translation of the plot has failed")
        print(e)
        raise
    finally:
        _germanify(ax, reverse=True)


@revert_settings
def presentation_plot(filename: File, ax: Axes, fig: Figure,
                      bbox_inches: Optional[str]) -> None:
    """
    create a plot to be used in a presenation
    """

    # fig.set_size_inches(figsize[0]*0.6*factor, figsize[1]*0.6*factor)
    fig.set_size_inches(7.0, 5.0)
    # increase line thickness
    for axi in ax.figure.axes:
        for line in axi.get_lines():
            line.set_linewidth(4)

    # create the plots for the presentation
    presentation_fontsize = 22
    presentation_pathname = os.path.join(os.path.dirname(filename),
                                         "presentation")
    mkdir_p(presentation_pathname)
    # plt.locator_params(nbins=5)
    # This option is probably no longer supported

    for axi in ax.figure.axes:
        items = [
            axi.xaxis.label,
            axi.yaxis.label,
            *axi.get_xticklabels(),
            *axi.get_yticklabels(),
        ]
        if axi.get_legend():
            items += [*axi.get_legend().texts]
        for item in items:
            item.set_fontname("Arial")
            item.set_fontsize(presentation_fontsize)
            item.set_text(translate(item.get_text()))
        try:  # z-axis
            assert axi.zaxis, "There is no z-axis."
            for item in [axi.zaxis.label, *axi.get_zticklabels()]:
                item.set_fontname("Arial")
                item.set_fontsize(presentation_fontsize)
        except AttributeError:
            pass
        except AssertionError:
            pass

    # font = {'size'   : 80}

    # mpl.rc('font', **font)
    plt.set_cmap("rwth_list")
    try:
        if not hasattr(ax, "zaxis"):
            plt.tight_layout()
    except IndexError:
        pass
    new_name = os.path.join(
        presentation_pathname,
        os.path.basename(filename)
    )
    fig.canvas.draw()
    _savefig(new_name.replace(".pdf", ".png"),
             bbox_inches=bbox_inches, dpi=300)
    _savefig(new_name.replace(".png", ".pdf"),
             bbox_inches=bbox_inches)


@contextmanager
def figure(figsize: tuple[float, float] = FIGSIZE,
           factor: Optional[float] = None)\
        -> Generator[Figure, None, None]:
    """context manager to open an close the file.
    this creates the latex plot for IEEE"""
    if factor is not None:
        figsize = (figsize[0] * factor, figsize[1] * factor)
    else:
        factor = 1.0
    latexify(fig_width=6.27 * 0.45 * factor, font_size=10)
    # plt.set_cmap(rwth_cmap)
    plt.set_cmap("rwth_gradient")
    mpl.rcParams.update({"figure.autolayout": True})
    fig = plt.figure(figsize=figsize)

    plt.savefig = new_save

    try:
        yield fig
    except Exception as e:
        print("Creation of plot failed:")
        print(e)
        raise
    finally:
        plt.close(fig)
        plt.close("all")
        plt.savefig = _savefig


@contextmanager
def presentation_figure(figsize: tuple[float, float] = (4, 3)) ->\
        Generator[Axes, None, None]:
    """context manager to open an close the file.
    default seaborn-like plot"""
    fig, ax = plt.subplots(figsize=figsize)
    mpl.rcParams["text.latex.preamble"] = [
        r"\usepackage{helvet}",  # set the normal font here
        r"\usepackage{sansmath}",  # load up the sansmath so that math
        # -> helvet
        r"\sansmath",  # <- tricky! -- gotta actually tell tex to use!
    ]
    mpl.rc("font", family="sans-serif")
    mpl.rc("text", usetex=True)
    font = {"size": 30}

    mpl.rc("font", **font)
    plt.set_cmap("rwth_list")
    try:
        yield ax
    except Exception as e:
        print("creation of plot failed")
        print(e)
        raise
    finally:
        plt.close(fig)
        plt.close("all")
        mpl.rcParams.update(mpl.rcParamsDefault)
        plt.style.use("default")
