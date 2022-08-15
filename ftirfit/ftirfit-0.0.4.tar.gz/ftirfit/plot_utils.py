import matplotlib.pyplot as plt

def plot_spectral_corrections(data,cor_spectra,bdata,roi):
    '''A grid plot describing the baseline corrections, with polynomial fits in respect to the original spectra.

    Paramaeters
    -----------
    data : Pandas DataFrame 
        The original dataframe of the raw data loaded
    cor_spectra : Pandas DataFrame
        Corrected spectra after baseline correction
    bdata : Pandas DataFrame
        The baseline obtained with the desired polynomial degree obtained for each spectra        

    Returns
    -----------
    plt : matplotlib.pyplot.plot object 
    '''

    f = plt.figure('Spectral Corrections',figsize=(16,12))
    for i,cols in enumerate(data.columns):
        if cols != 'x' :   
            plt.subplot(6,5,i)
            plt.plot(data['x'],bdata[cols], label='Baseline')
            plt.plot(data['x'],cor_spectra[cols],'r-.' ,label='Corrected')
            plt.plot(data['x'],data[cols],'k:' ,label='Original')
            plt.xlim(roi[0,0],roi[1,1])
            y_max = data[cols].max()
            # print(y_max)
            plt.ylim(-0.1,y_max)
            plt.title(cols,loc = 'right', fontweight = 'bold')
            plt.hlines(y= 0,xmin= roi[0,0], xmax= roi[1,1], color='grey', linestyle ='dashed', linewidth = 1.5)
            plt.gca().invert_xaxis()
            plt.gca().sharex = True
            plt.gca().sharey = True
            plt.gca().set_xlabel = 'Frequency, cm$^{-1}$'
        plt.figlegend(['Baseline', 'Corrected', 'Original'])  
    plt.tight_layout()
    # plt.show()
    return plt

def plot_norm_signals(normSpectra):
    f = plt.figure('Normalized Signal',figsize=(16,12))
    for s,cols in enumerate(normSpectra.columns):
        if cols != 'x' :   
            plt.subplot(6,5,s)
            plt.plot(normSpectra['x'],normSpectra[cols], label=cols)
            plt.ylim(-0.1,1.01)
            plt.title('Norm Signal_'+cols)
            plt.hlines(y= 0, xmin = normSpectra['x'].iloc[0], xmax = normSpectra['x'].iloc[-1], color='grey', linestyle ='dashed', linewidth = 1.5)
            plt.gca().invert_xaxis()   
    
    plt.tight_layout()
    return plt


def plot_fitres(ready_to_plot_df,x_fit,ratio={}):
    '''
    Creates plot of the peaks from the residual dataframe created

    Parameters
    -----------
    ready_to_plot_df : DataFrame
        Consits of the results obtained from the multirunfit
    x_fit : Pandas.series
        X axis 
    ratio : Dictionary
        ratio of protein/lipid calculated 
    Returns
    -----------
    plt : plot

    '''
    # Check the column naming and append based on it
    if isinstance(ready_to_plot_df.columns[0], int):
        ready_to_plot_df = ready_to_plot_df.add_prefix('Peak_')
    # Finding the unique indices 
    ui = ready_to_plot_df.index.unique()

    plt.figure('Fit',figsize=(16,14))
    for i,sp in enumerate(ui):
        sel_df = ready_to_plot_df.loc[sp]
        sel_df.index = x_fit
        plt.subplot(6,5,i+1)
        plt.plot(sel_df)
        if len(ratio) == 0:
            plt.title(sp)
        else:
            plt.title(sp+" P/L ratio: "+ str(round(ratio[sp],3)))
        plt.gca().get_lines()[0].set_color("tab:blue")
        plt.gca().get_lines()[1].set_color("tab:orange")
        plt.gca().get_lines()[0].set_linestyle('-.')
        plt.gca().get_lines()[0].set_linewidth(3.5)
        plt.gca().get_lines()[1].set_linewidth(3.5)
        plt.gca().invert_xaxis()
    
        col_names = ['Data', 'Fit']
        for dd,_ in enumerate(ready_to_plot_df.columns):
            if dd > 1:
                n = dd-1
                col_names.append('Peak_' + str(n))
    plt.figlegend(col_names, loc='lower right', ncol = len(col_names)) 
    plt.tight_layout()
    return plt

    
def plot_residuals(df_residual,df_stats):

    plt.figure('Residuals',figsize=(16,14))
    for i,col in enumerate(df_residual.columns):
        if col!='x' :
            plt.subplot(6,5,i)
            plt.plot(df_residual['x'],df_residual[col],'k')
            plt.gca().invert_xaxis()
            chi = round(df_stats.loc[col]['chisqr'],3)
            plt.title(col+' Chisqr:'+str(chi))
            plt.hlines(y= 0,xmin= 1300, xmax= 1800, color='grey', linestyle ='dashed', linewidth = 1.5)
            # plt.xlabel("Frequency, cm$^{-1}$")
            # plt.ylabel("Residuals")
            # plt.rcParams.update({'font.size': 16})
        plt.figlegend(['Residuals'], framealpha=0.5, loc='lower right') 
        plt.tight_layout()
    return plt

# SMALL_SIZE = 8
# MEDIUM_SIZE = 10
# BIGGER_SIZE = 12

# plt.rc('font', size=SMALL_SIZE)          # controls default text sizes
# plt.rc('axes', titlesize=SMALL_SIZE)     # fontsize of the axes title
# plt.rc('axes', labelsize=MEDIUM_SIZE)    # fontsize of the x and y labels
# plt.rc('xtick', labelsize=SMALL_SIZE)    # fontsize of the tick labels
# plt.rc('ytick', labelsize=SMALL_SIZE)    # fontsize of the tick labels
# plt.rc('legend', fontsize=SMALL_SIZE)    # legend fontsize
# plt.rc('figure', titlesize=BIGGER_SIZE)  # fontsize of the figure title
