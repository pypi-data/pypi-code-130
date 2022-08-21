
import matplotlib.pyplot as plt
import seaborn as sns
from matplotlib.colors import Normalize
import matplotlib as mpl

import  beautifulplots.beautifulplots as bp  


def barplot(df, bar_columns, bar_values, barcurrency=None, barorientation="v", bardataformat="1.2f",
            y2=None,  estimator=sum, estimator2=sum,
            ax=None, bardatalabels=False, test_mode=False, bardatafontsize=14,
            **kwargs):
    """Bar plot function designed for ease of use and aesthetics. 
    The underlying barplot is ased on the Seaborn with additions, such as secondary axis, data labels,
    and improved default parameters. Refer to beautifulplots plot_defaults for a complete list of options.
    
    Args:
        df (DataFrame): The input DataFrame containing colums corresponding to bar_plot values ("bar_values") and column names (see examples in documentation)
            
        bar_columns: Datafrae columns corresponding to bar column names
            
        bar_values: Dataframe column corresponding to bar column values
            
        ax (axis): matplotlib axis (optional), default = None. If axis is None, then create a matplolib figure, axis to host the barplot
            
        color: Matplotlib compatabile color name as text or RGB values, for example,  color = [51/235,125/235,183/235].
            
        palette: Matplotlib compatible color palette name, for example, "tab20"
            
        hue: Name of hue dimension variable (i.e., DataFrame column name)
            
        ci: Seaborn confidence interval parameter: float, sd, or None, default = None
            
        barorientation: default = v (vertical), or h (horizontal)
            
        barcurrency: default = False (bar values do not represent currency). True (bar values represent currency, append $ to the value)
            
        bardatalabels (Boolean): default = False (data labels not included)
        
        estimater: default = sum. Specifies how to aggregate plot bar data.
        
        estimator2: default = None. Summarize y2 asis daa. Default is no aggregation, do not summarize y2 axis data.
        
        additional options:  see beautifulplot.plot_defaults for additional input variables.
        

    Returns:
        returns True if processing completes succesfully (without errors).
    """
        
    plot_options = bp.get_kwargs(**kwargs)
    
    ci = plot_options['ci']
    ci2 = plot_options['ci2']
    alpha = plot_options['alpha']
    alpha2 = plot_options['alpha2']
    hue = plot_options['hue']
    palette = plot_options['palette']
    palette2 = plot_options['palette2']
    marker2 = plot_options['marker2']
    marker2 = plot_options['marker2']
    markers2 = plot_options['markers']
    style2 = plot_options['style2']
    color = plot_options['color']
    color2 = plot_options['color2']
    y2label=plot_options['y2_axis_label']
    y2axisformat = plot_options['y2_axis_format']
    y2currency = plot_options['y2_currency']


    # if no hue then only one color
    # if hue == None and color==None : color = [51/235,125/235,183/235] if plot_options['color'] == None else plot_options['color']

    if barorientation == 'v': x,y = bar_columns, bar_values
    else: x,y = bar_values, bar_columns
    

    if ax == None: 
        mpl.rcParams.update(mpl.rcParamsDefault) # reset plot/figure parameters
        plt.style.use(plot_options['pltstyle'])
        fig,_ax = plt.subplots(nrows=1, ncols=1, figsize=plot_options['figsize']) 
    else: _ax = ax
        
    g=sns.barplot(x=x, y=y, hue=hue, color = color, palette=palette, data=df, ax = _ax,
                  orient=barorientation, ci=ci, estimator=estimator, alpha=alpha)
    
    # Bar labels ... iterate with hue
    # Matplotlib
      # https://matplotlib.org/stable/gallery/lines_bars_and_markers/bar_label_demo.html#sphx-glr-gallery-lines-bars-and-markers-bar-label-demo-py
      # Geeks for Geeks bar data labels
      # https://www.geeksforgeeks.org/how-to-show-values-on-seaborn-barplot/
    
    if  bardatalabels == True:
        f = bardataformat
        for i in g.containers: 
            if barcurrency!=None:
                g.bar_label(i,fontsize=bardatafontsize,labels=[f'{barcurrency}{x:{f}}' for x in i.datavalues] )
            else:
                g.bar_label(i,fontsize=bardatafontsize,labels=[f'{x:{f}}' for x in i.datavalues] )
   
    # yaxis tick label format
    # https://matplotlib.org/stable/gallery/pyplots/dollar_ticks.html
    # x or y format same as bars ... since this could be v or h graph
        #y_ticks = _ax.get_yticks()
        
    f='{x:'+ bardataformat  +'}'
    if isinstance(barcurrency,str): f= barcurrency + f
    if barorientation=='v':
        _ax.yaxis.set_major_formatter(f)
    if barorientation=='h':
        _ax.xaxis.set_major_formatter(f)
 
   # secondary y-axis
    if y2 != None:
       
        # make sure y2 and marker2 are iterable
        if not isinstance(y2,list): y2 = [y2]
        if marker2 == None:
            if not isinstance(marker2,list): marker2 = len(y2)*[marker2]
        else:
            if not isinstance(marker2,list): marker2 =[marker2]

        _ax2 = _ax.twinx()
        
        
        for _y2,_marker2 in zip(y2,marker2):
            if plot_options['palette2'] !=None:
                g = sns.lineplot(data=df,x=x, y =_y2, hue=hue, palette=palette2,  ax=_ax2, label=_y2, 
                                 alpha = alpha2,ci = ci2, marker=_marker2, estimator=estimator2,
                                 markers=markers2, style=style2)
            elif plot_options['color2'] !=None:
                g = sns.lineplot(data=df,x=x, y=_y2, hue=hue, color=color2,  ax=_ax2,label=_y2, 
                                 alpha=alpha2, ci=ci2, marker=_marker2, estimator=estimator2,
                                 markers=markers2, style=style2)
            else:
                g = sns.lineplot(data=df,x=x, y=_y2, hue=hue, ax=_ax2, label=_y2, 
                                 alpha=alpha2, ci=ci2, marker=_marker2, estimator=estimator2,
                                 markers=markers2, style=style2) 
                
        _ax2.grid(visible=None)  
    
    # set axis params
    bp.set_axisparams(plot_options,_ax,g)  # axis parameters from the plot_options dictionary
    
    # y2 axis params
    if y2 != None:
        plot_options["y_label"]=y2label
        bp.set_axisparams(plot_options,_ax2,g)  # axis parameters
    
        # set ylims 2 after general axis parameters 
        if plot_options['y_lims2'] != None:
            _ax2.set_ylim(plot_options['y_lims2'])
        
        # axis 2 legend
        handles, labels = _ax2.get_legend_handles_labels()
        if y2 != None and handles==True:
            _ax2.legend( loc=plot_options['legend_loc2'], prop={'size': plot_options['legend_size']})
            
        bp.set_yaxis_format(_ax2,y2axisformat, y2currency)
    

    if ax==None and test_mode==False: plt.show() # if barplot created the figure then plt.show()
    
    return None