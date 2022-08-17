from .api import run
from .update_api import deploy_resources, reosurces_are_updated


import fire
fire.Fire({
    'run': run,
    'is-updated': reosurces_are_updated,
    'reload': deploy_resources,

})