# the data must be a series and continuous
def prepForHistogram(data_array, num_digits = 0):
    # import data
    import pandas as pd
    import numpy as np
    import matplotlib.pyplot as plt
    import scipy.stats as stats

    # describe the data
    print(f'Data description:\n{data_array.describe()}\n')

    # extract info to help create bins
    zscores = stats.zscore(data_array)
    outliers = zscores[(zscores < -3) | (zscores > 3)]

    if len(outliers) > 0:
        print(f'Are there any outliers in the data? Yes, there are {len(outliers)} outliers.')
        print(f'The outliers are on average {round(np.absolute(outliers).mean(),1)} standard deviations away.\n')
    else:
        print(f'Are there any outliers in the data? No, there are no outliers.\n')

    minWithin6std = np.floor(min(data_array[zscores>-3]))
    print(f'Minimum value in the data excluding the outliers is: {minWithin6std}')
    maxWithin6std = np.ceil(max(data_array[zscores<3]))
    print(f'Maximum value in the data excluding the outliers is: {maxWithin6std}')


    # calculate the proposed bin size based on Sturge’s rule 
    # use this value as a rule of thumb 
    # perferably not lower than 5 or higher than 20
    n = round(1+3.322*np.log(len(data_array)))
    print(f'Suggested bin size based on Sturge’s rule: {n}\n')

    binWidth = round((maxWithin6std - minWithin6std)/n, 0)
    print(f'Suggested bin width is: {binWidth}\n')
    return data_array
    
###############################################################################################################
def plotHistogram(min_value, max_value, outlier, width, figsize = (7, 4), facecolor = "#5790fc", num_digits = 0):
    # create bins
    binSize = (max_value - min_value)/width # change this to another value if need be
    bins = []
    for i in range(0, int(binSize + 1)):
        bins = bins + [min_value + i*width]
    binTickLabels = [f'[{i},{i+width})' for i in bins]
    binTickLabels[-1] = binTickLabels[-1].split(',')[0] + ',' + str(round(outlier)) + ')'

    # plot the figure
    y, x = np.histogram(data_array,bins=bins)
    x = [i/width for i in bins]
    y = list(y) + [len(data_array[data_array > bins[-1]])]

    # create the figure
    # 7 inch the the width of a letter size paper excluding the margins
    fig, ax = plt.subplots(1,1, figsize = figsize) 
    ax.bar(x, y, width = 0.8, align = 'center', facecolor = facecolor)

    # figure customization
    ax.set_title('Histogram of ----')
    ax.set_xlabel('Seconds')
    ax.set_ylabel('Frequency')
    ax.set_xticks([i/width for i in bins])
    ax.set_xticklabels(binTickLabels, rotation = 45, ha = 'right')
    #ax.set_xlim(0, 1000)
    #ax.set_ylim(0, 1)

    ax.grid(alpha = 0.2)
    plt.show()
