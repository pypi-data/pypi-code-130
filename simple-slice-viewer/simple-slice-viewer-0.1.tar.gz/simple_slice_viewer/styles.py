import os
import numpy as np
import yaml
import matplotlib.pyplot as plt

from pyqtgraph import ColorMap


def get_cmap(col_data):
    return ColorMap(pos=col_data[:,-1], color=255*col_data[:,:3]+0.5)


__file__ = os.getcwd() + '/test.tx'
STYLE_DATA = yaml.safe_load(open(os.path.join(os.path.split(__file__)[0], 'styles.yml')))

STYLE_DATA['colormaps'] = sorted(plt.colormaps())


# STYLE_DATA = {'colormaps':  ['gray',
#                              'gray_r',
#                               'hot',
#                               'afmhot',
#                               'bone',
#                               'copper',
#                               'rainbow',
#                               'jet',
#                               'seismic'],
#  'window_levels': {'Full': None,
#   'CT Soft Tissue': [400, 50],
#   'CT Bones': [1800, 400],
#   'CT Lung': [1500, -600],
#   'CT Liver': [150, 30],
#   'PET 0-6 SUV': [6, 3],
#   'PET 0-10 SUV': [10, 5],
#   'PET 0-3 SUV': [3, 1.5],
#   'PET 0-1 SUV': [0.5, 1],
#   'Mask': [0.5, 1]},
#  'presets': {'FULL': {'image': {'window_level': None, 'cmap': 'gray'},
#    'fusion': {'window_level': None, 'cmap': 'hot'}},
#   'Overlay': {'image': {'window_level': 'CT Bones', 'cmap': 'Greens'},
#    'fusion': {'window_level': 'CT Bones', 'cmap': 'Magentas', 'alpha': 0.5}},
#   'PET': {'image': {'window_level': 'PET 0-6 SUV', 'cmap': 'gray_r'},
#    'fusion': {'window_level': None, 'cmap': 'hot', 'alpha': 0.5}},
#   'PET-CT': {'image': {'window_level': 'CT Soft Tissue', 'cmap': 'gray'},
#    'fusion': {'window_level': None, 'cmap': 'hot', 'alpha': 0.5}},
#   'PET-CT SUV': {'image': {'window_level': 'CT Soft Tissue', 'cmap': 'gray'},
#    'fusion': {'window_level': 'PET 0-6 SUV', 'cmap': 'hot', 'alpha': 0.5}},
#   'Mask': {'image': {'window_level': 'CT Soft Tissue', 'cmap': 'gray'},
#    'fusion': {'window_level': 'Mask', 'cmap': 'copper', 'alpha': 1}}}}


_greens = np.array([[0., 0., 0., 0.],
                     [0., 1., 0., 1.]])

_magentas = np.array([[0., 0., 0., 0.],
                      [1., 0., 1., 1.]])

CUSTOM_COLORMAPS = {'Greens': get_cmap(_greens),
                    'Magentas': get_cmap(_magentas)}





FILE = 'styles.yml'


folder = os.path.split(__file__)[0]



WINDOW_LEVELS = STYLE_DATA['window_levels']
PRESETS = STYLE_DATA['presets']
COLORMAPS = STYLE_DATA['colormaps']