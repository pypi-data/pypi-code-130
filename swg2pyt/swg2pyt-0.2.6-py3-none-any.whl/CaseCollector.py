import json
import os
from json.decoder import JSONDecodeError
from os.path import join as opj

from xmindparser import xmind_to_dict

from .GlobalDict import GlobalDict

AST = "断言"
BODY = "请求体"
MARK = "mark"
ORDER = "order"
DESCRIPTION = "描述"
OTHER = "其他入参"
PRETREATMENT = "预置条件"


class CaseCollector(object):
    inst = {}
    xminds = []
    jsons = []

    @classmethod
    def load(*args):
        argslist = [os.getcwd()]
        argslist.extend(args[1])
        xmindpath = opj(*tuple(argslist))
        for dirpath, dirs, files in os.walk(xmindpath, topdown=True):
            if not files:
                continue
            for module in [f for f in files if f.endswith((".xmind", ".json"))]:
                module, filetype = module.rsplit(".", 1)
                gpdir, pdir = dirpath.split(os.path.sep)[-2:]
                if module == gpdir and f'{module}_data' == pdir:
                    if filetype == "xmind":
                        CaseCollector.xminds.append(
                            opj(dirpath, f'{module}.xmind'))
                    elif filetype == "json":
                        CaseCollector.jsons.append(
                            opj(dirpath, f'{module}.json'))

    def __new__(cls, *args):
        '''
        匹配规则：xxx/xxx_data/xxx.xmind
        '''
        inited = True
        if not cls.inst.get(inited):
            inited = False
            cls.inst.update({False: object.__new__(cls)})
        return cls.inst.get(inited)

    def __init__(self, *args) -> None:
        if False in CaseCollector.inst:
            CaseCollector.load(args)
            self.casedict = {}
            for xmind in CaseCollector.xminds:
                xdict = xmind_to_dict(xmind)
                xdict = xdict[0]["topic"]["topics"]
                cases = self.loadscase(self.collectcase(xdict))
                self.todict(cases)
                self.tojson(xmind, cases)
            for __json in CaseCollector.jsons:
                with open(__json, "r", encoding="utf-8") as jsfile:
                    cases = json.loads(jsfile.read())
                    for k, v in cases.items():
                        self.casedict.setdefault(k, []).extend(v)

            self.marks_and_ordering()
            CaseCollector.inst = {True: self}

    def marks_and_ordering(self):
        marker = set()
        queue = {}
        for method in self.casedict:
            for mcase in self.casedict[method]:
                casename = "test_{}_{}".format(method, mcase["title"])
                mark = mcase.get(MARK)
                order = mcase.get(ORDER)
                if mark:
                    marker.update(mark)
                if order:
                    queue[casename] = int(order)
                else:
                    queue[casename] = 0
        GlobalDict()["marks"] = marker
        GlobalDict()["queue"] = queue

    def collectcase(self, xminddic, p="root", gp="root"):
        casedict = {}
        for tp in xminddic:
            if tp["title"] == "TestCase":
                casedict[gp] = tp["topics"]
            elif tp.get("topics"):
                items = self.collectcase(tp["topics"], tp["title"], p).items()
                for topic, caselist in items:
                    casedict.setdefault(topic, []).extend(caselist)
        return casedict

    def loadscase(self, casedict):
        for casekey in casedict:
            for realcase in casedict[casekey]:
                for topic in realcase["topics"]:
                    realcase.update({topic["title"]: topic.get("topics")})
                realcase.pop("topics")
                for i in realcase:
                    if type(realcase[i]) == list:
                        realcase[i] = realcase[i][0]["title"]
        return casedict

    def todict(self, cases):
        for method in cases:
            for mcase in cases[method]:
                jslset = {OTHER, BODY, AST, PRETREATMENT, MARK}
                jslset = jslset.intersection(
                    {c for c in mcase if type(mcase[c]) == str})
                mcase.update({c: {}for c in mcase if mcase[c] == None})
                for c in mcase:
                    try:
                        if c in jslset:
                            mcase[c] = json.loads(mcase[c])
                    except JSONDecodeError:
                        print("请检查xmind:{}_{}\n{}".format(
                            method, mcase['title'], mcase[c]))

    def tojson(self, xmind: str, cases):
        path = ".".join([xmind.rsplit(".", 1)[0], "json"])
        with open(path, "w", encoding="utf-8") as jsonfile:
            jsonfile.write(json.dumps(cases, indent=4,
                           sort_keys=True, ensure_ascii=False))
