import inspect
import time
from copy import deepcopy
from json.decoder import JSONDecodeError
from typing import Generator

import jmespath

from .Asserter import INVALIDPATH, ast
from .CaseCollector import (AST, BODY, DESCRIPTION, OTHER, PRETREATMENT,
                            CaseCollector)
from .GlobalDict import GlobalDict
from .Pretreator import prt

EMPTYCASE = False
NOTINXMIND = True
KEYERROR = False

WHI = "_with_http_info"
GD = GlobalDict()


class Executor:
    def __init__(self, obj: object, path: tuple):
        """
        获取一个 swagger_client.api 对象的用例执行器
        :param obj: swagger_client.api
        :return: 用例执行器
        """
        self.obj = obj
        attrs = [obj.__getattribute__(d)for d in obj.__dir__()if d[:2] != "__"]
        self.methods = [a for a in attrs if type(a).__name__ == "method"]
        self.grep()
        self.cc = CaseCollector(*path)
        self.c = None

    def grep(self):
        self.methods = [m for m in self.methods if m.__name__.endswith(WHI)]

    def exe(self, method, casekey, fixture):
        self.asts = {}
        methodname = method.__name__.replace(WHI, "")
        current = f'test_{methodname}_{casekey}'
        GD["nextitem"] = current
        if not methodname in self.cc.casedict:
            assert NOTINXMIND
        if not self.cc.casedict[methodname]:
            assert EMPTYCASE, "case is empty"
        if casekey not in [c['title'] for c in self.cc.casedict[methodname]]:
            assert KEYERROR, 'casekey error'
        for c in self.cc.casedict[methodname]:
            if c["title"] == casekey:
                self.c = deepcopy(c)
                break
        byforce = GD.setdefault("byforce", None)
        if current not in GD.setdefault("casershs", {}) or byforce:
            self.pretreat(current, self.c, fixture)
            self.paramcall(self.c, method, current)
        ast_current = GD.setdefault("asts", {})[current]
        retry = ast_current.get("retry") or 1
        while retry:
            retry -= 1
            try:
                rsh_current = GD.setdefault("casershs", {})[current]
                ast(current, ast_current, rsh_current, fixture)
                break
            except AssertionError as ae:
                time.sleep(3)
                if retry:
                    GD.setdefault("casershs", {})[current] = []
                    self.paramcall(self.c, method, current)
                else:
                    raise ae

    def paramcall(self, mcase, method, current):
        body, bodygener, nextbody = self.parametrize(mcase.get(BODY))
        other, othergener, nextother = self.parametrize(mcase.get(OTHER))
        rsh = self.decocall(method, body, other)
        self.setback(mcase.get(BODY), bodygener)
        self.setback(mcase.get(OTHER), othergener)
        GD.setdefault("casershs", {}).setdefault(current, []).append(rsh)
        GD.setdefault("asts", {})[current] = mcase[AST]
        if nextbody | nextother:
            self.paramcall(mcase, method, current)

    def parametrize(self, source, rootpath=[]):
        generators = {}
        havenext = False
        if type(source) == dict:
            for d in source:
                if isinstance(source[d], Generator):
                    generators[source[d]] = rootpath+[d]
                    source[d], hn = next(source[d])
                    havenext = havenext | hn
                else:
                    gnm = self.parametrize(source[d], rootpath+[d])
                    generators.update(gnm[0])
                    havenext = havenext | gnm[1]
        elif type(source) == list:
            for index, l in enumerate(source):
                if isinstance(l, Generator):
                    generators[l] = rootpath+[index]
                    source[index], hn = next(l)
                    havenext = havenext | hn
                else:
                    gnm = self.parametrize(l, rootpath+[index])
                    generators.update(gnm[0])
                    havenext = havenext | gnm[1]
        if rootpath:
            return generators, havenext
        else:
            return deepcopy(source), generators, havenext

    def setback(self, source, generators):
        for g in generators:
            endpath = generators[g].pop()
            parent = source
            if generators[g]:
                parent = jmespath.search(".".join(generators[g]), source)
            parent[endpath] = g

    def decocall(self, method, reqdata, otherdata):
        '''
        若reqdata不为空，置于可变参数元组首位
        尔后根据函数签名，从otherdata中提取参数值，置于可变参数元组末尾
        '''
        print("\n", reqdata, otherdata)
        req_and_other = [deepcopy(reqdata), deepcopy(otherdata)]
        args = tuple()
        rt = []
        if reqdata is not None:
            args = tuple([reqdata])
        signature = str(inspect.signature(method))[1:-1].split(",")
        signature = tuple(i.strip() for i in signature)[int(bool(reqdata)):-1]
        if otherdata:
            args = args+tuple(otherdata.pop(sig) for sig in signature)
        if otherdata:
            rt = list(method(*args, **otherdata, _preload_content=False))
        else:
            rt = list(method(*args, _preload_content=False))
        rt.extend(req_and_other)
        return rt

    def pturl(self, casekey, urlptm, fixture):
        for ptm in urlptm:
            self.obj.api_client._path_params = {
                ptm: prt(casekey, urlptm[ptm], fixture)}

    def ptfixture(self, casekey, fixtureptm, fixture):
        pass

    def pretreat(self, casekey, c, fixture):
        pretreatments = self.directpt(casekey, c.get(PRETREATMENT), fixture)
        for pretreatment in pretreatments:
            p_root = None
            p_parent = None
            for ptm in pretreatments[pretreatment]:
                p_root = c[pretreatment]
                p_family = str(ptm).rsplit(".", 1)
                p_child = p_family.pop()
                if p_family:
                    p_parent = jmespath.search(p_family.pop(), p_root)
                else:
                    p_parent = p_root
                if not p_parent:
                    assert False, INVALIDPATH.format(str(ptm))
                if "replace" in pretreatments[pretreatment][ptm]:
                    pretreatments[pretreatment][ptm]["replace"].insert(
                        0, p_parent[p_child])
                try:
                    p_parent[p_child] = prt(casekey,
                                            pretreatments[pretreatment][ptm], fixture)
                except KeyError:
                    assert KEYERROR, "KeyError"
            c[pretreatment] = p_root

    def ptheaders(self, casekey, headersptm, fixture):
        for ptm in headersptm:
            self.obj.api_client.set_default_header(
                ptm, str(prt(casekey, headersptm[ptm], fixture)))

    def ptcase(self, casekey, caseptm, fixture):
        prt(casekey, {"precase": caseptm}, fixture)

    def ptifprecase(self, casekey, ifcaseptm, fixture):
        prt(casekey, {"ifprecase": ifcaseptm}, fixture)

    def directpt(self, casekey, pretreatments, fixture):
        rt = pretreatments
        ptdict = {"url": self.pturl, "fixture": self.ptfixture,
                  "headers": self.ptheaders, "precase": self.ptcase,
                  "ifprecase": self.ptifprecase}
        rt.update({pt: {} for pt in ptdict if pt not in rt})
        ptdict["ifprecase"](casekey, rt.pop("ifprecase"), fixture)
        ptdict.pop("ifprecase")
        # 涉及跳过用例，优先级高
        for pt in ptdict:
            ptdict[pt](casekey, rt.pop(pt), fixture)
        return rt
