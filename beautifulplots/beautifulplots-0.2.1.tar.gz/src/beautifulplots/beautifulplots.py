
import matplotlib.pyplot as plt
import seaborn as sns
from matplotlib.colors import Normalize
from matplotlib.cbook import boxplot_stats
import matplotlib as mpl 


def plot_defaults():
    """Dictionary of plot parameters. Each parameter coresponds and corresponding value. 
    See also get_plot_options for extracting plot options from **kwargs. 

    **Axis - x, y, and plot area parameters**
    
    Args:
        df (DataFrame): The input DataFrame containing colums corresponding to bar values and columns.
 
        title (String): corresponds to the axis title. default = ''
            
        title_fontsize: font size of the axis title, default = 18
         
        x_lims: (xmin, xmax), minimum and maximum x-values of the axis. default = None, in which case the min and max are set automatically by matplotlib.
        
        y_lims: (ymin,ymax), minimum and maximum y-values of the axis. default = None, in which case the min and max are set automatically by matplotlib.
        
        y2_lims: (ymin,ymax), minimum and maximum y-values of the secondary axis. default = None, in which case the min and max are set automatically by matplotlib.
        
        x_label_fontsize: default = 16
        
        x_tick_labelsize: default = 16
        
        x_tick_fontsize: default = 16
        
        x_tick_rotation: default = 0
        
        y_label_fontsize: ylabel font size, default = 16
            
        y_tick_fontsize: xtick label font size, default = 16
        
        y_tick_rotation:  Rotation of the xtick label, default = 0
        

        
    **Plot attributes - Line, Bar, Scatter Plots**
    
    Args:
        
        marker: Matplotlib line markers. default = None (Matplotlib default).
            
        marker2: Secondary axis, Matplotlib line marker. default = None (Matplotlib default).
        
        marker: sns line markers. default = None (sns default).
            
        marker2: Secondary axis, sns line markers. default = None (sns default).
            
        y_axis_currency (Boolean): Boolean default = False.
            
        y_tick_format (String): String default = None (Matplotlib default).
            
        alpha (fraction): Trasnparancy (opacity), default = None (not transparent)
            
        alpha2 (fraction): Secondary axis, default = 0.5, 50% opacity
        
        legend_labels (list): Overide default legend labels. default = None (do not override)
        
        legend_loc(String): Matplotlib legend location, for example, upper right , default = "best".
        
        legend_loc2 (String): Secondary axis legend location, for example, upper right , default = best.
        
        legend_fontsize: legend font size, default = 16
        
        estimator: seaborn barplot summary estimator, default = sum
            
        estimator2: secondary axis, seaborn barplot summary estimator, default = sum
            
        color: default = None, indicateing Matplolib default (Matplotlib default)
            
        color2: secondary axis line, bar or color. defualt = None (Matplotlib default)
            
        palette: colormap, default = None
            
        palette2: colormap, default = None, secondary y axis.
            
        hue: dimension value for corresponding Seaborn graphs, default = None.
        
        ci: Seaborn confidence interval parameter: float, sd, or None
            
        ci2: Seaborn confidence interval parameter second y axis: float, sd, or None
            
        x_label (String): xlabel title, default = ''
            
        y_label (String):  y lable title, default = ''
        
        h_line (int):  y-value, corresponding to horizontal line, default = None
                
        h_line_label (String):  y value, corresponding to horizontal line, default = None
        
        v_line (int):  x-value, corresponding to vertical line, default = None (no line)
        
        v_line_label (String):  x value, corresponding to vertical line, default = None (no line)

        y_scale (String): scale for the y-axis (e.g., yscale = "log"), default = None (default is linear)
        
        x_scale (String): scale for the x-axis (e.g., xscale = "log"), default = None (default is linear)
     
    **Plots and subplots**
    
    Parameters corresponding to the plot or subplot characteristics. They are used when matplot_helpers
    functions create the plot figure and axis, otherewise, these parameters do not affect the plot.
    
    Args:
    
        plot_style (String): matplotlib plot style
            
        fig_size: total size (height, width) in inches of the figure, including total plotting area of all subplots and spacing
        
        w_space: width space (horizontal) between subplots, default wspace = 0.2
        
        h_space: height space (vertical) between subplots, default hspace = 0.2
        
    **Annotations**
    
    Args:
        annotate (List of Strings and positions): default = None.  List of Strings with corresponding (x,y) positions.
        
        annotate_fontsize (int): default = 16. Fontsize for each annotation.
            
    **Returns**
    
        Dictionary: {parameter1:value1, parameter2:value2, ... }. 
        Pairs of plat parameters and corresponding values.
    """    

    plot_defaults = {
        
    # axis, plot and subplot
    'pltstyle': 'seaborn',
    'figsize' : None,
    'w_space': 0.2,
    'h_space': 0.2,
    'share_x':False,
    'title' :None,               #  list ot titles, 1 per axis  #  list of x,y tuples
    'y_lims' :None,               # list of two-tuples ylims (lower, upper)
    'x_lims' :None,
    'y_lims2':None,
    "yfb": None,
    "yfb_color": "red",
    "yfb_alpha": 0.5,
    'y_currency':None,
    'y2_currency':None,
    'y_axis_format':"1.2f",
    'y2_axis_format':"1.2f",
    'x_label_fontsize':16,
    'x_tick_labelsize':16,
    'x_tick_fontsize': 16,
    'x_tick_rotation':0,
    'y_label_fontsize':16,
    'y_tick_fontsize':16,
    'y_tick_rotation':0,
    'title_fontsize':18,
    'legend':True,
    'legend_labels':None,
    'legend_loc':'best',
    'legend_loc2':'best',
    'legend_fontsize':16,
    'x_axis_label': None,
    'y_axis_label': None,
    'y2_axis_label': None,
    'marker':None,
    'marker2':None,
    'markers':None,
    'markers2':None,
    "linestyle":"-",
    "linestyle2":"-",
    'style':None,
    'style2':None,
    'color':None,   # color designation for the corresponding graph
    'color2':None,   # color secondary y axis
    'palette':None,  
    'palette2':None,  # palette secondary y axis
    'hue':None,   # dimensional value for corresponding Seaborn graphs
    'ci':None, # confidence parameter for pimary axis
    'ci2': None, # confidence parameter for secondary axis


    # Lines, bar, and Scatter plots
    'ytick_format': None,
    'alpha': None,
    'alpha2': 0.5,
    'estimator':"sum",
    'estimator2':"sum",
    'h_line':None,
    "v_line":None,
    "h_line_label": None,
    "v_line_label": None,
    "y_scale":None,
    "x_scale":None,
    
    
    # annotations
    "annotate":None,
    "annotate_fontsize":16

    }

    return plot_defaults

