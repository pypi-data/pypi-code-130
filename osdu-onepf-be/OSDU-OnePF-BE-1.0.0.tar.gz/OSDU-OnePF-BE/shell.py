import os
import subprocess
import sys
import json
root = os.getcwd()
''' Fetching required parameters'''
with open(os.path.join(root,"config1.json"),"r") as f:
    path=json.load(f)
with open(os.path.join(root,path['global_config']), "r") as f:
        global_config = json.load(f)
