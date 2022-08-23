#!/usr/bin/python
"""this set of unit-tests test the creation of plots by
'python-module'"""
from os import remove
from os.path import exists
from shutil import rmtree
from pathlib import Path

from numpy import linspace

from python_module.types_ import Vector

from python_module.default_plots import plot, two_plots, two_axis_plots


def test_default_plot(tmp_path: Path) -> None:
    """
    test the default plot creation by 'plot'
    """
    x_test: Vector = linspace(1., 100., 100)
    y_test: Vector = x_test**2
    x_label = "x-values"
    y_label = "y-values"
    filename = ".test_plot.tmp.pdf"
    plot(x_test, y_test, x_label, y_label, tmp_path / filename)
    assert exists(tmp_path / filename)
    remove(tmp_path / filename)
    # logarithmic plot
    plot(x_test, y_test, x_label, y_label, tmp_path / filename, logscale=True)
    assert exists(tmp_path / filename)
    remove(tmp_path / filename)
    subfolder = ["arial", "comparison", "half_width", "presentation"]
    for folder in subfolder:
        assert exists(tmp_path / folder / filename)
        rmtree(tmp_path / folder)


def test_two_plots(tmp_path: Path) -> None:
    """Test the creation of a twin-plot."""
    x_test: Vector = linspace(1., 100., 100)
    y_test1: Vector = x_test**2
    y_test2: Vector = x_test**.5
    filename = ".test_plot.tmp.pdf"
    two_plots(x_test, y_test1, "plot1",
              x_test, y_test2, "plot2",
              "x", "y",
              tmp_path / filename)
    assert exists(tmp_path / filename)


def test_twinx_plots(tmp_path: Path) -> None:
    """Test the creation of a twin-plot."""
    x_test: Vector = linspace(1., 100., 100)
    y_test1: Vector = x_test**2
    y_test2: Vector = x_test**.5
    filename = ".test_twin_plot.tmp.pdf"
    two_axis_plots(
        x_test, y_test1, "plot1",
        x_test, y_test2, "plot2",
        "x", "y", "y2",
        tmp_path / filename)
    assert exists(tmp_path / filename)

    remove(tmp_path / filename)
    # tick-plot
    two_axis_plots(
        x_test, y_test1, "plot1",
        x_test, y_test2, "plot2",
        "x", "y", "y2",
        tmp_path / filename,
        ticks=([1., 10.], ["a", "b"]))
    assert exists(tmp_path / filename)
