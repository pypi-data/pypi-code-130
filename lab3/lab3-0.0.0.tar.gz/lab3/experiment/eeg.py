"""
analysis scripts written by Gergo
contact: gt2253@cumc.columbia.edu
5/9/2022
5/26/2022 -- moved to lab3/experiment/"""

from dataclasses import dataclass

from os.path import join
import collections

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
# import dabest  # need to install this dependency!


@dataclass

class sleep:
    pass

    # imaging: str
    # eeg: str
    # eeg_folder: im_exp.sima_path+'/eeg'


def calc_ci(x, ci=0.95, bootstrap=1000, decimals=5):
    """calculates the 95 percent confidence interval of an array

    Parameters:
    ===========
    x: numpy.array
        or something in array format
    ci: float, optional
        confidence interval to calcualte
    bootstrap: int, optional
        number of bootstrap resampling
    round: int, optional
        how many decimals should be rounded
        
    Returns:
    ========
    tuple 
        upper and lower confidence interval values rounded to 4 digits"""
    
    confidence = ci
    
    values = [np.random.choice(x,size=len(x),
                               replace=True).mean() for i in range(bootstrap)]
    up, low = np.percentile(values, [100*(1-confidence)/2,
                       100*(1-(1-confidence)/2)])
    
    return up.round(decimals), low.round(decimals)

def ci_difference(awake_arr, nrem_arr, resamples=5000):
    """ 
    uses estimation stats to evaluate the difference between two sets
    of numbers. The documentation can be found here:
    https://acclab.github.io/DABEST-python-docs/tutorial.html
    
    Parameters:
    ===========
    awake_arr: numpy array
        compied dfof of awake periods
    nrem_arr: numpy array
        compiled dfof of NREM periods
    resamples: int
        number of resamples to generate the effect size bootstrap
        
    Returns:
    ========
    tuple
    difference: float
        this is the Cohen D effect size between the two arrays
    significance: float
        the p value for the (unpaired) student test 
    """

    dabest_dict = {'awake': awake_arr, 'nrem': nrem_arr}
    dabest_df= pd.DataFrame.from_dict(dabest_dict, orient='index')
    dabest_df = dabest_df.transpose()

    # calculating the stats
    two_groups_unpaired = dabest.load(dabest_df, idx=("awake", "nrem"),
                                      resamples=resamples)
    stats = two_groups_unpaired.cohens_d
    significance =stats.results['pvalue_students_t'][0] < 0.05
    difference = stats.results['difference'][0]

    return (difference, significance)


def converter(series, state):
    """converts a series to a dataframe. This was used for creating a
    boolean column for brain states 

    Parameters:
    ===========
    series: pandas.Series
    state: list 
    """
    df = series.reset_index()
    df.set_index(['cells'], inplace=True)
    df.rename(columns={'dfof': 'dfof_'+state}, inplace=True)
    result_df = df[df[state]==True]    
    return result_df.drop(labels=state, axis=1)

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

def sub(a,b):
    """
    Subtracts two tuples from each other
    Params:
    =======
    a, b: tuple 
    Returns:
    ========
    tuple
    """
    return tuple(map(lambda x, y: x-y, a,b))

def overlap_test(tuple1, tuple2):
    """ 
    Checks whether the items in tuple2 are within the range of tuple1. Used to
    check whether confidece intervals overlap.
    
    Paramaters:
    ===========
    tuple1, tuple2: tuple, list
        with 2 items in each
    Return:
    =======
    True: if the item1 or item2 is between the numbers of tuple1
    False: if the item1 or item2 is NOT between the numbers of tuple1
    """
    return ((tuple1[0]<= tuple2[0] <=tuple1[1]) or
            (tuple1[0]<= tuple2[1] <=tuple1[1]))

def transient_freq_count(df, state, state_frames):
    """
    counts transient frequency. 

    df: pandas DataFrame
        must have 'roi_labels','onset' and 'state: ' columns
        >>> expt_transients = im_exp.events(signal_type='imaging',
                                event_type='transients',
                                channel='Ch2',
                                label='suite2p')
        >>> trans = expt_transients.dataframe

    state: str
        usually it's in 'state:NREM' format
    state_frames: int
        number of frames for the given state

    Return:
    =======
    freq_df: pandas DataFrame
        
    """
    freq_df = df[df[state]].groupby('roi_label')['onset'].count().reset_index()
    freq_df['frames'] = state_frames
    freq_df['State'] = state
    freq_df['Freq (event/sec)'] = state_frames
    freq_df['Freq (event/sec)'] = freq_df['onset'] / freq_df['frames']
    return freq_df

