"""
Play a sequence of commands concurrently via yaml specification
"""
from argparse import ArgumentError
import os
from pathlib import Path
import copy
from pathos.multiprocessing import ProcessPool

import yaml
import click

from saysynth.lib import controller
from saysynth.cli.commands import chord, midi, note, arp


TRACK_FUNCS = {
    "chord": chord.run,
    "midi": midi.run,
    "note": note.run,
    "arp": arp.run,
}

def _run_track_func(item):
    seq_name, track, kwargs = item
    pid = os.getpid()
    controller.add_parent_pid(seq_name, track, pid)
    type = kwargs.get('type', None)
    options = kwargs.get('options', {})
    options['parent_pid'] = pid # pass parent id to child process.
    if type not in TRACK_FUNCS:
        raise ValueError(f'Invalid track type: {type}. Choose from: {",".join(TRACK_FUNCS.keys())}')
    print(f'Starting track {track} with parent pid {pid}')
    return TRACK_FUNCS.get(type)(**options)

def run(**kwargs):
    controller.ensure_pid_log()
    config_path = kwargs.pop('base_config')
    command = kwargs.pop('command')
    base_config = yaml.safe_load(config_path)
    config_overrides = kwargs['config_overrides']
    globals = base_config.pop('globals', {})
    seq = base_config.pop('name', None)
    if seq is None:
        raise ArgumentError('You must set a `name` in your sequence config')

    tracks = kwargs.get('tracks') or []

    # play/start sequences/tracks
    if command in ["play", "start"]:
        track_configs = []
        for track, base_track_config in base_config.get('tracks', {}).items():

            # optionally skip tracks
            if len(tracks) and track not in tracks:
                continue

            # allow for track-specific overrides
            track_overrides = config_overrides.pop(track, {})
            config_overrides.update(track_overrides)

            # create track config
            track_options = copy.copy(globals) # start with globals
            track_options.update(base_track_config.get('options', {})) # override with base track configs
            track_options.update(config_overrides)

            # optionally start tracks immediately
            if command == "start":
                track_options["start_count"] = 0

            base_track_config['options'] = track_options
            track_configs.append((seq, track, base_track_config))

        #run everything
        ProcessPool(len(track_configs)).map(_run_track_func, track_configs)

    if command == "stop":
        if not len(tracks):
            tracks = ["*"]
        for track in tracks:
            print(f"Stopping track: {track}")
            controller.stop_child_pids(seq, track)

@click.command()
@click.argument("base_config", type=click.File(), required=True)
@click.argument("command", type=click.Choice(["play", "start", "stop"]), required=False, default="play")
@click.option("-t", "--tracks", type=lambda x: [track for track in x.split(',')])
@click.option("-c", "--config-overrides", type=lambda x: yaml.safe_load(x), default='{}', help="Override global and track configurations at runtime")
def cli(**kwargs):
    run(**kwargs)