def set_axisparams(options_dict,ax,g): 
    """Receives as input a dictionary of plot options and applies the options to the maxtplotlib axis and graph.

    Args:
        options_dict (dictionary): dictionar containint plot options. Each key, value pair corresponds to a plot parameter
        ax (axis): matplotlib axis to apply the plot options
        g (graph): matplotlib graph to apply the plot options

    Returns:
        None: returns None if the function completes without errors.
    """ 
    from beautifulplots import beautifulplots as bp 
    
    annotate=options_dict['annotate']
    annotate_fontsize=options_dict['annotate_fontsize']
    title=options_dict['title']
    title_fontsize=options_dict['title_fontsize']
    legend=options_dict['legend']
    legendloc=options_dict['legend_loc']
    legendfontsize=options_dict['legend_fontsize']
    xlabel=options_dict['x_axis_label']
    xlabelfontsize=options_dict['x_label_fontsize']
    xlims=options_dict['x_lims']
    xtickfontsize=options_dict['x_tick_fontsize']
    xtickrotation=options_dict['x_tick_rotation']
    ylabel=options_dict['y_axis_label']
    ylabelfontsize=options_dict['y_label_fontsize']
    ytickfontsize=options_dict['y_tick_fontsize']
    ytickrotation=options_dict['y_tick_rotation']
    ylims=options_dict['y_lims']
    hline=options_dict['h_line']
    vline=options_dict['v_line']
    hline_label=options_dict['h_line_label']
    vline_label=options_dict['v_line_label']
    yscale=options_dict['y_scale']
    xscale=options_dict['x_scale']
    
    ax.set_xlabel(xlabel,fontsize=xlabelfontsize)
    ax.set_ylabel(ylabel,fontsize=ylabelfontsize)

    for x_tick in ax.get_xticklabels():
        x_tick.set_fontsize(xtickfontsize)
        x_tick.set_rotation(xtickrotation)

    for y_tick in ax.get_yticklabels():
        y_tick.set_fontsize(ytickfontsize)
        y_tick.set_rotation(ytickrotation)


    ax.set_title(title, fontsize=title_fontsize)

    if ylims != None:
        ax.set_ylim(ylims[0],ylims[1])

    if xlims != None:
        ax.set_xlim(xlims[0],xlims[1])

    # if legend then set fontsize ... otherwise get warning

    
    handles, labels = ax.get_legend_handles_labels()
    if handles: 
        ax.legend().set_visible(legend)
    if handles and legend == True: 
        if legend == True: ax.legend( loc=legendloc, prop={'size': legendfontsize})     
        
    # horizontal line(s)
    if hline != None:
        ax.axhline(y=hline, xmin=0.0, label=hline_label, xmax=1.0, color='k',lw=1)
        
    if vline != None:
        ax.axvline(x=vline, ymin=0.0, ymax=1.0, label=vline_label, color='k',lw=1)
        
    if yscale == "log":
        g.set(yscale="log")
        
    if xscale == "log":
        g.set(xscale="log")
        
    if annotate != None:
        for a in annotate: 
            ax.annotate(a[0],xy=a[1], fontsize=annotate_fontsize)
    
    # vertical line(s)

    return None

def get_kwargs(**kwargs):   
    """process **kwargs options corresponding to the plot_defaults dictionary (see above)
    If a beautifulplots plot_option dictionary key is 
    contained in the **kwargs then the plot_defautls[key] value is replaced 
    with that found in **kwargs. 

    Returns:
        Dictionary: {parameter1:value1, parameter2:value2, ...} dictionary corresponding to plot options 
    """   
       
    plot_options = plot_defaults() # returns a dictionary of defaut matplotlib parameters

    # interate through the parameters in the plot_options dictionary
    # find the key in the kwargs, otherwise the paremeer = default
    # if the kwargs parameter != default then update plot_options
    for key in plot_options:
        default = plot_options[key]
        kwarg_value = kwargs.get(key, default) # parameter = kwarg  or default
        if kwarg_value != default: plot_options[key] = kwarg_value # update plot_option 
        
    return plot_options


def set_yaxis_format(ax,yaxisformat="1.2f", ycurrency=None, labelcolor='black', which='major'):
    
    # https://matplotlib.org/stable/gallery/pyplots/dollar_ticks.html
    # Use automatic StrMethodFormatter

    
    f='{x:'+ yaxisformat  +'}'
    if ycurrency !=None: f = ycurrency + f
    ax.yaxis.set_major_formatter(f)
    ax.yaxis.set_tick_params(which=which, labelcolor=labelcolor)
    
    return None