import rampy as rp
import matplotlib.pyplot as plt
import pandas as pd
from scipy.integrate import trapezoid
import os
import numpy as np
import lmfit
import pybroom as br

def residual(pars, x, data=None, eps=None): #Function definition
    # unpack parameters, extract .value attribute for each parameter
    a1 = pars['a1'].value
    a2 = pars['a2'].value
    a3 = pars['a3'].value
    a4 = pars['a4'].value
    a5 = pars['a5'].value
    a6 = pars['a6'].value
    a7 = pars['a7'].value
    
    f1 = pars['f1'].value
    f2 = pars['f2'].value
    f3 = pars['f3'].value
    f4 = pars['f4'].value
    f5 = pars['f5'].value 
    f6 = pars['f6'].value
    f7 = pars['f7'].value
    
    l1 = pars['l1'].value
    l2 = pars['l2'].value
    l3 = pars['l3'].value
    l4 = pars['l4'].value
    l5 = pars['l5'].value
    l6 = pars['l6'].value
    l7 = pars['l7'].value
    
    
    # Using the Gaussian model function from rampy
    # peak1 = rp.lorentzian(x,a1,f1,l1)
    # peak2 = rp.lorentzian(x,a2,f2,l2)
    # peak3 = rp.lorentzian(x,a3,f3,l3)
    # peak4 = rp.lorentzian(x,a4,f4,l4)
    # peak5 = rp.lorentzian(x,a5,f5,l5)
    # peak6 = rp.lorentzian(x,a6,f6,l6)
    # peak7 = rp.lorentzian(x,a7,f7,l7)
    #  chi-square         = 0.23088034
    # reduced chi-square = 2.5123e-04
    # peak1 = rp.pseudovoigt(x,a1,f1,l1,0)
    # peak2 = rp.pseudovoigt(x,a2,f2,l2,0)
    # peak3 = rp.pseudovoigt(x,a3,f3,l3,0.2)
    # peak4 = rp.pseudovoigt(x,a4,f4,l4,0.2)
    # peak5 = rp.pseudovoigt(x,a5,f5,l5,0)
    # peak6 = rp.pseudovoigt(x,a6,f6,l6,0.1)
    # peak7 = rp.pseudovoigt(x,a7,f7,l7,0)

    # peak1 = rp.pseudovoigt(x,a1,f1,l1,0)
    # peak2 = rp.pseudovoigt(x,a2,f2,l2,0)
    # peak3 = rp.pseudovoigt(x,a3,f3,l3,0.2)
    # peak4 = rp.pseudovoigt(x,a4,f4,l4,0.2)
    # peak5 = rp.pseudovoigt(x,a5,f5,l5,0)
    # peak6 = rp.pseudovoigt(x,a6,f6,l6,0)
    # peak7 = rp.pseudovoigt(x,a7,f7,l7,0)
    
    peak1 = rp.pseudovoigt(x,a1,f1,l1,0)
    peak2 = rp.pseudovoigt(x,a2,f2,l2,0)
    peak3 = rp.pseudovoigt(x,a3,f3,l3,0.2)
    peak4 = rp.pseudovoigt(x,a4,f4,l4,0.2)
    peak5 = rp.pseudovoigt(x,a5,f5,l5,0)
    peak6 = rp.pseudovoigt(x,a6,f6,l6,0.1)
    peak7 = rp.pseudovoigt(x,a7,f7,l7,0)


    model = peak1 + peak2 + peak3 + peak4 + peak5 + peak6 + peak7 # The global model is the sum of the Gaussian peaks
    
    if data is None: # if we don't have data, the function only returns the direct calculation
        return model, peak1, peak2, peak3, peak4, peak5, peak6, peak7
    if eps is None: # without errors, no ponderation
        return (model - data)
    return (model - data)/eps # with errors, the difference is ponderated





