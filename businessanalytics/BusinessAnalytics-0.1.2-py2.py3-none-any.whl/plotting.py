from typing import Union, List
from matplotlib.axes._axes import Axes as MplAxes
from matplotlib.colors import ListedColormap
import matplotlib.patches as mpatches
import matplotlib.pyplot as plt
import pandas as pd
import numpy as np 
import seaborn as sns

##  Set formatting for plotting
def _set_colors() -> None:

    ##  Set formatting for plotting
    colormap=ListedColormap(sns.color_palette("pastel", 10))
    COLORS = colormap.colors
    colors = plt.cycler(color=COLORS)
    sns.set_context('paper', font_scale=1.4)
    plt.rcParams['figure.figsize'] = [9,6]
    plt.rcParams['savefig.dpi'] = 300
    plt.rc("legend", frameon=False)
    plt.rc("axes.spines", top=False, right=False)
    plt.rcParams['axes.prop_cycle'] = colors

    return COLORS

COLORS = _set_colors()

## Define available plots

PLOTS = {} #  Dict holding registered plotting functions
def register(func):
    PLOTS.setdefault(func.__name__, func)

@register
def line(**kwargs) -> MplAxes:
    
    ax = sns.lineplot(**kwargs)
    
    return ax

@register
def bar(**kwargs) -> MplAxes:
    
    ax = sns.barplot(**kwargs)
    
    return ax

@register
def scatter(**kwargs) -> MplAxes:
    
    ax = sns.scatterplot(**kwargs)

    return ax
    
@register
def hist(**kwargs) -> MplAxes:
    
    kwargs.pop("ci")
    ax = sns.histplot(**kwargs)
    
    return ax  

@register
def violin(**kwargs) -> MplAxes:
    
    ax = sns.violinplot(**kwargs)
    return ax

@register
def box(**kwargs) -> MplAxes:
    
    kwargs.pop("ci")
    ax = sns.boxplot(**kwargs)
    
    return ax

@register
def strip(**kwargs) -> MplAxes:
    
    kwargs.pop("ci")
    ax = sns.stripplot(**kwargs)
    
    return ax

## Utility functions for handling data (_transform) and formatting plots (_format_ax)

def _transform(ys, df):
    "Transform columns into long-format (i.e. rows)"
    
    _df = df.copy()
    id_vars = _df.drop(columns=ys).columns
    _df = _df.melt(id_vars=id_vars, value_vars=ys)
    
    return _df


def _format_ax(ax, xlabel, ylabel, show_legend, colors,hue, hue_order, y, **kwargs):

    if xlabel: ax.set_xlabel(xlabel)
    if ylabel: ax.set_ylabel(ylabel)
    #if title: ax.set_title(title)
        
    legend = ax.get_legend()
    handles, labels = None, None
    if legend:
        #handles, labels = ax.get_legend_handles_labels()
        handles = legend.legendHandles # e.g. for Histogram
        legend.remove()

    if show_legend == True:
        names = hue_order if hue else [y]
        if handles and labels:
            ax.legend(handles, labels, title='',bbox_to_anchor=(1.05, 1), loc=2, borderaxespad=0. )
        else:
            # Build new legend
            if not colors: colors = COLORS[0:len(names)]
            patches = [mpatches.Patch(color=c, label=name) for name, c in zip(names, colors)]
            ax.legend(handles=patches, title='',bbox_to_anchor=(1.05, 1), loc=2, borderaxespad=0. )
        
    return ax

## Generic plot function applying specific plots available

def plot(data:pd.DataFrame, x:str, y:Union[str, List]=None, hue:str=None, plot_type:str="line", 
         size=(9,6),
         xlabel:str=None, 
         ylabel:str=None, 
         title:str=None, 
         colors:List=None, 
         show_legend:bool=True) -> MplAxes:
    '''Erstellt Graphen für angegebene Daten
    
    Input:
    - data: DataFrame, der Daten beinhaltet
    - x: Name der Spalte im DataFrame, der auf x-Achse dargestellt werden soll
    - y: Name der Spalte im DataFrame, der auf y-Achse dargestellt werden soll
    optional:
    - hue: Name der Spalte im DataFrame für die Gruppe gebildet werden soll (für z.B. groupedbar)
    - plot_type: Art des Graphen (z.B. "line" für Liniendiagramm); Default: "line"
        - "line": Liniengraph
        - "bar": Balkendiagramm
        - "scatter": Streudiagramm
        - "hist": Histogramm
        - "violin": Violindiagramm
        - "box": Boxplot
        - "strip": Stripdiagramm
    - size: Größe der Graphik (Höhe, Breite), Default: (9,6)
    - title: Überschrift für Graph
    - xlabel: Beschriftung für X-Achse
    - ylabel: Beschriftung für Y-Achse 
    - colors: Farben, die Standardfarben überschreiben sollen (z.B. ["red"] oder ["red", "green"]; auch HEX-Farben möglich)   
    - show_legend: True/False; gibt an, ob Diagramm Legende beinhalten soll
    '''

    hue_order = None
    
     # Transform data to long-form if multiple columns are passed for y. Ensure identical handling of case for multiple ys and hue
    if isinstance(y, list):
        data = _transform(y, data)
        y, hue = "value", "variable"
    
    # Define hue_order
    if hue:
        hue_order = data[hue].unique()  

    # Set up relevant key word arguments
    kwargs_plot = {"data":data, "x":x, "y":y, "hue":hue, "hue_order": hue_order, "ci":None}
    if colors:
        if len(colors) == 1 and plot_type != "bar": colors = colors[0]
    
    color_kwarg = {"palette": colors} if hue else {"color": colors}
    if plot_type == "bar": color_kwarg = {"palette": colors}
    kwargs_plot.update(color_kwarg)
    
    # Get relevant plotting function from registry
    f = PLOTS[plot_type] 
    
    # Create basic plot
    fig, ax = plt.subplots(figsize=size)
    fig.suptitle(title, fontsize=16)
    ax = f(**kwargs_plot)
    
    # Format plot
    kwargs_format = {"xlabel": xlabel, "ylabel": ylabel, "title": title, "show_legend": show_legend, "colors": colors}
    kwargs_plot.update(kwargs_format)
    
    ax = _format_ax(ax, **kwargs_plot)

    return ax