
from dreem_herschlag.resources import __file__ as resources_file
from dreem_herschlag import __file__ as dreem_herschlag_file
import yaml, os, subprocess
import string
import random

class Path(object):
    def __init__(self) -> None:    
        self.resources_file = '/'.join(resources_file.split('/')[:-1])
        self.dreem_herschlag_file = '/'.join(dreem_herschlag_file.split('/')[:-1])
        self.sample_attribute_path = self.resources_file+'/sample_attributes.yml'
        self.library_attributes_path = self.resources_file+'/library_attributes.yml'
        self.config_template = self.resources_file+'/config-template.yml'

def run_command(cmd):
    output, error_msg = None, None
    try:
        output = subprocess.check_output(
                cmd, shell=True, stderr=subprocess.STDOUT
        ).decode("utf8")
    except subprocess.CalledProcessError as exc:
        error_msg = exc.output.decode("utf8")
    return output, error_msg

def format_path(path):
    if path == '.':
        path = os.path.abspath('')
    if path[-1] != '/':
        path = path+'/'
    if not os.path.exists(path):
        os.makedirs(path)
    return path


def get_random_string(length):
    # With combination of lower and upper case
    result_str = ''.join([random.choice(string.ascii_letters) for i in range(length)])
    # return random string
    return result_str
