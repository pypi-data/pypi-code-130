import os, sys, json
from epcam_api import BASE

from epcam_api.Action import Selection, Information

def delete_feature(job, step, layers):
    try:
        BASE.sel_delete(job, step, layers)
    except Exception as e:
        print(e)
    return 0

def break_features(job, step, layers, type):
    try:
        BASE.sel_break(job, step, layers, type)
    except Exception as e:
            print(e)
    return 0

def add_line(job, step, layers, symbol, start_x, start_y, end_x, end_y, polarity, attributes):
    try:
        layer = ''
        if len(layers) > 0:
            layer = layers[0]
        BASE.add_line(job, step, layers, layer, symbol, start_x, start_y, end_x, end_y, polarity, 0, attributes)
    except Exception as e:
        print(e)
    return 0

def hierarchy_edit(job, step, layers, mode):
    try:
        BASE.sel_index(job, step, layers, mode)
    except Exception as e:
        print(e)
    return 0

def add_surface(job, step, layers, polarity, attributes, points_location):
    try:
        layer = ''
        if len(layers)> 0:
            layer = layers[0]
        BASE.add_surface(job, step, layers, layer, polarity, 0, False, attributes, points_location)
    except Exception as e:
        print(e)
    return ''

def add_round_surface(job, step, layers, polarity, attributes,center_x,center_y,radius):
    try:
        layer = ''
        if len(layers)> 0:
            layer = layers[0]
        point2_x = center_x + radius
        point2_y = center_y
        points_location = [[center_x, center_y], [point2_x, point2_y]]
        BASE.add_surface(job, step, layers, layer, polarity, 0, True, attributes, points_location)
    except Exception as e:
        print(e)
    return '' 

def contour2pad(job, step, layers, tol, minsize, maxsize, suffix):
    try:
        BASE.contour2pad(job, step, layers, tol, minsize, maxsize, suffix)
    except Exception as e:
        print(e)
    return ''

def resize_polyline(job, step, layers, size, sel_type):
    try:
        BASE.resize_polyline(job, step, layers, size, sel_type)
    except Exception as e:
        print(e)
    return ''

def contourize(job, step, layers, accuracy, separate_to_islands, size, mode):
    try:
        BASE.contourize(job, step, layers, accuracy, separate_to_islands, size, mode)
    except Exception as e:
        print(e)
    return ''

def add_pad(job, step, layers, symbol, location_x, location_y, polarity, orient, attributes):
    try:
        layer=''
        if len(layers)>0:
            layer=layers[0]
        BASE.add_pad(job, step, layers, layer, symbol, location_x, location_y, polarity, 0, orient, attributes)
    except Exception as e:
        print(e)
    return ''

def change_feature_symbols(job, step, layers, symbol):
    try:
        BASE.change_feature_symbols(job, step, layers, symbol, False)
    except Exception as e:
        print(e)
    return 0

def create_profile(job, step, layer):
    try:
        BASE.create_profile(job, step, layer)
    except Exception as e:
        print(e)
    return 0
    
def step_repeat(job, parent_step, child_steps):
    """
    #拼板
    :param     parentstep: panel
    :param     childsteps: 拼入panel的step
    :returns    :
    :raise error:
    """
    try:
        BASE.step_repeat(job, parent_step, child_steps)
    except Exception as e:
        print(e)
    return 0

def surface_repair(job, step, layers, scope, radius, remove_type, is_round):
    try:
        ret= Information.check_matrix_info(job,step,layers)
        if ret==True:
            BASE.remove_sharp_angle(job, step, layers, scope, radius, remove_type, is_round)
    except Exception as e:
        print(e)
    return 


def line2pad(job, step, layers):
    try:
        ret= Information.check_matrix_info(job,step,layers)
        if ret==True:
            BASE.line2pad_new(job, step, layers)
    except Exception as e:
        print(e)
    return 

def surface2outline(job, step, layers, width):
    try:
        ret= Information.check_matrix_info(job,step,layers)
        if ret==True:
            BASE.surface2outline(job, step, layers, width)
    except Exception as e:
        print(e)
    return 

def modify_attributes(job, step, layers, mode, attributes):
    try:
        BASE.modify_attributes(job, step, layers, mode, attributes)
    except Exception as e:
        print(e)
    return 