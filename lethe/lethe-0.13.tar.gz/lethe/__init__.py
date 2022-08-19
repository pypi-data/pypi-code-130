"""
Git snapshotting tool
"""
from .lethe import (
    snap, snap_ref, snap_tree, find_merge_base, deref_symref,
    update_ref, commit_tree, get_tree, get_commit, get_obj,
    shorten_hash, get_root, get_latest_commit,
    push_ref, fetch_ref,
    )

from .endpoints import main

__author__ = 'Jan Petykeiwicz'
__version__ = '0.13'