def protein_to_lipid(df,x_fit):
    '''
    Implementation completely based on experimental work.
    Protein to lipid ratio based on the area under the peak.
    Taking into accound of the 1st 4 fitted peaks. 
    The first two is coming from lipids and next two from proteins.

    Parameters
    -----------
    df - DataFrame
        With different fitted peaks. First two columns are data and fitted peaks.
    x_fit - DataFrame series
        x axis used in trapezoid calculation

    Returns
    -----------
    ratio : Dictionary
        Keys are the experiment temparature and values are the Protein to Lipid ratio    

    '''
    if isinstance(df.columns[0], int):
            new_df = df.add_prefix('Peak_')

    ratio_l =[]
    ui = new_df.index.unique()
    for i,sp in enumerate(ui):
        sel_df = new_df.loc[sp]
        trap_1 = trapezoid(sel_df['Peak_2'],x_fit)
        trap_2 = trapezoid(sel_df['Peak_3'],x_fit) 
        lipid_trap = trap_1+trap_2
        trap_3 = trapezoid(sel_df['Peak_4'],x_fit)
        trap_4 = trapezoid(sel_df['Peak_5'],x_fit) 
        protein_trap = trap_3 + trap_4
        r = protein_trap/lipid_trap
        ratio_l.append(r)

    ratio = dict(zip(ui, ratio_l))

    return ratio 



def load_files(dir_name):
    '''
    Load all files from the directory path
    The dataframe output and column naming is based on the temparature.
    With index as the x axis or Frequency
    '''
    init_temp = 10
    c = 0
    all_data = pd.DataFrame()
    for file in os.listdir(dir_name):
        filename = file
        if '_XY' or 'XY' in filename:
            full_file = os.path.join(dir_name,filename)
            # print(file_num)
            data_temp = init_temp+c
            # print(filename + ' : '+str(data_temp))
            c += 3 
            colx = "x_"+str(data_temp)
            coly = "y_"+str(data_temp)
            col_nam = [colx , coly]
            data = pd.read_csv(full_file, delimiter = "\t", names = col_nam)
            all_data = pd.concat([all_data,data[coly]], axis=1)
            
    all_data = pd.concat([data[colx], all_data], axis=1)    
    all_data = all_data.rename(columns = {colx:'x'})
    return all_data

def correct_spectra(data,roi,pol_order = 3):
    '''
    Performs background correction - baseline subtraction and data trimming.
    Parameters
    -----------
    data : Dataframe
        The raw data/spectra obtained from the loaded files
    roi : np array -> Usage : roi = np.array([(1347,1365),(1774,1800)])
        The region of interest, used for polynomial fit of the spectra
    pol_order : Integer
        Uses polynomial function for baseline correction of the spectra
        rampy.baseline() module used, refer to Rampy python package
    
    Returns
    -----------
    data_corr_trim : DataFrame
        Trimmed spectra
    data_corr : DataFrame
        Corrected spectra(but not trimmed) hence can be used for comparing with raw spectra 
    data_base : DataFrame
        Baseline obtained for each spectra

    This function is later used for plotting and comparasion with raw data.
    Refer to plot_utils.plot_spectral_corrections()

    Usage
    ------    
    trim_data,cor_spectra,bdata = correct_spectra(data,roi,pol_order = 3)
    '''
    # Get the x axis as nump
    x = data['x'].to_numpy()
    # Initialize the dataframe to concat later
    data_corr_trim = pd.DataFrame()
    data_base = pd.DataFrame()
    data_corr = pd.DataFrame()
    # Already merge the x axis except in case of data-trim since length it will alter
    data_corr = pd.concat([data_corr,data['x']], axis = 1)
    data_base = pd.concat([data_base,data['x']], axis = 1)
    for col in data.columns:
        if col != 'x':
            y = data[col].to_numpy()            
            y_corr, y_base = rp.baseline(x,y,roi,'poly',polynomial_order = pol_order)        
            # Merging to the dataframe
            data_corr = pd.concat([data_corr,pd.DataFrame(y_corr,columns=[col])], axis=1)
            data_base = pd.concat([data_base,pd.DataFrame(y_base,columns=[col])], axis=1)
            # Trimming / Correction 
            x_fit = pd.DataFrame(x[np.where((x > roi[0,0])&(x < roi[1,1]))], columns= ['x'])
            y_fit = pd.DataFrame(y_corr[np.where((x > roi[0,0])&(x < roi[1,1]))],columns=[col])
            # Add the y_fit to the dataframe
            data_corr_trim = pd.concat([data_corr_trim,y_fit],axis = 1)
    # Add the x-axis to the dataframe
    data_corr_trim = pd.concat([x_fit,data_corr_trim], axis = 1)
    return data_corr_trim, data_corr, data_base


