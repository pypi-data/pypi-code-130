import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import seaborn as sns
import base64
import typing
from typing import List, Dict, Any, Tuple
import io
import inspect
from .artemis_helper import ArtemisHelper, ArtemisType
from .artemis_config_manager import ArtemisConfigManager
'''
Available output types:
- graph
- heading
 
Required return type: Tuple

Required function format (arg, named_args)
'''

# ========================================================
# WARNING: DO NOT EDIT
def setup_plot_args(named_args):

        # Graph parameters
        xmin = None
        xmax = None
        ymin = None
        ymax = None
        figsize = (8,3)
        xlabel = ""
        ylabel = ""
        title = ""

        # Run args
        for named_arg in named_args:
            if named_arg[0] == 'xmin':
                xmin = float(named_arg[1])
            if named_arg[0] == 'xmax':
                xmax = float(named_arg[1])
            if named_arg[0] == 'ymin':
                ymin = float(named_arg[1])
            if named_arg[0] == 'ymax':
                ymax = float(named_arg[1])
            if named_arg[0] == 'xlabel':
                xlabel = named_arg[1]
            if named_arg[0] == 'ylabel':
                ylabel = named_arg[1]
            if named_arg[0] == 'title':
                title = named_arg[1]
            if named_arg[0] == 'figsize':
                figsize_input = named_arg[1].replace(')', '').replace('(', '')
                figsize_components = figsize_input.split(',')
                figsize = (float(figsize_components[0]), float(figsize_components[1]))

        # Make plot
        plt.figure(figsize=figsize)

        # Set limits
        if xmin != None:
            plt.xlim(left=xmin)
        if xmax != None:
            plt.xlim(right=xmax)
        if ymax != None:
            plt.ylim(top = ymax)
        if ymin != None:
            plt.ylim(bottom=ymin)

        # Set labels
        plt.xlabel(xlabel)
        plt.ylabel(ylabel)

        # Set title
        plt.title(title)
# ========================================================

def graph(fig, named_args : Dict) -> Tuple:

    # Validate input
    ArtemisHelper.assert_input_is_type(fig, plt.Figure)

    # Return serialized data
    return ArtemisHelper.serialize(fig, ArtemisType.MATPLOTLIB_FIGURE)

ArtemisConfigManager.register_function(graph, 'graph')

def line_graph(arr, named_args : Dict) -> Tuple:

    # Convert type to numpy array if it is a list
    arr = ArtemisHelper.convert_if(arr, ArtemisType.LIST, ArtemisType.NUMPY_ARRAY)

    # Validate input
    ArtemisHelper.assert_input_is_type(arr, np.ndarray)

    # Reshape data for line plot
    if arr.ndim == 2:
        if arr.shape[1] == 2:
            arr = arr
        elif arr.shape[0] == 2:
            arr = np.array(list(zip(arr[0], arr[1])))
        else:
            return None

    # Setup plot arguments
    setup_plot_args(named_args)

    # Actually plot data
    if arr.ndim == 1:
        plt.plot(arr)
    elif arr.ndim == 2:
        plt.plot(arr[:,0], arr[:,1])

    # Return serialized plot
    return ArtemisHelper.serialize(None, ArtemisType.MATPLOTLIB_PLOT)
ArtemisConfigManager.register_function(line_graph, 'line-graph')

def scatter_graph(arr , named_args : Dict) -> Tuple:

    # Convert type to numpy array if it is a list
    arr = ArtemisHelper.convert_if(arr, ArtemisType.LIST, ArtemisType.NUMPY_ARRAY)

    # Validate input
    ArtemisHelper.assert_input_is_type(arr, np.ndarray)

    # Setup plot arguments
    setup_plot_args(named_args)

    # Reshape data for line plot
    if arr.ndim == 2:
        if arr.shape[1] == 2:
            arr = arr
        elif arr.shape[0] == 2:
            arr = np.array(list(zip(arr[0], arr[1])))
        else:
            return None

    # Actually plot data
    if arr.ndim == 1:
        plt.scatter(arr)
    elif arr.ndim == 2:
        plt.scatter(arr[:,0], arr[:,1])

    # Return serialized plot
    return ArtemisHelper.serialize(None, ArtemisType.MATPLOTLIB_PLOT)
ArtemisConfigManager.register_function(scatter_graph, 'scatter-graph')

def histogram(arr , named_args : Dict) -> Tuple:

    # Convert type to numpy array if it is a list
    arr = ArtemisHelper.convert_if(arr, ArtemisType.LIST, ArtemisType.NUMPY_ARRAY)

    # Validate input
    ArtemisHelper.assert_input_is_type(arr, np.ndarray)

    # Actually plot data
    fig = plt.figure()
    plt.hist(arr, 50)
    out = ArtemisHelper.matplotlib_plot_to_str()

    # Return serialized plot
    return ArtemisHelper.serialize(None, ArtemisType.MATPLOTLIB_PLOT)
ArtemisConfigManager.register_function(histogram, 'histogram')

def line_graph_x_y(arr , named_args : Dict) -> Tuple:

    # Validate input is a list
    ArtemisHelper.assert_input_is_type(arr, list)

    # Pick out x and y values
    ArtemisHelper.assert_true(len(arr) == 2)

    # Unpack
    x = arr[0]
    y = arr[1]

    # Convert type to numpy arrays if lists
    x = ArtemisHelper.convert_if(x, ArtemisType.LIST, ArtemisType.NUMPY_ARRAY)
    y = ArtemisHelper.convert_if(y, ArtemisType.LIST, ArtemisType.NUMPY_ARRAY)

    # Actually plot data
    plt.figure()
    plt.title('My Title')
    plt.plot(arr[0], arr[1])

    # Return serialized plot
    return ArtemisHelper.serialize(None, ArtemisType.MATPLOTLIB_PLOT)
ArtemisConfigManager.register_function(line_graph_x_y, 'line_graph_x_y')
