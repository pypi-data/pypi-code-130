


import matplotlib.pyplot as plt
from tqdm.auto import tqdm
from imgaug import augmenters as iaa  # optional program to further augment data

from whacc import utils
import numpy as np
from whacc import image_tools, PoleTracking
from natsort import natsorted, ns
import pickle
import pandas as pd
import os
import copy
import seaborn as sns
from keras.preprocessing.image import ImageDataGenerator
import h5py

from whacc import utils, analysis
import h5py
import matplotlib.pyplot as plt
import numpy as np
from sklearn import metrics
from pathlib import Path

from whacc import utils, image_tools, transfer_learning, analysis
from IPython.utils import io
import matplotlib.pyplot as plt
from tensorflow.keras.layers import Dense, Dropout
from tensorflow.keras.models import Model
from tensorflow import keras
from sklearn.utils import class_weight
import time
from pathlib import Path
import os
import copy
import numpy as np
from tensorflow.keras import applications
from pathlib import Path
import shutil
import zipfile
from datetime import datetime
import pytz
import json
from whacc import model_maker

from whacc.model_maker import *
import itertools

import tensorflow as tf
from tensorflow import keras
import matplotlib.pyplot as plt
import numpy as np
import h5py
from whacc import image_tools
from whacc import utils
import copy
import time
import os
import pdb
import glob
from tqdm.contrib import tzip
import scipy.io as spio
import h5py
# from tqdm.notebook import tqdm
from matplotlib import cm

import matplotlib.pyplot as plt
import matplotlib.gridspec as gridspec
import numpy as np
import matplotlib.patches as mpatches
from scipy.signal import medfilt, medfilt2d
import cv2


def remap_array_to_color_channels(in_array, color_numers_to_match=None, color_list=[0, .5, .2, .3, .75, .85],
                                  cmap_col='inferno'):
    in_array = copy.deepcopy(in_array).astype(int)
    out_array = np.stack((in_array,) * 3, axis=-1)

    color_dict = dict()
    cmap = cm.get_cmap(cmap_col)
    if color_numers_to_match is None:
        color_numers_to_match = np.unique(in_array).astype(int)
        print(color_numers_to_match)

    for key, k1 in zip(color_numers_to_match, color_list):
        color_dict[key] = (np.asarray(cmap(k1)[:-1]) * 255).astype(int)
    for ii, kk in enumerate(color_numers_to_match):
        out_array[(in_array == kk).astype(bool)] = color_dict[kk]

    return out_array, color_dict


def foo_heatmap_with_critical_errors(real_bool, pred_bool, in_range, frame_nums, lines_thick=20, title_str='',
                                     figsize=(10, 10)):
    acc_percentage = ((pred_bool == real_bool) * 1).astype(float)
    acc_percentage[np.invert(in_range.astype(bool))] = np.nan
    acc_percentage = np.nanmean(acc_percentage)
    acc_percentage = str(np.round(acc_percentage * 100, 2)) + '%  '
    title_str = acc_percentage + title_str

    c_list = []
    for n in [2, 3, 4, 5, 8]:
        c_list.append(.0833 / 2 + n * .0833)

    max_ = np.max(frame_nums)
    x = np.zeros([len(frame_nums), int(max_)]) - 2

    d = real_bool - pred_bool
    d = d + (real_bool + pred_bool == 2) * 2  # TP = 2, TN = 0, FP = -1, FN = 1 ...... -2 pole out of range

    for i, (k1, k2) in enumerate(utils.loop_segments(frame_nums)):
        L = frame_nums[i]
        tmp1 = d[k1:k2]

        tmp1[in_range[k1:k2] == 0] = -2
        # in_range[k1:k2]
        x[i, :L] = tmp1

    x2, color_dict = remap_array_to_color_channels(x, color_numers_to_match=[0, 2, 1, -1, -2], color_list=c_list,
                                                   cmap_col='Paired')
    x2 = np.repeat(x2, lines_thick, axis=0)

    # get the color coded error type matrix
    a = analysis.error_analysis(real_bool, pred_bool, frame_num_array=frame_nums)
    d = copy.deepcopy(a.coded_array)
    d[d < 0] = -2
    d[d >= 4] = -2

    max_ = np.max(frame_nums)
    x = np.zeros([len(frame_nums), int(max_)]) - 2

    for i, (k1, k2) in enumerate(utils.loop_segments(frame_nums)):
        L = frame_nums[i]
        tmp1 = d[k1:k2]

        tmp1[in_range[k1:k2] == 0] = -2
        x[i, :L] = tmp1
    c_list = []
    for n in [1, 3, 4, 5, 8]:  # ['ghost', 'miss', 'join', 'split', nothing
        c_list.append(.1111 / 2 + n * .1111)
    x2_error_type, color_dict_error_type = remap_array_to_color_channels(x, color_numers_to_match=[0, 1, 2, 3, -2],
                                                                         color_list=c_list, cmap_col='Set1')
    print(np.nanmin(x2_error_type))
    x2_error_type = np.repeat(x2_error_type, lines_thick, axis=0)

    for i, (k1, k2) in enumerate(utils.loop_segments([10, 10] * len(
            frame_nums))):  # nan out certain regions so that we can leave those to be filled in with actual heatmap
        if (i % 2) != 0:
            x2_error_type[k1:k2] = color_dict_error_type[-2]

    x3 = copy.deepcopy(x2).astype(int)
    inds = x2_error_type != color_dict_error_type[-2]
    x3[inds] = x2_error_type[inds]
    plt.figure(figsize=figsize)
    plt.imshow(x3)

    # LEGEND
    all_labels = ['TN', 'TP', 'FN', 'FP', 'pole down']
    patches = []
    for i, ii in zip(color_dict, all_labels):
        c = color_dict[i] / 255
        patches.append(mpatches.Patch(color=c, label=ii))
    all_labels = ['ghost', 'miss', 'join', 'split']
    for i, ii in zip(color_dict_error_type, all_labels):
        c = color_dict_error_type[i] / 255
        patches.append(mpatches.Patch(color=c, label=ii))
    plt.legend(handles=patches, bbox_to_anchor=(1.02, 1), loc=2, borderaxespad=0, fontsize=15, prop={'size': 6})
    plt.title(title_str, fontsize=20)

    return x3


