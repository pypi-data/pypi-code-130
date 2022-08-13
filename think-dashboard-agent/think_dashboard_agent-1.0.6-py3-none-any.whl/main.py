import os
import sys
import time
from pathlib import Path
from typing import Dict, Union

import requests
from apscheduler.events import EVENT_JOB_ERROR
from apscheduler.schedulers.background import BackgroundScheduler

from think_dashboard_agent import types
from think_dashboard_agent.providers import DEFAULT_PROVIDERS, BaseProvider

__scheduler = BackgroundScheduler()
__inited_providers: Dict[str, BaseProvider] = {}
requests_session = requests.Session()


def __run(
        config: types.Config,
        providers: Dict[str, BaseProvider] = None,
        auto_close: bool = True,
        post_to_api: bool = False,
        session: requests.Session = None
):
    _results = []
    if providers is None:
        providers = DEFAULT_PROVIDERS
    else:
        providers = {**DEFAULT_PROVIDERS, **providers}

    for instance in config.instances:
        if instance.key not in __inited_providers:
            provider = providers[instance.type]
            __inited_providers[instance.key] = provider.init(instance)
    for provider in __inited_providers.values():
        instance_result = provider.check(auto_close).dict()
        _results.append({
            'key': getattr(getattr(provider, 'instance'), 'key'),
            'type': getattr(getattr(provider, 'instance'), 'type'),
            'name': getattr(getattr(provider, 'instance'), 'name'),
            'response': instance_result,
        })

    post_body = {
        'server': config.server_name,
        'instances': _results,
    }
    if post_to_api:
        if session is None:
            session = requests_session
            session.headers.update({'Authorization': f"Token {config.api_key}"})
        try:
            r = session.post(config.dashboard_url, json=post_body)
            if r.status_code != 200:
                raise Exception(f'Failed to post to dashboard: {r.status_code}')
        finally:
            if auto_close is True:
                session.close()
    else:
        print(post_body)


def run(conf_file: Union[str, Path], providers: Dict[str, BaseProvider] = None, post_to_api: bool = True):
    config = types.Config.from_file(conf_file)

    __run(config, providers, auto_close=True, post_to_api=post_to_api)


def run_forever(
        conf_file: Union[str, Path],
        interval: int = 30,
        providers: Dict[str, BaseProvider] = None,
        post_to_api: bool = True,
):
    config = types.Config.from_file(conf_file)

    requests_session.headers.update({'Authorization': f"Token {config.api_key}"})

    __scheduler.add_job(
        __run,
        'interval',
        seconds=interval,
        args=[
            config,
            providers,
            False,
            post_to_api,
            requests_session,
        ]
    )
    __scheduler.add_listener(__job_exception_handler, EVENT_JOB_ERROR)
    __scheduler.start()
    print('Press Ctrl+{0} to exit'.format('Break' if os.name == 'nt' else 'C'))
    try:
        while __scheduler.running:
            time.sleep(2)
    except (KeyboardInterrupt, SystemExit):
        print('Shutting down...')
    finally:
        requests_session.close()
        if __scheduler.running:
            __scheduler.shutdown(wait=False)
        for provider in __inited_providers.values():
            provider.close()
        sys.exit(0)


def __job_exception_handler(event):  # noqa
    if __scheduler.running:
        __scheduler.shutdown(wait=False)
