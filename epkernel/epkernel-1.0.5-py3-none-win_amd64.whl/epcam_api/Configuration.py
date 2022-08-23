import os, sys, json
from epcam_api import epcam, BASE

def init(): 
    epcam.init()
    config_path = os.path.join(os.path.join(os.path.dirname(os.path.realpath(__file__)), 'bin'), 'config')
    BASE.set_config_path(config_path)

def set_sys_attr_path(path):
    try:
        BASE.set_sysAttr_path(path)
    except Exception as e:
        print(e)
    return 

def set_user_attr_path(path):
    try:
        BASE.set_userAttr_path(path)
    except Exception as e:
        print(e)
    return  
