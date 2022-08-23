import base64
import datetime
import json
import os
from json import loads as jsl
from typing import Generator

import jmespath
from pytest import __version__, skip

from .GlobalDict import GlobalDict

GD = GlobalDict()


class Pretreator():
    inst = {}

    def fixture(self, casekey, arglist, fixture=None):
        if fixture is None:
            assert False, "fixture not found,check fixture in 预置条件"
        for ft in arglist:
            if "." in ft:
                fix, ture = ft.split(".", 1)
                f_type = type(fixture[fix])
                if f_type == dict:
                    return fixture[fix][ture]
                elif f_type == str:
                    return fixture[fix]
                elif callable(fixture[fix]):
                    if "," in ture:
                        ture = ture.split(",")
                        return fixture[fix](*ture)
                    return fixture[fix](ture)
                else:
                    try:
                        return fixture[fix].__getattribute__(ture)
                    except AttributeError:
                        return fixture[fix]
            else:
                return fixture[ft]

    def precase(self, casekey, arglist, fixture=None):
        for pcase in arglist:
            self.getrsh(casekey, f'test_{pcase}', {}, fixture, 0)

    def ifprecase(self, casekey, arglist, fixture=None):
        if not arglist:
            return
        casershs = GD.setdefault("casershs", {})
        ifcase = arglist.pop(0)
        pcase = arglist.pop()if arglist else None
        if f'test_{ifcase}' in casershs:
            if pcase:
                self.getrsh(casekey, f'test_{pcase}', {}, fixture, 0)
        else:
            skip(f"因 {ifcase} 未曾执行，跳过")

    def runtest_py6(self, target):
        from _pytest.fixtures import FixtureRequest
        from _pytest.runner import runtestprotocol
        fr = FixtureRequest(target)
        gfv = fr.getfixturevalue
        target.funcargs = {fn: gfv(fn)for fn in target.fixturenames}
        if hasattr(target, '_request') and not target._request:
            target._request = fr
        runtestprotocol(target, log=False, nextitem=GD[GD["nextitem"]])

    def runtest_py7(self, current, target):
        from _pytest.runner import (pytest_runtest_call, pytest_runtest_setup,
                                    pytest_runtest_teardown)
        old_parent = target.parent
        target.parent = GD[current]
        pytest_runtest_setup(target)
        pytest_runtest_call(target)
        pytest_runtest_teardown(target, nextitem=GD[current])
        target.parent = old_parent

    def getrsh(self, current, target, kwargs={}, fixture=None, caseindex=0):
        casershs = GD.setdefault("casershs", {})
        target_item = None
        if (target not in casershs) or kwargs:
            try:
                target_item = GD[target]
            except KeyError:
                assert False, "无此用例"
            GD.setdefault("rearkwargs", {}).update({target: kwargs})
            GD["byforce"] = target
            GD.setdefault("forced", []).append(target)
            if __version__.split('.')[0] == '6':
                self.runtest_py6(target_item)
            elif __version__.split('.')[0] == '7':
                self.runtest_py7(current, target_item)
            GD["byforce"] = None
        casershs = GD.setdefault("casershs", {})
        if target not in casershs:
            assert False, "来源用例可能未曾成功执行"
        rshs = []
        if isinstance(caseindex, Generator):
            realindex, nextindex = next(caseindex)
            rshs.append(casershs[target][realindex])
            while nextindex:
                realindex, nextindex = next(caseindex)
                rshs.append(casershs[target][realindex])
        elif isinstance(caseindex, int):
            rshs.append(casershs[target][caseindex])
        else:
            rshs = casershs[target]
        rshs = [[rsh[index] for rsh in rshs]for index in [0, 1, 2, 3, 4]]
        if kwargs:
            GD.setdefault("casershs", {}).pop(target)
        return rshs

    def fromcase(self, casekey, arglist, fixture=None):
        '''
        :param: arglist: [casekey, path]
        :param: casekey: ["body"|"status"|"headers"]
        :param: path: ["body.xxx.yyy.zzz"|"status"|"headers.headerkey"]
        '''
        caseindex = None
        if len(arglist) == 3:
            caseindex = arglist.pop()
        target, path = arglist
        response_s = None
        status_s = None
        headers_s = None
        rshs = self.getrsh(casekey, f'test_{target}', {}, fixture, caseindex)
        response_s, status_s, headers_s, body_s, other_s = rshs
        rt = []
        path = path.split(".", 1)
        target = path[0]
        if path:
            path = path.pop()
        if target == "req":
            for body in body_s:
                rt.append(jmespath.search(path, body))
        elif target == "other":
            for other in other_s:
                rt.append(jmespath.search(path, other))
        elif target == "body":
            for response in response_s:
                response = str(response.data, encoding="utf-8")
                response = jsl(response.replace("'", '"'))
                if type(path) != str or len(path) == 0:
                    assert False, "【fromcase】路径无法解析"
                rt.append(jmespath.search(path, response))
        elif target == "status":
            rt = [status for status in status_s]
        elif target == "headers":
            rt = [headers.get[path] for headers in headers_s]
        if not rt:
            return None
        if type(caseindex) == int:
            return rt[caseindex]
        else:
            return rt[0]

    def accept(self, casekey, arglist, fixture=None):
        data = GD.setdefault("rearkwargs", {})
        data = data.get(casekey)
        return jmespath.search(arglist[0], data)

    def sth(self, casekey, arglist, fixture=None):
        return "unfinish"

    def tolen(self, casekey, arglist, fixture=None):
        return len(arglist[0])

    def replace(self, casekey, arglist, fixture=None):
        if len(arglist) == 1:
            return arglist[0]
        else:
            if type(arglist[2]) == dict:
                key, argl = arglist[2].popitem()
                if key in self.prtdict:
                    arglist[2] = self.prtdict[key](argl)
            origin, old, new = [str(arg)for arg in arglist]
            return origin.replace(old, new)

    def timestamp(self, casekey, arglist, fixture=None):
        now = datetime.datetime.now()
        if "int" in arglist:
            rt = str(int(datetime.datetime.timestamp(now)))
        elif "float" in arglist:
            rt = str(datetime.datetime.timestamp(now))
        if len(arglist) >= 3:
            start = arglist[1]
            stop = arglist[2]
            step = None
            if len(arglist) == 4:
                step = arglist[3]
            return rt[slice(start, stop, step)]
        return rt

    def tobase64(self, casekey, arglist, fixture=None):
        target_type = "string"
        if len(arglist) == 2:
            target_type = arglist[0]
        if target_type == "string":
            return base64.b64encode(arglist[1])
        elif target_type == "file":
            target_path = os.path.join(os.getcwd(), "localfile", arglist[1])
            with open(target_path, "rb") as target:
                return str(base64.b64encode(target.read()), encoding="ascii")

    def toint(self, casekey, arglist, fixture=None):
        if not arglist:
            return 0
        try:
            return int(arglist.pop())
        except TypeError:
            return 0

    def tofloat(self, casekey, arglist, fixture=None):
        if not arglist:
            return 0
        try:
            return float(arglist.pop())
        except TypeError:
            return 0

    def tostr(self, casekey, arglist, fixture=None):
        arg = arglist.pop()
        if type(arg) == bytes:
            return str(arg, encoding="utf-8")
        else:
            return str(arg)

    def torange(self, casekey, arglist, fixture=None):
        start, stop = arglist
        return list(range(start, stop))

    def tolist(self, casekey, arglist, fixture=None):
        return [arg for arg in arglist]

    def todict(self, casekey, arglist, fixture=None):
        key, value = arglist
        return {key: value}

    def parametrize(self, casekey, arglist, fixture=None):
        if len(arglist) == 2:
            return self.paramgenerator(casekey, arglist[0], True)
        else:
            return self.paramgenerator(casekey, arglist[0])

    def paramgenerator(self, casekey, arglist, lenonly=False):
        if not arglist:
            raise IndexError
        finalval = None
        for index, a in enumerate(arglist):
            finalval = a
            if lenonly:
                yield [index, bool(index < len(arglist)-1)]
            else:
                yield [finalval, bool(index < len(arglist)-1)]
        while True:
            if lenonly:
                yield [index, False]
            else:
                yield [finalval, False]

    def __new__(cls):
        inited = True
        if not cls.inst.get(inited):
            inited = False
            cls.inst.update({False: object.__new__(cls)})
        return cls.inst.get(inited)

    def __init__(self):
        if False in Pretreator.inst:
            self.prtdict = {"sth": self.sth,
                            "len": self.tolen,
                            "toint": self.toint,
                            "tostr": self.tostr,
                            "range": self.torange,
                            "base64": self.tobase64,
                            "accept": self.accept,
                            "tolist": self.tolist,
                            "todict": self.todict,
                            "tofloat": self.tofloat,
                            "fixture": self.fixture,
                            "replace": self.replace,
                            "precase": self.precase,
                            "fromcase": self.fromcase,
                            "ifprecase": self.ifprecase,
                            "timestamp": self.timestamp,
                            "parametrize": self.parametrize,
                            }
            custom_prt = GD.setdefault("custom_prt", {})
            if custom_prt:
                self.update_prtdict(custom_prt)

    def update_prtdict(self, custom_prt: dict):
        # cp_dict key 查重, 避免覆盖预置prt
        custom_prt.update(self.prtdict)
        self.prtdict = custom_prt


def prt(casekey, pretreatment, fixture=None):
    pretreatpr = Pretreator()
    for ptm in pretreatment:
        if ptm in pretreatpr.prtdict:
            pretreatment[ptm] = subprt(casekey, pretreatment[ptm], fixture)
            return pretreatpr.prtdict[ptm](casekey, pretreatment[ptm], fixture)


def subprt(casekey, arglist: list, fixture=None):
    index = [arglist.index(arg)for arg in arglist if type(arg) == dict]
    for i in index:
        arglist[i] = prt(casekey, arglist[i], fixture)
    return arglist
