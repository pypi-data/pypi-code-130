"""Methods for handling EEG data -- GT 
"""

import pandas as pd

def upsample(df, freq):
    """
    Upsampling dataframes, alternative for pd.resample method which results in less rows.
    If you resample you don't change the boundaries. You still have 4 initial values, 
    and you add as many values as there are intermediates (4 values -> 3 intermediates, 
    n values -> n-1 intermediates)

    Parameters:
    ===========
    df: pandas DataFrame with a Timedelta index or timedelta column
    freq: str
        the upsampling frequecy. E.g. '0.5S', '0.05S'

    Returns:
    ========
    upsampled dataframe

    Note: the `closed` arguent has changed to `inclusive` in pandas >=1.4
	"""

    delta = df.index[1]-df.index[0]
    idx = pd.date_range(df.index.min(),
                        df.index.max()+delta,
                        closed='left',
                        freq=freq)

    return df.reindex(idx).ffill()

def xcorr_comparision(im_exp, df1, df2, st1, st2, save=False):
    """
    Compares two cross correlation matrices.

    Parameters:
    ===========
    im_exp: lab3 ImagigExperiment object
    df1, df2: pandas DataFrames to compare
    st1, st2: str
        brain states belong to the dataframes
    save: boolean, optional

    Return:
    =======
    fig: figure object"""

    state1 = upper(df1.corr())
    state2 = upper(df2.corr())
    ecdf_state1= ECDF(state1)
    ecdf_state2 = ECDF(state2)

    fig, axs = plt.subplots(ncols=2, nrows=2, figsize=(10,8))

    corr_plot(df1, title=st1, ax=axs[0][0],
                xticklabels=False, yticklabels=False, cbar=False)
    corr_plot(df2, title=st2, ax=axs[0][1],
                xticklabels=False, yticklabels=False)

    axs[1][0].plot(ecdf_state1.x, ecdf_state1.y, label=st1)
    axs[1][0].plot(ecdf_state2.x, ecdf_state2.y, label=st2)
    axs[1][0].spines['top'].set_visible(False)
    axs[1][0].spines['right'].set_visible(False)
    axs[1][0].legend()
    axs[1][0].set_title('Cumulative Distribution of pearson r-s')

    significance_test(df1.corr(), df2.corr(), ax=axs[1][1])
    fig.suptitle('Ca activity cross correlation of significanlty upregulated cells')

    if save:
        fig.savefig(join(im_exp.sima_path,
                            f'Ca_xcorr_w_CDF_{st1}_vs_{st2}_states.png'),
                dpi=300, transparent=False, tight_layout=True)
    return fig