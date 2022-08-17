import importlib
import os
import sys

import pytest

from swg2pyt.GlobalDict import GlobalDict

from .Executor import DESCRIPTION, PRETREATMENT, WHI, Executor

ENTRY_TEMPLATE = '\
import pytest\n\
from swg2pyt.ClassGenerator import ClassGenerator\n\
\n\
methoddict, traceexe = ClassGenerator("{}","{}").getall()\n'
DESCRIPTION_TEMPLATE = "\
'''\n    {}\
    \n\
    '''"
MARK_TEMPLATE = '\
@pytest.mark.{}\n'
METHOD_TEMPLATE = '\n\n\
{}\
def test_{}{}:\n\
    {}\n\
    traceexe["{}"].exe(methoddict["{}"], "{}", {})\n'


class ClassGenerator(object):
    inst = {}
    inited = {}
    swgs = []

    def __new__(cls, swgdir, casedir):
        if not cls.inst.get(swgdir):
            cls.inst[swgdir] = super().__new__(cls)
        return cls.inst[swgdir]

    def __init__(self, swgdir, casedir) -> None:
        if not ClassGenerator.inited.get(swgdir):
            self.locate_swg(swgdir)
            ClassGenerator.inited[swgdir] = True
            self.classdict = {}
            self.methoddict = {}
            self.cmc = {}
            self.traceexe = {}
            self.fixturedict = {}
            self.descdict = {}
            self.swgdir = swgdir
            self.casedir = casedir
            self.py_template = ENTRY_TEMPLATE.format(swgdir, casedir)
            # 遍历swagger文件夹，为每个api生成一个执行器Executor
            # 并更新self.xxxdict
            for swg in ClassGenerator.swgs:
                for v in swg.__dict__:
                    variable = swg.__getattribute__(v)
                    if type(variable).__name__ == "type":
                        variable = variable()
                        executor = Executor(variable, tuple([casedir]))
                        self.updatecmc(v, executor)
                        self.classdict[v] = variable
            ClassGenerator.swgs.clear()

    def locate_swg(self, swgdir):
        cwd, dirs, files = next(os.walk(os.getcwd(), topdown=True))
        for dir in dirs:
            absdir = os.path.join(cwd, dir)
            if ".swagger-codegen-ignore" in os.listdir(absdir) and dir == swgdir:
                if absdir not in sys.path:
                    sys.path.append(absdir)
                swg = __import__(
                    f"{swgdir}.swagger_client.api", fromlist=["api"])
                if swg not in ClassGenerator.swgs:
                    ClassGenerator.swgs.append(swg)
                if absdir in sys.path:
                    sys.path.remove(absdir)
                break

    def updatecmc(self, classname, executor):
        casedict = executor.cc.casedict
        for m in executor.methods:
            mkey = m.__name__.replace(WHI, "")
            cmethod = self.cmc.setdefault(classname, {})
            mcase = cmethod.setdefault(mkey, [])
            self.methoddict[f'{self.swgdir}_{mkey}'] = m
            self.traceexe[f'{self.swgdir}_{mkey}'] = executor
            cdm = casedict.get(mkey.replace(WHI, ""))
            if cdm:
                for c in cdm:
                    mcase.append(c)
                    casetitle = f'{mkey}_{c.get("title")}'
                    self.descdict[casetitle] = c.get(DESCRIPTION)
        defaultdesc = {d: d for d in self.descdict if self.descdict[d] is None}
        self.descdict.update(defaultdesc)

    def getall(self):
        methoddict = {}
        traceexe = {}
        for i in ClassGenerator.inst.values():
            methoddict.update(i.methoddict)
            traceexe.update(i.traceexe)
        return methoddict, traceexe

    def generate(self):
        genpath = os.path.join(os.getcwd(), self.casedir, "auto")
        if not os.path.exists(genpath):
            os.mkdir(genpath)
        self.tofile(genpath)
        return genpath

    def generate_and_run(self, pytest_argv=[]):
        pytest.main([self.generate()] + pytest_argv)

    def tofile(self, path):
        for apiclass in self.cmc:
            filecontent = ""
            for cmethod in self.cmc[apiclass]:
                for mcase in self.cmc[apiclass][cmethod]:
                    fixture = self.genfixture(mcase.get(PRETREATMENT))
                    ctitle = f'{cmethod.replace(WHI,"")}_{mcase["title"]}'
                    dt = self.descdict[ctitle].replace("\n", "\n    ")
                    dt = DESCRIPTION_TEMPLATE.format(dt)
                    strfixture1 = str(tuple(fixture)).replace("'", "")
                    strfixture2 = str({f'"{ft}"': ft for ft in fixture})
                    strfixture2 = strfixture2.replace("'", "")
                    mks = mcase.get("mark")
                    mkt = "".join(
                        [MARK_TEMPLATE.format(mk)for mk in mks] if mks else "")
                    mtformat = (mkt, ctitle, strfixture1, dt, f'{self.swgdir}_{cmethod}',
                                f'{self.swgdir}_{cmethod}', mcase["title"], strfixture2)
                    mt = METHOD_TEMPLATE.format(*mtformat)
                    filecontent += mt
            if filecontent:
                apipath = os.path.join(path, f"test_{apiclass}.py")
                with open(apipath, "w", encoding="utf-8")as test_newpy:
                    test_newpy.write(self.py_template+filecontent)
        with open(os.path.join(path, "marks"), "w+", encoding="utf-8")as markfile:
            marks = [mark for mark in GlobalDict()["marks"]]
            markfile.write(",".join(marks))

    def genfixture(self, ptm):
        rt = tuple()
        if ptm:
            fixture = ptm.get("fixture")
            if fixture:
                rt = fixture
        return rt