def import_eeg(imaging_exp, eeg_file):
    """
    imports scored eeg data from a csv file. The file should be located
    in a subfolder named 'eeg' within the sima folder
    
    Parameters:
    ===========
    imaging_exp: ImagingExperiment object
    eeg_file: str
        imagaging file name
    Return:
    ======
    eeg_df: pandas DataFrame
    
    """
    eeg_data_path = imaging_exp.sima_path+"/eeg/"+eeg_file
    eeg_df = pd.read_csv(eeg_data_path, names=['time', 'eeg'])
    eeg_df['eeg'] = eeg_df['eeg'].astype(int)
    eeg_df['awake'] = eeg_df['eeg'] == 0
    eeg_df['NREM'] = eeg_df['eeg'] == 1
    eeg_df['REM'] = eeg_df['eeg'] == 2
    return eeg_df

def plot_state_velocity(imaging_exp, df, state):
    """
    Creates a graphical representation of velocity and brain state

    Parameters:
    ===========
    imaging_exp: ImagingExperiment object
    df: pandas DataFrame
        required columns: 'filtered velo', 'NREM','state:awake',
        'state:locomotion'
    state: list, str
        list or str of state columns from the df with booleans or 0-1 values
    """
    
    fig, ax1 = plt.subplots(nrows=2, ncols=1, figsize=(15,10))
    fig.suptitle('Velocity vs %s' % state, fontsize=16, y=1.02)

    color = 'tab:red'
    ax1[0].set_xlabel('frames')
    ax1[0].set_ylabel('m/s', color=color, fontsize=16)
    df['filtered velo'][:18000].plot(ax=ax1[0], color=color)
    ax1[0].tick_params(axis='y', labelcolor=color)
    ax1[0].legend().remove()

    ax2 = ax1[0].twinx()  # instantiate a second axes that shares the same x-axis

    color = 'tab:blue'
    ax2.set_ylabel(state, color=color, fontsize=16)    
    df[state].astype(int)[:18000].plot(ax=ax2,color=color)
    ax2.set_yticks((0,1))
    ax2.tick_params(axis='y', labelcolor=color)
    ax2.legend().remove()

    color = 'tab:red'
    ax1[1].set_xlabel('frames')
    ax1[1].set_ylabel('m/s', color=color, fontsize=16)
    df['filtered velo'][18000:].plot(ax=ax1[1], color=color)
    ax1[1].tick_params(axis='y', labelcolor=color)
    ax1[1].legend().remove()

    ax2 = ax1[1].twinx()  # instantiate a second axes that shares the same x-axis

    color = 'tab:blue'
    ax2.set_ylabel(state, color=color, fontsize=16)  
    df[state][18000:].astype(int).plot(ax=ax2,color=color)
    ax2.set_yticks((0,1))
    ax2.tick_params(axis='y', labelcolor=color)
    ax2.legend().remove()

    fig.tight_layout()  # otherwise the right y-label is slightly clipped
    fname = state.replace(':', '_')
    fig.savefig(join(imaging_exp.sima_path, 'Velocity vs %s.png' % fname),
               transparent=True, dpi=300, bbox_inches='tight')

def brain_state_filter(velo_eeg_df, states):
    """
    sets up boolean masks for brain states

    Paramaters:
    ===========
    velo_eeg_df: pandas DataFrame
        contains a 'filtered_velo' columns with the velocity and columns
        with brain states. See eeg.import_eeg()
    states: list
        list of the possible brain states: NREM, REM, awake
        
    Return:
    =======
    filters: dictionary
        the keys correspond to boolean values
    states: list
        the states used as an input plus 'locomotion'

    """
    l1 = ['NREM', 'REM', 'awake']
    filters = {}
    if collections.Counter(states) == collections.Counter(l1):
        print(f'Making filters for {l1} and locomotion')        
        awake = ((velo_eeg_df['NREM']==False) &
             (velo_eeg_df['REM']==False) &
             (velo_eeg_df['filtered velo']<0.1))
        NREM = ((velo_eeg_df['NREM']) &
                (velo_eeg_df['filtered velo']<=0.1))
        REM = ((velo_eeg_df['REM']) &
               (velo_eeg_df['filtered velo']<=0.1))
        locomotion = ((velo_eeg_df['NREM']==False) &
              (velo_eeg_df['REM']==False) &
              (velo_eeg_df['filtered velo']>0.1))
        filters = {'awake':awake,
                  'NREM': NREM,
                  'REM':REM,
                  'locomotion':locomotion}        
    else:
        print(f'no REM, making filters for NREM, awake and locomotion')
        awake = ((velo_eeg_df['NREM']==False) &
             (velo_eeg_df['REM']==False) &
             (velo_eeg_df['filtered velo']<0.1))
        NREM = ((velo_eeg_df['NREM']) &
                (velo_eeg_df['filtered velo']<=0.1))        
        locomotion = ((velo_eeg_df['NREM']==False) &
              (velo_eeg_df['REM']==False) &
              (velo_eeg_df['filtered velo']>0.1))
        filters = {'awake': awake,
                  'nrem':nrem,
                  'locomotion':locomotion}
    states.append('locomotion')
    return filters, states