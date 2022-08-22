from os.path import join

import matplotlib as mpl
import matplotlib.pyplot as plt
import matplotlib.gridspec as gridspec
from matplotlib.backends.backend_pdf import PdfPages

import numpy as np
import pandas as pd
import seaborn as sns

from scipy.stats import stats
from statsmodels.distributions.empirical_distribution import ECDF


from lab3.plotting import utils 

def prep_csv(im_exp, f_name, state, direction="Upregulated"):
    """loads a csv file and returns a list of the significant cells
    
    Parameters:
    ===========
    im_exp: lab3 ImagingExperiment object
    f_name: str
        name of the csv file to load
    state: str
        brain state associated with the csv as it appears in 
        the CSV file
	direction: str, default="Upregulated"
		'Upregulated' will pull the upregulated cells,
		'Downregulated is the downregulated ones

    Return:
    =======
    ind_list: list
    	list of ROI labels

    """
    sig_cells = pd.read_csv(join(im_exp.sima_path, f_name))
    sig_cells.drop(labels='Unnamed: 0', inplace=True, axis=1)
    sig_cells.rename({'cells': 'roi_label'}, inplace=True, axis=1)
    sig_cells.set_index('roi_label', inplace=True)
    ind_list = list(sig_cells[
        (sig_cells['Direction']==direction) &
                             (sig_cells['State']=='dfof '+state)].index)
    return ind_list

def xcorr_comparison(im_exp, df1, df2, st1, st2, dtype,
					lim=None, save=False, **kwargs):
	"""
	compares two correlation matrices and uses

	Parameters:
	===========
	im_exp: lab3 ImagingExperiment object
	df1, df2: pandas DataFrame
		contains the data to be correlated
	st1, st2: string
		brain states for df1 and df2 respectively
	dtype: list of 2 str
		needed for plotting and saving. Type of the data
		being plotted (Calcium or spike), up or downregulated
		cells (up or down)
	lim: tuple of integers (max, min), optional
		the upper and lower limits of the color coding. 
	save: boolean

	Returns:
	========
	fig: pyplot figure object 
		with 4 subplots

	"""

	state1 = utils.upper(df1.corr())
	state2 = utils.upper(df2.corr())
	ecdf_state1= ECDF(state1)
	ecdf_state2 = ECDF(state2)
	if lim == None:
		vmax = np.array([state1.max(), state2.max()]).max()
		vmin = np.array([state1.min(), state2.min()]).min()		
	else:
		vmax, vmin =lim

	fig, axs = plt.subplots(ncols=2, nrows=2, figsize=(10,8))

	utils.corr_plot(df1, title=st1, ax=axs[0][0],
	         xticklabels=False, yticklabels=False, cbar=False, **kwargs)
	utils.corr_plot(df2, title=st2, ax=axs[0][1],
	         xticklabels=False, yticklabels=False, **kwargs)

	axs[1][0].plot(ecdf_state1.x, ecdf_state1.y, label=st1)
	axs[1][0].plot(ecdf_state2.x, ecdf_state2.y, label=st2)
	axs[1][0].spines['top'].set_visible(False)
	axs[1][0].spines['right'].set_visible(False)
	axs[1][0].legend()
	axs[1][0].set_title('Cumulative Distribution of pearson r-s')

	significance_test(df1.corr(), df2.corr(), ax=axs[1][1])
	fig.suptitle(f'{dtype[0]} activity cross correlation of significanlty ' \
		f'{dtype[1]}regulated cells')

	if save:
		fig.savefig(join(im_exp.sima_path,
	    			f'{dtype[0]}_xcorr_w_CDF_{st1}_vs_{st2}'\
							f'of_significantly_{dtype[1]}regulated_cells.png'),
	           dpi=300, transparent=False, tight_layout=True)
	return fig

def significance_test(m1, m2, ax=None):
	"""Nonparametric permutation testing Monte Carlo. Used to compare
	the similarities of two distribution obtained with cross correlation.

	Parameters:
	==========
	m1,m2: pandas or numpy correlation matrix
	ax: pyplot ax object

	Return:
	=======


	"""
	np.random.seed(0)
	rhos = []
	n_iter = 5000
	true_rho, _ = stats.spearmanr(utils.upper(m1), utils.upper(m2))
	# matrix permutation, shuffle the groups
	m_ids = list(m1.columns)
	m2_v = utils.upper(m2)
	for iter in range(n_iter):
		np.random.shuffle(m_ids) # shuffle list
		r, _ = stats.spearmanr(utils.upper(m1.loc[m_ids, m_ids]), m2_v)
		rhos.append(r)
	perm_p = ((np.sum(np.abs(true_rho) <= np.abs(rhos)))+1)/(n_iter+1) # two-tailed test

	if ax==None:
		f,ax = plt.subplots()
	else:
		ax=ax
	ax.hist(rhos, bins='auto')
	ax.axvline(true_rho, color = 'r', linestyle='--')
	ax.set(title=f"Spearman r: {round(true_rho, 2)}, Permuted p: {perm_p:.3f}",
	       ylabel="counts", xlabel="rho")

	return ax

def xcorr_lag(datax, datay, lag=0):
	""" Lag-N cross correlation. 

	Parameters
	==========
	datax, datay : pandas.Series objects of equal length
	lag : int, default 0    

	Returns
	=======
	crosscorr : float
	"""

	return datax.corr(datay.shift(lag))