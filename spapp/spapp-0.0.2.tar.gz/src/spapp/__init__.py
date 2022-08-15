from spapp.node_env import NodeEnv
from spapp.node_params import NodeParams
from spapp import api

__version__ = '0.0.2'
__all__ = ['env', 'params', 'api']


# get env value, user_id, app_id, node_id etc.
env = NodeEnv()

# get node info, input output, params
_node_info = env.get_node_info()
_cli_params = env.get_params()

# get params from commandline
params = NodeParams(_cli_params, _node_info)

# setup api env
api.setup_env(env)
