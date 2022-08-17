"""Command run."""

import uvicorn

from typing import Dict
from spec import Spec, load_spec, fn
from logging import getLogger

fn.load_env()

log = getLogger(__name__)


def uvicorn_options(spec: Spec) -> Dict:
    """Uvicorn options by spec."""

    options = {
        'app': spec.runtime.entrypoint,
        'host': spec.socket.host,
        'port': spec.socket.port,
        'use_colors': not spec.runtime.on_k8s,
        'log_level': spec.log_level.lower(),
        'access_log': spec.runtime.debug,
        'workers': spec.policy.service_workers,
        'lifespan': 'auto',
    }

    # TODO: Reload dir for non k8s

    if spec.paths.log_config_path and spec.paths.log_config_path.exists():
        options['log_config'] = spec.paths.log_config_name

    return options


def uvicorn_run_service():
    """Run app with uvicorn by spec."""
    spec = load_spec()
    options = uvicorn_options(spec)
    print('>>>', options)
    uvicorn.run(**options)