h5 = '/Volumes/GoogleDrive-114825029448473821206/.shortcut-targets-by-id/1pUteMEgx37rAyqujJWxVN9-ywFAqaxhF/WhACC_PROCESSING_FOLDER/Finished_Sessions/Session1_FINISHED/Session1/AH1179X23052021x1_final_combined.h5'
h5 = '/Users/phil/Desktop/SAMSONS_TEST_SESSIONS/TESTING_SAMSONS_MP4S_FINISHED/AH1179X01062021x14_final_combined.h5'
####################################
####################################

utils.foo_predict_mods('/Users/phil/Desktop/002_model.pkl', h5)
####################################
####################################
utils.print_h5_keys(h5)
labels_key = 'YHAT__002_model'
pred_bool_temp = image_tools.get_h5_key_and_concatenate(h5, labels_key)
contacts_samson_curated_for_transfer_learning_220707 = image_tools.get_h5_key_and_concatenate(h5, 'contacts_samson_curated_for_transfer_learning_220707')
labels = image_tools.get_h5_key_and_concatenate(h5, 'labels')
frame_nums = image_tools.get_h5_key_and_concatenate(h5, 'frame_nums')
################################################
""" SET THHE SOURCE OF THE LABELS YOU ARE DRAWING FROM MAKE SURE TO ADJUST MODEL IND ACCORDINGLY"""
threshold = .4
lines_thick = 20
kernel_size = 11

in_range = 1*(contacts_samson_curated_for_transfer_learning_220707!=-1)

real_bool = contacts_samson_curated_for_transfer_learning_220707
real_bool[np.invert(in_range.astype(bool))] = -1
real_bool = 1*(real_bool==1)

# pred_bool_temp = pred_bool_temp.astype(float)
pred_bool_smoothed = medfilt(copy.deepcopy(pred_bool_temp).flatten(), kernel_size=kernel_size)
pred_bool_smoothed = (pred_bool_smoothed>threshold)*1

x2 = foo_heatmap_with_critical_errors(real_bool, pred_bool_smoothed, in_range, frame_nums.astype(int), title_str='')






tmp3 = plot_segments_with_array_blocks(h5, [[100]], in_list_of_arrays=[real_bool, pred_bool_smoothed],
                                       seg_num=0,
                                       color_numers_to_match=[0, 1], color_list=[0, .5], cmap_col='nipy_spectral',
                                       max_frames=20, min_frames=20)

#
#
# a = analysis.error_analysis(1*(real_bool==1), 1*(pred_bool_smoothed==1), frame_num_array=frame_nums.astype(int))
# # pred_bool = copy.deepcopy(pred_bool_smoothed)
# # pred_bool[np.invert(in_range.astype(bool))] = -1
# x2 = foo_heatmap_with_critical_errors(real_bool, pred_bool_smoothed, in_range, frame_nums, title_str='median smoothed')
#
#
#

for i, (i1, i2) in enumerate(utils.loop_segments(frame_nums)):
    ii = i*lines_thick
    x = pd.Series(pred_bool_temp[i1:i2])
    tmp1 = np.argmax(x.rolling(window=10).std())
    plt.plot(tmp1,ii, '.k')
