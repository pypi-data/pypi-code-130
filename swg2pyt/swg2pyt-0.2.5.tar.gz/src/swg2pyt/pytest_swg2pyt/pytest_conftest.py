# -*- coding: utf-8 -*-
import sys
from os import path

import pytest
from swg2pyt.GlobalDict import GlobalDict


@pytest.fixture
def whoami():
    return {"name": "swg2pyt"}


def pytest_collection_modifyitems(config, items):
    # 收集pytest collected item，用于控制执行流程
    gd = GlobalDict()
    for item in items:
        gd[item.name] = item


def pytest_configure(config: pytest.Collector.config):
    # 注册来自xmind的mark
    case_dir = config.invocation_params.args[0]
    markpath = ''
    if path.isdir(case_dir):
        markpath = path.join(path.abspath(case_dir), "marks")
        if not path.exists(markpath):
            return
    with open(markpath, "r", encoding="utf-8")as markfile:
        marks = markfile.read().split(",")
    for mark in marks:
        config.addinivalue_line("markers", f"{mark}: mark from xmind.")

    # try to import custom prtreator
    for plugin in config.pluginmanager._conftest_plugins:
        if "SWG2PYT_CUSTOM_PRT" in plugin.__dict__:
            GlobalDict().setdefault("custom_prt", {}).update(plugin.SWG2PYT_CUSTOM_PRT)


def pytest_runtest_teardown(item, **kwargs):
    # 将被强制先行执行过的用例加入堆栈
    if pytest.__version__.split('.')[0] == '6':
        forced = GlobalDict().setdefault("forced", [])
        if item.name in forced:
            item.session._setupstate.stack.append(item)


def pytest_runtestloop(session):
    # 变更执行顺序
    queue = GlobalDict().setdefault("queue", {})
    session.items.sort(key=lambda item: queue.get(item.name, 0), reverse=True)