def norm_spectra(data_corr_trim,method_type = "intensity"):
    '''
    Perform normalization on the trimmed data/spectra.

    Parameters
    ----------
    data_corr_trim : DataFrame
        The corretcted and trimmed dataframe. Refer to correct_spectra(data,roi,pol_order = 3) 
    method_type : Str
        Type of method to normalize spectra. Using Rampy package. rp.normalise()
        Refer to rampy package for more types
    
    '''
    data_norm = pd.DataFrame()
    for col_name in data_corr_trim.columns:
        if col_name != 'x':
            y_fit_norm_intensity = pd.DataFrame(rp.normalise(data_corr_trim[col_name],x = data_corr_trim['x'],method = method_type))
            data_norm = pd.concat([data_norm,y_fit_norm_intensity],axis = 1)   
    data_norm = pd.concat([data_corr_trim['x'],data_norm],axis = 1)            
    return data_norm

def run_multifit(normSpectra,params, algo = 'leastsq', message = True):
    '''
    Run fit along the stored spectra simultaneously.

    Parameters
    -----------
    normSpectra : DataFrame
        The normalized spectra which will be used for running the lmfit
    params : lmfit.Parameters
        Requires to be initialized as a script
    algo : Str
        By default - "leastsq" method is used,Algorithim which lmfit will use to fit 
    message : Boolean
        If True, a message will be printed on the progress
    
    Return
    ----------
    df_stats : DataFrame
        Consisiting of the lmfit report statistics, such as Chi Square, nev etc
    df_variables : DataFrame
        All the fitting variables , row wise accesible for each spectra, using loc argument 
    df_residuals : DataFrames
        Residuals are stored as columns for each spectra
    df_ready_to_plot : DataFrames
        Fitted Peaks from the objective function.
        The first two columns are Data and Model/Fit (Sum of Peaks)
        Rest columns are fitted peaks with number of components    
    '''
    # Initialize storing DataFrames
    df_stats = pd.DataFrame()
    df_variables = pd.DataFrame()
    df_residual = pd.DataFrame()
    df_ready_to_plot = pd.DataFrame()
    df_residual = pd.concat([df_residual,normSpectra['x']],axis = 1) 

    for cols in normSpectra:  
        if cols!='x':
            
            # Assigining x and y axis to work for fits
            x_fit = normSpectra['x']
            y_fit = normSpectra[cols]
            
            # Running individual fit
            result = lmfit.minimize(residual, params, method = algo, args=(x_fit,y_fit))
            
            ##----- IMPORTANT -------###
            # It Changes based on the total no of peaks/components
            sum_peak, peak1,peak2,peak3,peak4,peak5,peak6, peak7 = residual(result.params,x_fit)
            res_stack = np.column_stack((np.array(y_fit),sum_peak,peak1,peak2,peak3,peak4,peak5,peak6,peak7))
            # Convert to DataFrame
            res_df = pd.DataFrame(res_stack)  
            len_res_df = len(res_df)
            res_df.index = [cols]*len_res_df # Adding index for unique ID
            
            stat_glance = br.glance(result)
            stat_glance.index = [cols]

            dt = br.tidy(result)
            nl = len(dt)
            dt.index = [cols]*nl # Adding index for unique ID

            
            df_ready_to_plot = pd.concat([df_ready_to_plot,res_df], axis = 0)
            # df_ready_to_plot = df_ready_to_plot.add_prefix('Peak_')
            df_variables = pd.concat([df_variables,dt])
            df_stats = pd.concat([df_stats,stat_glance])
            df_residual = pd.concat([df_residual,pd.DataFrame(result.residual,columns=[cols])],axis = 1) 
    
            if message is True:
                print("Spectra(Y) at temp." + cols +"..completed with stats:"
                + "[Chisqr value]:"+str(stat_glance['chisqr'])+" ,[reduced_Chi] value: "+ str(stat_glance['redchi'])
                + " ,[Number of evaluation]:"+str(stat_glance['num_func_eval'])
                + ",LMFIT message"+str(stat_glance['message'])+str(stat_glance['success'])
                )

    return df_stats, df_variables, df_residual, df_ready_to_plot 
