import matplotlib.pyplot as plt
import seaborn as sns
import matplotlib as mpl

import  beautifulplots.beautifulplots as bp  

def lineplot(df, x, y, y2=None,  ax=None, test_mode=False, estimator=None, estimator2=None, 
             **kwargs):
    """Lineplot function designed for ease of use and aesthetics. Based on the
    Seaborn lineplot, with additions such as secondary axis, ease of use, and 
    improved default parameters. Refer to beautiful plot_defaults for full list of options.
 
    Args:
        df (Dataframe): The input DataFrame containing colums corresponding to x and y     
            
        x: Dataframe column corresponding to the lineplot x-axis
            aldfsd;lfj
        
        y: Dolumn or list of columns corresponding to the lineplot y-axis
            
        y2: Column or list of columns correspondng to the secondary axis, default = None 
        
        yaxisformat: default = "1.2f" 
        
        ycurrency: default = None. Primary y-axis. For example = "$" to prepend dollar symbol.
        
        y2currency: default = None. Secondary y-axis. For example = "$" to prepend dollar symbol.
        
        marker: default = None. Primary y-axis. Matplotlib line marker. If y is a list, then marker must be a list of markers.
        
        marker2: default = None. Secondary y-axis. Matplotlib line marker. If y2 is a list, then marker2 must be a list of markers.
        
        estimator: Specifies how to summarize data corresponding to y-axis. Defaults to plot all data points do not summarize.
        
        estimator2: Specifies how to summarize data corresponding to y2-axis. Defaults to plot all data points do not summarize.
        
        additional options:  see beautifulplot.plot_defaults for additional input variables.

    Returns:
        returns None if processing completes succesfully (without errors).
    """ 
    #***
 
    plot_options = bp.get_kwargs(**kwargs)
    
    
    # get plot_options 
    hue = plot_options['hue']
    ci2 = plot_options['ci2']
    alpha = plot_options['alpha']
    alpha2 = plot_options['alpha2']
    hue = plot_options['hue']
    palette = plot_options['palette']
    palette2 = plot_options['palette2']
    color = plot_options['color']
    color2 = plot_options['color2']
    marker = plot_options['marker']
    marker2 = plot_options['marker2']
    markers = plot_options['marker']
    markers2 = plot_options['marker2']
    linestyle = plot_options["linestyle"]
    linestyle2 = plot_options["linestyle2"]
    style = plot_options['style']
    style2 = plot_options['style2']
    ycurrency = plot_options['y_currency']
    y2currency = plot_options['y2_currency']
    ylabel = plot_options['y_axis_label']
    y2label = plot_options['y2_axis_label']
    yaxisformat = plot_options['y_axis_format']
    y2axisformat = plot_options['y2_axis_format']
    yfb = plot_options['yfb']
    yfb_color = plot_options["yfb_color"]
    yfb_alpha = plot_options["yfb_alpha"]
    
    
    # get back to the default plot options
    if ax == None: 
        mpl.rcParams.update(mpl.rcParamsDefault) # reset plot/figure parameters
        plt.style.use(plot_options['pltstyle'])
        fig,_ax = plt.subplots(nrows=1, ncols=1, figsize=plot_options['figsize']) 
    else: _ax = ax
    

    # make sure y and marker are iterable
    if isinstance(y,str): y = [y]
    if marker == None:
        if not isinstance(marker,list): marker = len(y)*[marker]
    else:
        if not isinstance(marker,list): marker =[marker]
    

    for _y,_marker in zip(y,marker):
        if plot_options['palette'] !=None:
            g = sns.lineplot(data=df,x=x, y=_y, hue=hue, palette=palette,  ax=_ax, label=_y, 
                             alpha = alpha, ci=ci2, marker=_marker, estimator=estimator,
                             markers=markers, style=style, linestyle=linestyle)
        elif plot_options['color'] !=None:
            g = sns.lineplot(data=df,x=x,y=_y, hue=hue, color=color,  ax=_ax,label=_y, 
                             alpha = alpha, marker=_marker, estimator=estimator,
                             markers=markers, style=style, linestyle=linestyle)
        else:
            g = sns.lineplot(data=df,x=x,y=_y, hue=hue, ax=_ax, label=_y,
                             alpha= alpha, marker=_marker, estimator=estimator,
                             markers=None, style=style, linestyle=linestyle)
    
    
    if yfb != None:
        yfb1 = yfb[0]
        yfb2 = yfb[1]
        _ax.fill_between(df[x], df[yfb1], df[yfb2], color = yfb_color, alpha=yfb_alpha)
    
                 #df_ml_pred["unit_sales_pred"]+df_ml_pred["error_lower"] ,
                 #df_ml_pred["unit_sales_pred"]+df_ml_pred["error_upper"] , 
                 #color="red", alpha=0.5)
            
            
    # second y_axis ... plot this first so that primary y is plotted over secondary
    if y2 != None:
        _ax2 = _ax.twinx()
        
        if isinstance(y2,str): 
            y2 = [y2]
        

        
        if marker2 == None:
            if not isinstance(marker2,list): marker2 = len(y2)*[marker2]
        else:
            if not isinstance(marker2,list): marker2 =[marker2]
            
        for _y2,_marker2 in zip(y2,marker2):
            if plot_options['palette2'] !=None:
                g = sns.lineplot(data=df,x=x, y=_y2, hue=hue, palette=palette2,  ci=ci2,
                                        ax=_ax2, label=_y2, alpha = alpha2, marker=_marker2,
                                        estimator=estimator2, markers=markers2, style=style2, linestyle=linestyle2)
            elif plot_options['color2'] !=None:
                g = sns.lineplot(data=df,x=x, y=_y2, hue=hue, color=color2,  ci=ci2,
                                        ax=_ax2,label=_y2, alpha=alpha2, marker=_marker2,
                                        estimator=estimator2, markers=markers2, style=style2, linestyle=linestyle2)
            else:
                g = sns.lineplot(data=df,x=x, y=_y2, hue=hue, ax=_ax2, label=_y2, ci=ci2,
                                        alpha=alpha2, marker=_marker2,
                                        estimator=estimator2,markers=markers2, style=style2, linestyle=linestyle2) 
                    
            _ax2.grid(visible=None)        
            
    # yaxis format
    # y axis Parameters primary axis
    
    bp.set_axisparams(plot_options,_ax,g)  # axis parameters
    bp.set_yaxis_format(_ax,yaxisformat, ycurrency)
    
    # y2 axis parameters
    if y2 != None:
        plot_options['y_axis_label']=y2label
        bp.set_axisparams(plot_options,_ax2,g)  # axis 2 parameters
        
        # set ylims after set_axis ... set_axis lims defaults to primary y axis 
        if plot_options['y_lims2'] != None:
            _ax2.set_ylim(plot_options['y_lims2'])
        
        # axis 2 legend
        handles, labels = _ax2.get_legend_handles_labels()
        if y2 != None and handles:
            _ax2.legend( loc=plot_options['legend_loc2'], prop={'size': plot_options['legend_fontsize']})

        bp.set_yaxis_format(_ax2,y2axisformat, y2currency)
        
    # plot show if easy lineplot created the figure
    if ax==None and test_mode==False: plt.show() # if simpl_plot created the figure then plt.show()
    
    return None