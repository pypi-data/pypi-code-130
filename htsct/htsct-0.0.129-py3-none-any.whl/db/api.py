import json
from typing import Callable, List
from requests_toolbelt import sessions
from htsct.constants import DB_URL

session = sessions.BaseUrlSession(base_url=DB_URL)
get, post, put, delete = session.get, session.post, session.put, session.delete


# ribbon
class Ribbon:
    getRibbon = lambda params: get("/ribbons", params=params).json()  # type: Callable[[dict],List[dict]]
    createRibbon = lambda data: post("/createRibbon",
                                     data=json.dumps(data)).json()  # type: Callable[[List[dict]],List[dict]]
    updateRibbon = lambda data: put("/updateRibbon",
                                    data=json.dumps(data)).json()  # type: Callable[[List[dict]],List[dict]]
    deleteRibbon = lambda id_: delete("/deleteRibbon", params={"id": id_}).json()  # type: Callable[[str],dict]
    getRibbonRunningStatus = lambda id_: get("/getRibbonRunningStatus",
                                             params={"id": id_}).json()  # type: Callable[[str],dict]
    updateRunningStatus = lambda params: put("/updateRunningStatus",
                                             params=params).json()  # type: Callable[[dict],dict]
    # info
    getAllInfo = lambda params: get("/getAllInfo", params=params).json()
    updateAllInfo = lambda data: put("/updateAllInfo", data=json.dumps(data)).json()


# C2db
class C2db:
    createC2db = lambda data: post("/createC2db",
                                   data=json.dumps(data)).json()  # type: Callable[[List[dict]],List[dict]]
    getC2db = lambda params: get("/queryC2db", params=params).json()  # type: Callable[[dict],List[dict]]

    # VaspInput
    createVaspInput = lambda data: post("/createVaspInput",
                                        data=json.dumps(data)).json()  # type: Callable[[dict],List[dict]]
    getVaspInput = lambda params: get("/queryVaspInput", params=params).json()  # Callable[[dict],dict]
    deleteVaspInput = lambda name: delete("/deleteVaspInput",
                                          params={"name": name}).json()  # Callable[[str],dict]
    updateVaspInput = lambda data: put("/updateVaspInput",
                                       data=json.dumps(data)).json()  # type: Callable[[List[dict]],List[dict]]


# Config
class Config:
    getConfig = lambda params: get("/config", params=params).json()  # type: Callable[[dict],List[dict]]
    setConfig = lambda data: post("/config",
                                  data=json.dumps(data)).json()  # type: Callable[[List[dict]],List[dict]]
    deleteConfig = lambda id: delete("/config", params={"id": id}).json()  # type: Callable[[str],dict]
    updateConfig = lambda data: put("/config",
                                    data=json.dumps(data)).json()  # type: Callable[[List[dict]],List[dict]]
    setActive = lambda id: put("/activeConfig", params={"id": id}).json()  # type: Callable[[str],dict]
    getActive = lambda: get("/activeconfig").json()


# VaspInputs
class VaspInputs:
    getVaspinputs = lambda params: get("/queryVaspInput", params=params).json()  # type: Callable[[dict],List[dict]]
    createVaspInputs = lambda data: post("/createVaspInput",
                                         data=json.dumps(data)).json()  # type: Callable[[dict],dict]
    deleteVaspInput = lambda name: delete("/deleteVaspInput",
                                          params={"name": name}).json()  # type: Callable[[str],dict]
    updateVaspInput = lambda data: put("/updateVaspInput",
                                       data=json.dumps(data)).json()  # type: Callable[[List[dict]],List[dict]]


# TaskLog
class TaskLog:
    getTaskLog = lambda params: get("/taskLog", params=params).json()  # type: Callable[[dict],List[dict]]
    setTaskLog = lambda data: post("/taskLog", data=json.dumps(data)).json()  # type: Callable[[List[dict]],List[dict]]


# functions
def updateInfo(key: str, value, limit=2000):
    """批量修改info"""
    infos = Ribbon.getAllInfo({"limit": limit})
    for info in infos:
        if info["info"][key] == value:
            info["info"][key] = value
    Ribbon.updateAllInfo(infos)
