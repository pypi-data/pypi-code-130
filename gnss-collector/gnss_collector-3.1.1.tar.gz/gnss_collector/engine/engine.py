# stdlilb python
import asyncio
import concurrent.futures
import datetime
import functools
import itertools
import logging
import multiprocessing
import multiprocessing as mp
import os
import socket
import sys 
import time
import traceback
import httpx
import ujson as json
from asyncio import shield, wait_for
from datetime import timedelta, datetime
from dataclasses import (field, dataclass)
from functools import reduce
from ipaddress import ip_address
from pathlib import Path
from tasktools.taskloop import TaskLoop
from typing import List, Dict, Union, overload, Any, Tuple
from collections.abc import Iterable
import inspect

# contrib 
from rethinkdb import RethinkDB
from rich import print

# contrib: share exceptions as message
from tblib import pickling_support
pickling_support.install()

# contrib @dpineda
from networktools.time import timestamp, now
from networktools.colorprint import gprint, bprint, rprint
from networktools.library import my_random_string
from networktools.library import check_type
from networktools.library import (pattern_value,
                                  fill_pattern, context_split,
                                  gns_loads, gns_dumps)
from networktools.messages import MSGException, MessageLog

from networktools.time import gps_time, now
from basic_queuetools.queue import read_queue_gen
from basic_logtools.filelog import LogFile as FileLog
from crb import RingBuffer, Data 
from dataprotocols import BaseProtocol, Gsof, Eryo
from data_rdb import Rethink_DBS
import time

# Tasktools
from tasktools.taskloop import coromask, renew, simple_fargs, simple_fargs_out
from tasktools.scheduler import TaskScheduler
# GSOF Protocol
from .steps import (CollectSteps as CSteps, DBSteps, Logger, ORMSteps,
                    ControlActions)
# DBS Rethinkdb
# same module
from .subscribe import SubscribeData
from .message import MessageManager

# from .async_mongo import AsyncMongoDB

rdb = RethinkDB()

def rdbnow():
    return rdb.iso8601(now().isoformat())

# base settings
try:
    from .conf.settings import COMMANDS, groups, dirs

except:
    from conf.settings import COMMANDS, groups, dirs

DATA_KEYS = {"DT_GEN":"dt_gen","DELTA_TIME":"latency"}
SLEEP = 0.0001

def load_stations(url):
    print(now(),f"URL-> {url}/stations")
    u = httpx.get(f"{url}/stations")
    while u.status_code != httpx.codes.OK:
        u = httpx.get(f"{url}/stations")
        time.sleep(SLEEP)
    return json.loads(u.content)


def load_databases(url):
    print(now(), f"URL-> {url}/databases")
    u = httpx.get(f"{url}/databases")
    while u.status_code != httpx.codes.OK:
        u = httpx.get(f"{url}/databases")
        time.sleep(SLEEP)
    return json.loads(u.content)


def active_server(url):
    print(now(), f"URL-> {url}/servers")
    servers = httpx.get(f"{url}/servers")
    print(servers)
    u = []
    while servers.status_code != httpx.codes.OK:
        servers = httpx.get(f"{url}/servers")
        time.sleep(SLEEP)
    u = [s for s in json.loads(servers.content) if s["activated"]] 
    return u


def deactive_server(server_name, datadb, log_path='~/log'):
    print(now(), f"URL-> {url}/servers")
    servers = httpx.get(f"{url}/servers")
    u = []
    while servers.status_code != httpx.codes.OK:
        servers = httpx.get(f"{url}/servers")
        time.sleep(SLEEP)
    u = [s for s in json.loads(servers.content) if not s["activated"]] 
    return u


"""
Engine basic for collector
"""


class Aux:
    async def stop(self):
        pass


Value = Union[str, int, float, datetime]

ORM_URL = os.getenv("ORM_SERVICE_HOST",'http://10.54.218.196')

@dataclass
class Engine(TaskScheduler):
    """
    A class for data adquisition, receive messages from messegeser and
    save data on db

    """
    # ARGS: ordered and obligatory
    set_queue: List[mp.Queue]
    sleep_time: int
    est_by_proc: int
    stations: Dict[str, Dict[str, Value]]
    dbtype: Dict[str, Dict[str, Value]]
    protocol: Dict[str, Dict[str, Value]]
    status_sta: Dict[str, bool] # ok
    db_instances_sta: Dict[str,str] # ok
    status_conn: Dict[str, bool] # ok 
    db_data: Dict[str,Dict[str,str]] # can be better
    dump_list: Dict[str,str]
    proc_tasks: Dict[str,str]
    assigned_tasks: Dict[str,str]
    free_ids: Dict[str,str]
    wait: Dict[str,str]
    inc_msg: Dict[str,str]
    ids:List[str]
    idd:List[str]
    ipt:List[str]
    idm:List[str]
    ico:List[str]
    changes: Dict[str,str]
    gsof_timeout:int 
    sta_init: Dict[str,str]
    db_init:Dict[str, bool]
    db_connect:Dict[str, bool]
    status_tasks:Dict[str, Dict[str,str]]
    nproc:int
    idc: Dict[str,str]

    # KWARGS
    rdb_address: str = field(default_factory= lambda: "localhost")
    uin: int= 6
    
    args:List[Any] =  field(default_factory=list)
    kwargs:Dict[str, Any] = field(default_factory=dict)
    log_path: Path = Path.home() / "collector_log"
    server: str = "atlas"
    dt_criteria: int = 4
    raise_timeout: bool = False
    timeout: int = 15
    dbdata: Dict[str, Any] = field(default_factory=dict)
    collect_objects:Dict[str, BaseProtocol] = field(default_factory=lambda: dict(
            GSOF=Gsof,
            ERYO=Eryo
        ))
    database_objects:Dict[str, Any] = field(default_factory=lambda: dict(
            RethinkDB=Rethink_DBS,
            #Mongo=AsyncMongoDB
        ))
    folder:str = 'data'
    sep:str = '|'
    rethinkdb:Dict[str,  Any] = field(default_factory=dict)
    log_manager:Dict[str, str] = field(default_factory=dict)

    def __post_init__(self):
        self.set_queue_elems()
        self.set_stats_params()
        args = []
        kwargs_extra = {
            'ipt': self.ipt,
            'ico': self.ico,
            'assigned_tasks': self.assigned_tasks,
            'nproc': self.nproc,
            'sta_init': self.sta_init
        }
        self.server_name = self.kwargs.get('server', "atlas")
        self.log_path = Path(self.kwargs.get('log_path', '~/log'))
        self.timeout = self.kwargs.get("timeout", 5)
        self.datadb = self.kwargs.get("dbdata", {})
        self.raise_timeout = self.kwargs.get("raise_timeout", False)

        self.kwargs.update(kwargs_extra)
        super().__init__(*self.args, **self.kwargs)
        #
        coros_callback_dict = {
            'run_task': self.process_data,
        }
        self.set_new_run_task(**coros_callback_dict)
        self.instances = dict()
        self.db_instances = dict()
        # more processing
        self.nproc = mp.cpu_count()
        # list of objects
          # LOAD DATA TO STATIONS
        self.tasks = dict()
        self.first_time = dict()
        # set the main task
        # must be in every new process ATENTION!
        self.message_manager = MessageManager(self)
        self.subscribe_data = SubscribeData(
            'collector_subscribe', self.queue_t2n)
        self.LOG_STA = check_type(os.environ.get('LOG_STA', False))
        ###############################################
        self.server = active_server(ORM_URL)
        # table status
        self.stats = "STATIONS_STATS"


    def set_queue_elems(self):
        self.rq = self.set_queue[0]
        self.wq = self.set_queue[1]
        self.queue_process = self.set_queue[2]
        self.queue_ans_process = self.set_queue[3]
        self.queue_db = self.set_queue[4]
        self.queue_log = self.set_queue[-1]
        self.queue_n2t = self.rq
        self.queue_t2n = self.wq

    async def send_log(self, coroname, level, message, exc):
        msg = MessageLog(rdbnow(), coroname, level, message, MSGException(*exc))
        self.queue_log.put({"log":[msg.rdb]})
        
    def set_stats_params(self):
        # set ring buffer control
        self.mu = 0.5
        self.factor = 0.8
        self.sigma = 0.3
        self.buffer_size = 120*60
        self.u_base = self.mu + self.factor * self.sigma 
        self.acc = 15

    def set_datafolder(self, folder):
        """
        Set another, different, folder to save data
        """
        self.folder = folder

    def set_id(self, lista):
        """
        Defines a new id for stations, check if exists
        """
        ids = my_random_string(self.uin)
        while True:
            if ids not in lista:
                lista.append(ids)
                break
            else:
                ids = my_random_string(self.uin)
        return ids

    def set_ids(self):
        """
        Defines a new id for stations, check if exists
        """
        return self.set_id(self.ids)

    def set_idd(self):
        """
        Defines a new id for stations, check if exists
        """
        return self.set_id(self.idd)

    def set_ipt(self, ipt=""):
        """
        Defines a new id for relation process-collect_task, check if exists
        """
        if ipt:
            self.ipt.append(ipt)
        else:
            ipt = self.set_id(self.ipt) 
        return ipt

    def set_ico(self, ico):
        """
        Defines a new id for task related to collect data insice a worker, check if exists
        """
        if ico:
            self.ipt.append(ico)
        else:
            ico = self.set_id(self.ipt) 

        return ico

    def set_idm(self):
        """
        Defines a new id for relation incoming messages, check if exists
        """
        return self.set_id(self.idm)

    def load_stations(self):
        u = load_stations(ORM_URL)  # ok
        for m in u:
            keys = ['id', 'code', 'db', 'dblist', 'ecef_x', 'ecef_y', 'protocol_host',
                    'ecef_z', 'port', 'protocol', 'host', 'dbname']
            try:
                station = dict(
                    id=m['id'],
                    code=m['code'],
                    name=m['name'],
                    port=m["port"],
                    ecef_x=m["position"]['ecef']["x"],
                    ecef_y=m["position"]['ecef']['y'],
                    ecef_z=m["position"]['ecef']['z'],
                    protocol=m['protocol'],
                    protocol_host=m['protocol_host'],
                    position=m["position"],
                    on_db=True
                )
                (ids, sta) = self.add_station(**station)
                # print(station)
            except Exception as exc:
                raise exc

    def add_station(self, **sta):
        """
        Add station to list for data adquisition
        """
        try:
            keys = ['id',
                    'code',
                    'name',
                    'ecef_x',
                    'ecef_y',
                    'ecef_z',
                    'host',
                    'port',
                    'interface_port',
                    'db',
                    'dblist',
                    'protocol',
                    'protocol_host',
                    'on_db',
                    'position',
                    'ipt']
            ids = self.set_ids()

            # if ids in self.enqueued:
            #     self.enqueued.remove(ids)
            # self.enqueued.add(ids)

            station = dict(ids=ids)

            for k in keys:
                if k in sta.keys():
                    if k == 'protocol':
                        station[k] = sta.get(k, 'None').upper()
                    else:
                        station[k] = sta.get(k, None)
                else:
                    if k == 'host':
                        station[k] = 'localhost'
                    elif k == 'port' or k == 'interface_port':
                        station[k] = 0
                    elif k in  [f'ecef_{v}' for v in ("x", "y", "z")]:
                        station[k] = 0
                    else:
                        station[k] = None
            self.stations.update({ids: station})
            self.status_sta.update({ids: False})
            self.first_time.update({ids: True})
            return (ids, sta)
        except Exception as ex:
            raise ex

    def update_station(self, ids, **sta):
        """
        Add station to list for data adquisition
        """
        try:
            keys = ['id',
                    'code',
                    'name',
                    'ecef_x',
                    'ecef_y',
                    'ecef_z',
                    'host',
                    'port',
                    'interface_port',
                    'db',
                    'dblist',
                    'protocol',
                    'protocol_host',
                    'on_db',
                    'ipt']
            station = dict(ids=ids)

            for k in keys:
                if k in sta.keys():
                    if k == 'protocol':
                        station[k] = sta.get(k, 'None').upper()
                    else:
                        station[k] = sta.get(k, None)
                else:
                    if k == 'host':
                        station[k] = 'localhost'
                    elif k in {'port', 'interface_port', 'st_port'}:
                        station[k] = 0
                    elif k in  [f'ecef_{v}' for v in ("x", "y", "z")]:
                        station[k] = 0
                    else:
                        station[k] = None
            self.stations.update({ids: station})
            self.status_sta.update({ids: False})
            self.first_time.update({ids: True})
            return (ids, sta)
        except Exception as ex:
            raise ex


    def get_stations_keys(self):
        return list(self.stations.keys())

    def load_databases(self):
        u = load_databases(ORM_URL)
        # ok
        groups = {}
        for m in u:
            kwargs = dict(
                id=m['id'],
                path=m['path'],
                host=m['host'],
                port=m['port'],
                user=m['user'],
                passw=m['passw'],
                info=m['info'],
                dbname=m['dbname'],
                address=(m['host'], m['port']),
                log_path=self.log_path/"rdb",
                on_db=True)
            groups[(m["host"], m["port"])] = kwargs
        #print("Different db destinies", len(groups), groups.keys())
        for opts in groups.values():
            self.new_datadb(**opts)
        print("Database data")
        print(self.db_data)

    def new_datadb(self, **kwargs):
        """
        Here you give the argument for every type engine for store data colected
        and instantiate the db for enable query on that
        """
        # generate a idd= database instance identifier
        try:
            keys = [
                'id',
                'user',
                'passw',
                'code',
                'host',
                'port',
                'dbname',
                'path',
                'data_list',
                'type_name',
                'dbname',
                'type_db,'
                'url',
                'info',
                'address',
                'on_db',
                'log_path']
            uin = 4
            idd = self.set_idd()
            # create namedtuple/dataclass 
            db_data = dict(idb=idd, args={})
            for k in keys:
                if k in keys:
                    if k in kwargs.keys():
                        db_data['args'][k] = kwargs[k]
                    else:
                        if k == 'localhost':
                            db_data['args'][k] = 'localhost'
                        elif k == 'port':
                            db_data['args'][k] = 0
                        else:
                            db_data['args'][k] = ''
            self.db_data[idd] = db_data
            return idd, db_data
        except Exception as ex:
            raise ex

    def mod_station(self, ids, key, value):
        """
        Modify some value in station info

        """
        if key in self.stations.get(ids).keys():
            self.stations[ids][key] = value

    def del_station(self, ids):
        """
        Delete a station from list
        """
        del self.stations[ids]
        del self.status_sta[ids]
        del self.status_conn[ids]
        del self.instances[ids]
        k = self.ids.index(ids)
        del self.ids[k]

    def save_db(self, dbmanager, tname, args):
        """
        Save data to tname with args
        """
        # TODO: actualizar la lista de campos port table
        # TODO: añadir serverinstance
        input_args = dict(
            station=[
                'code',
                'name',
                'position_x',
                'position_y',
                'position_z',
                'host',
                'port',
                'interface_port',
                'db',
                'protocol'],
            dbdata=[
                'code',
                'path',
                'host',
                'port',
                'user',
                'passw',
                'info',
                'dbtype'],
            dbtype=['typedb', 'name', 'url', 'data_list'],
            protocol=['name', 'red_url', 'class_name', 'git_url']
        )
        name_args = input_args[tname]
        my_args = []
        id_instance = None
        if dbmanager == None:
            dbmanager = SessionCollector()
            instance = object
            if tname == 'station':
                instance = dbmanager.station(**args)
            elif tname == 'dbdata':
                instance = dbmanager.dbdata(**args)
            elif tname == 'dbtype':
                instance = dbmanager.dbtype(**args)
            elif tname == 'protocol':
                instance = dbmanager.protocol(**args)
            id_instance = instance.id
            return id_instance

    def save_station(self, ids):
        """
        Save station to database
        """
        # check if exists
        # if exist get data and compare
        # then update
        # if not, save
        pass

    def drop_station(self, ids):
        """
        Delete station from database
        """
        # get id from station ids
        # delete on database
        pass

    def del_db(self, varlist):
        """
        Delete element from database identified by idx in varlist
        """
        pass
###############

    def add_sta_instance(self, ids, loop):
        """
        Crear la instancia que accederá a los datos
        a través del socket
        """
        print(self.stations)
        station =  self.stations.get(ids)
        if station:
            protocol = self.stations[ids]['protocol']
            kwargs = self.stations[ids]
            self.stations[ids]['on_collector'] =  True
            kwargs['code'] = self.stations[ids]['code']
            kwargs['host'] = self.stations[ids]['protocol_host']
            kwargs['port'] = self.stations[ids]['port']
            kwargs['sock'] = None
            kwargs['timeout'] = self.gsof_timeout
            kwargs["raise_timeout"] = False
            kwargs['loop'] = loop
            kwargs['log_path'] = self.log_path/"protocols"
            instance = self.collect_objects[protocol](**kwargs)
            code = kwargs["code"]
            table_name = f"{code}_{protocol}"

            print("Instancia de estacion", instance)
            return instance, table_name
        else:
            print("No station")
            return (None, None)

    def set_status_sta(self, ids:str, value:bool)->None:
        if isinstance(value, bool):
            self.status_sta[ids] = value

    def set_status_conn(self, ids:str, value:bool)->None:
        if isinstance(value, bool):
            self.status_conn[ids] = value

    def del_sta(self, ids:str):
        del self.instances[ids]
        del self.status_sta[ids]
        del self.status_conn[ids]
        del self.first_time[ids]
        # del self.db_instances[ids]
        del self.ids

    def get_tname(self, varname):
        assert isinstance(varname, str)
        if varname == 'STA' or varname == 'STATION':
            return 'station'
        elif varname == 'DB' or varname == 'DBDATA':
            return 'database'
        elif varname == 'PROT' or varname == 'PROTOCOL':
            return 'protocol'
        elif varname == 'DBTYPE':
            return 'dbtype'
        else:
            return None

    def get_id_by_code(self, varname, code):
        if varname == 'STATIONS':
            this_var = self.stations
            for k in this_var.keys():
                if this_var[k]['code'] == code:
                    return k

        elif varname == 'DBDATA':
            this_var = self.db_data
            # variable in function dbtype
            for k in this_var.keys():
                # code_r=''
                try:
                    if this_var[k]['args']['code'] == code:
                        return k
                except Exception as ex:
                    raise ex

    def get_var(self, varname):
        varin = ''
        if varname == 'STA':
            varin = self.stations
        elif varname == 'DB':
            varin = self.db_data
        else:
            varin = None
        return varin

    async def connect(self, ids):
        if self.status_sta[ids]:
            await self.instances[ids].connect()
            self.set_status_conn(ids, True)
            self.set_status_sta(ids, False)
            self.first_time[ids] = False

    async def stop(self, ipt, ids):
        if self.status_sta[ids]:
            icos = [ico_dict for ipt, ico_dict in self.assigned_tasks.items()]
            ico_list = []
            for ico_dict in icos:
                ico_list += [ico for ico, _ids in ico_dict.items()
                             if _ids == ids]
            for ico in ico_list:
                self.unset_sta_assigned(ipt, ico, ids)
                instance_obj = self.instances.get(ids, Aux())
                await instance_obj.stop()
                self.set_status_conn(ids, False)
                self.set_status_sta(ids, False)

    async def reset_station_conn(self, sta_insta, ids, idc):
        self.set_status_sta(ids, False)
        self.set_status_conn(ids, False)
        self.first_time[ids] = True       
        v = 1
        message = ""
        if idc:
            try:
                await sta_insta.close(idc)
                message = f"Station {sta_insta.station} closed at {idc}"
            except Exception as e:
                print("sta insta yet closed")
            except asyncio.TimeoutError as te:
                print("sta insta yet closed")
        return message, logging.INFO

    def connect_to_sta(self, ids):
        return self.sta_init[ids] and not self.status_conn[ids] and self.first_time[ids]

    def is_connected(self, ids):
        return self.sta_init[ids] and self.status_conn[ids] and not self.first_time[ids]        

    def add_db_instance(self, ipt):
        """
        Create a new instance for ending database to save the raw data

        """
        try:
            if self.db_data:
                rdbs_destinies = [key for key in self.db_data.keys()]
                key_data = rdbs_destinies.pop()
                data = self.db_data.get(key_data)
                name_db = data["args"]['dbname']
                # name_db debe ser el tipo de database
                object_db = self.database_objects["RethinkDB"]
                data.update({
                    "dbname": data["args"]["dbname"],
                    'address': data["args"]["address"],            
                    'hostname': 'atlas'})
                db_insta = object_db(**data)
                self.rethinkdb[ipt] = False
                self.db_init[ipt] = True
                self.db_connect[ipt] = True
                #if data['name'] == 'RethinkDB':
                self.rethinkdb[ipt] = True

                self.db_instances[ipt]  = db_insta

                return db_insta 
            else:
                print("Ipt not in DB_DATA")
                return None
        except Exception as ex:
            print(f"Error creando instancia database {self.db_data}")
            raise ex


    def db_task(self):
        # enable db task
        # Queue log join
        queue_log = asyncio.Queue()        
        loop = asyncio.get_event_loop()
        queue_db = self.queue_db
        control = {f"DB_{i}":DBSteps.CREATE for i in range(24)}        
        counter = {}
        task_name = f"db_task"
        ipt = "DB_PROCESS"
        flags = {key:True for key in control}
        db_instances = {}
        assigned = {key:{} for key in control}
        backup = {key:{} for key in control}
        db_args = [ipt, control, queue_db, db_instances,
                   counter, now(), now(), flags, assigned, backup, queue_log]
        db_task = TaskLoop(self.db_work, db_args, {"last_dataset":{}},
                           name=task_name)
        db_task.set_name(f"db_task_{ipt}")
        db_task.create()

        # Queue log join

        args = ["db_task_log", queue_log,]
        task_name = f"queue_log_join:{ipt}"
        task_db = TaskLoop(
            self.queue_log_join,
            args,
            {},
            **{"name": task_name})
        task_db.set_name(task_name)
        task_db.create()
        
        # db task to receive and send to pool rdb

        
        if not loop.is_running():
            loop.run_forever()


    async def db_work(self, ipt, control, queue_db, 
                      db_instances, counter,
                      last_data, last_time, flags, assigned, backup,
                      queue_log, **kwargs):
        """
        TODO: Control exceptions
        """
        # task_name = asyncio.Task.current_task()
        level = Logger.ERROR
        messages = []
        message = ""
        kwargs["dataset"] = []
        last_dataset = kwargs["last_dataset"]
        now_check = now()
        task_name = f"db_task_{ipt}"
        loop = asyncio.get_event_loop()
        coroname = "db_work"
        exc = MSGException()
        control_changes = {}
        cnow = now()
        free = set()
        

        for key, futures in assigned.items():
            db_insta = db_instances.get(key)
            task_group = all(map(lambda f:f.done(), futures.values()))
            falses = {t:f for t,f in futures.items() if not f.done()}
            if task_group:
                flags[key] = True
                free.add(key)
            elif falses:  
                tosend = {}
                for table_name, future in falses.items():
                    bk = backup.get(key,{}).get(table_name)
                    time = bk.get("time")
                    dataset = bk.get("dataset")
                    if (not future.done()) and (cnow >= time +timedelta(seconds=15)):
                        await db_insta.close()
                        future.cancel()
                        tosend[table_name] = dataset
                        #await queue_db.put([])
                        # TODO
                        control[key] = DBSteps.CONNECT
                        exc = MSGException()
                        try:
                            future.exception()
                        except Exception as e:
                            exc = MSGException(*sys.exc_info())
                            message  = f"Task cancelled for {key}->{table_name}"
                            level = Logger.ERROR                            
                            messages.append(MessageLog(rdbnow(),coroname, level, message, exc))                            

                if tosend:
                    queue_db.put(tosend)
        for key in free:
            assigned[key] = {}

        for key, dbcontrol in control.items():
            db_insta = db_instances.get(key)
            if dbcontrol == DBSteps.CREATE and db_insta:
                if db_insta:
                    await db_insta.close()
                    del db_insta
                db_insta = None
                message = f"Deleted weird db instance at ipt {ipt}, db {key}"
                level = Logger.WARNING
                messages.append(MessageLog(rdbnow(),coroname, level, message, exc))

        for key, dbcontrol in control.items():
            #print("KEY", key,"CONTROL", dbcontrol)
            db_insta = db_instances.get(key)
            if dbcontrol == DBSteps.CREATE or not db_insta:
                db_insta = self.add_db_instance(ipt)
                db_instances[key] =  db_insta
                kwargs["instance"] = db_insta
                if db_insta:
                    control_changes[key] = DBSteps.CONNECT
                    message = f"RDB  {db_insta} at {ipt} created and passed to connect, db {key}"
                else:
                    message = f"RDB  {db_insta} at {ipt} can't created and try to recreate, db {key}"
                    level = Logger.WARNING
                    rprint("cannot create db object")
                #messages.append((level, message, {}))
                messages.append(MessageLog(rdbnow(), coroname, level, message, exc))

        control.update(control_changes)
        #print({k:db.active for k, db in db_instances.items()})

        for key, dbcontrol in control.items():
            db_insta = db_instances.get(key)
            if db_insta and dbcontrol == DBSteps.CONNECT:
                if not db_insta.active:
                    exc = MSGException()
                    try:
                        address = db_insta.client_address
                        if db_insta.active:
                            await db_insta.close()
                            db_insta.clean_client()

                        future = asyncio.create_task(db_insta.async_connect())
                        stage = "connect"

                        # await queue_control.put((
                        #     task_name, 
                        #     now(), 
                        #     stage, 
                        #     future))

                        coro = await wait_for(
                            shield(future), 
                            timeout=20)

                        await asyncio.shield(db_insta.list_dbs())
                        await asyncio.shield(db_insta.create_db(db_insta.default_db))
                        await asyncio.shield(db_insta.list_tables())

                        
                        message = f"RDB {db_insta} at {ipt} was connected, then passed to save data, db {key}"
                        level = Logger.INFO
                        control_changes[key] = DBSteps.SAVE
                    except asyncio.CancelledError as e:
                        exc = MSGException(*sys.exc_info())                        
                        message = f"RDB {db_insta} at {ipt} has canceled task, but protected by shield"
                        level = Logger.ERROR
                        control_changes[key] = DBSteps.CONNECT
                        gprint(f"Reconnect to db  IPT -> {ipt}")
                        await db_insta.close()
                        messages.append(MessageLog(rdbnow(), coroname, level, message, exc))
                        
                    except Exception as e:
                        exc = MSGException(*sys.exc_info())
                        message = f"RDB  {db_insta} at {ipt} has an exception {e}"
                        level = Logger.CRITICAL
                        control_changes[key] = DBSteps.CONNECT
                        gprint(f"Exception connecting to db  IPT -> {ipt}, {e}")
                        await asyncio.sleep(3)
                        await db_insta.close()
                        messages.append(MessageLog(rdbnow(), coroname, level, message, exc))

                    #print(now(),f"{ipt} Rethinkdb connection", db_insta.client_address)
                    #messages.append((level, message, exc))
                    messages.append(MessageLog(rdbnow(), coroname, level, message, exc))
                    
                else:
                    exc = MSGException()
                    message = f"At {ipt} tried to connect but active {db_insta.active}"
                    level = Logger.WARNING
                    #messages.append((level, message, exc))
                    messages.append(MessageLog(rdbnow(), coroname, level, message, exc))
                    
                    control_changes[key] = DBSteps.SAVE
                    
        control.update(control_changes)
        tasks = []
        for key, dbcontrol in control.items():
            db_insta = db_instances.get(key)
            db_flag = flags.get(key, True)
            opts = {}
            if db_insta.active and dbcontrol == DBSteps.SAVE and (not queue_db.empty()) and db_flag:
                """
                Leer la cola queue que debe ser una tupla (table_name,
                data)
                chequear si existe, si no crear
                """
                dataset = {}
                for i in range(queue_db.qsize()):
                    item = queue_db.get()
                    for t, array in item.items():                        
                        if t not in dataset:
                            dataset[t] = []
                        dataset[t] += array
                queue_db.task_done()

                i = 0
                # maybe group by table_name and then save as bulk
                flags[key] = False
                opts[key] = True
                assigned[key] = {}
                
                for table_name, items in dataset.items():
                    if table_name not in db_insta.tables:
                        create = await db_insta.create_table(table_name)
                        await db_insta.create_index(
                            table_name,
                            index='DT_GEN')
                    
                    message = ""
                    dataset = items
                    if table_name:
                        exc = MSGException()
                        try:
                            # print(now(), f"Saving to {table_name}"+\
                            #       f"#{len(dataset)},
                            #       {db_insta.client_address}")
                            
                            last_dt_gen = last_dataset.get(table_name,rdbnow() - timedelta(seconds=5))
                            dt_gens = [elem.get("DT_GEN") for elem in
                                       dataset if
                                       elem.get("DT_GEN")>last_dt_gen]
                            last_dt = max(dt_gens)
                            
                            filtered_dataset = [d for d in dataset if
                                                d["DT_GEN"] in dt_gens]

                            future = asyncio.create_task(
                                db_insta.save_data(
                                    table_name, 
                                    filtered_dataset), 
                                name=f"save_data_{key}_{table_name}_{len(dataset)}")
                            # for d in filtered_dataset:
                            #     print("SAVING",
                            #           my_random_string(),
                            #           f"{table_name} {d.get('TRACE', -1)} {d['DT_GEN']}")
                            last_dataset[table_name] = last_dt 
                            tasks.append(future)
                            assigned[key][table_name] = future
                           
                            backup[key][table_name] = {
                                "time":now(),
                                "dataset": dataset}
                            if table_name in counter:
                                counter[table_name] += len(dataset)
                            else:
                                counter[table_name] = 0

                            if counter[table_name] == 60:
                                message = f"At ipt {ipt} saved successfully last {counter[table_name]}"+\
                                    f" messages for {table_name}, last " +\
                                    f"result"
                                level = Logger.INFO
                                counter[table_name] = 0

                            last_data = now()
                        except asyncio.CancelledError as e:
                            message = f"RDB {db_insta} at {ipt} has canceled task, but protected by shield"
                            level = Logger.ERROR
                            exc = MSGException(*sys.exc_info())
                            messages.append(MessageLog(rdbnow(), coroname, level, message, exc))                            
                            control_changes[key] = DBSteps.CONNECT
                            gprint(f"Reconnect to db  IPT -> {ipt}")
                            await db_insta.close()
                            
                            break

                        
                        except Exception as e:
                            message = f"RDB {db_insta} at {ipt} has an exception {e}"
                            level = Logger.CRITICAL
                            exc = MSGException(*sys.exc_info())
                            messages.append(MessageLog(rdbnow(), coroname, level, message, exc))                            
                            control_changes[key] = DBSteps.CONNECT
                            gprint(f"Exception connecting to db {db_insta.client_address} IPT -> {ipt}, {e}")
                            await db_insta.close()
                            break

                        if message:
                            messages.append(MessageLog(rdbnow(), coroname, level, message, exc))
                            
        control.update(control_changes)
        # running futures
        asyncio.gather(*tasks, return_exceptions=True)
            # stage = "free"

            # await queue_control.put((
            #     task_name, 
            #     now(), 
            #     stage, 
            #     {}))

        #gprint(f"No data on queue, db_insta {db_insta}")
        if queue_db.empty():
            await asyncio.sleep(1)
        # do log
        if messages:
            queue_messages = {"log":[msg.rdb for msg in messages]}
            queue_db.put(queue_messages)
        if level not in {logging.INFO, logging.DEBUG}:
            await asyncio.sleep(1)

        return [ipt, control, queue_db,  
                db_instances, counter, 
                last_data, last_time,
                flags, assigned, backup,
                queue_log], kwargs
    
    async def process_data(self, 
                           ipt:str, 
                           ico:str, 
                           control:CSteps, 
                           sta_insta:Gsof,
                           last_data:datetime, 
                           last_time:datetime, 
                           counter:int, 
                           queue_control:asyncio.Queue, 
                           queue_log:asyncio.Queue,
                           *args, **kwargs
                           ) -> Tuple[Tuple[
                               str,
                               str,
                               CSteps,
                               datetime,
                               datetime,
                               int,
                               asyncio.Queue,
                               asyncio.Queue], Dict[str, Any]]:
        loop = asyncio.get_event_loop()
        ids = self.assigned_tasks.get(ipt, {}).get(ico, None)
        assigned_tasks = self.assigned_tasks.get(ipt, {})
        ids = assigned_tasks.get(ico)
        level = Logger.ERROR
        messages = []
        message = ""
        task_name = f"process_sta_task:{ipt}:{ico}"
        coroname = "process_data"
        connected = kwargs["connected"]
        created = kwargs["created"]
        
        if now() >= last_time + timedelta(seconds=5):
            stage = "update"
            # await queue_control.put((task_name, now(), stage, sta_insta))
            # counter["DB_WORK"] = 0       

        if ids:
            if self.changes.get(ids, False):
                """
                Linked to db_loop, if there are a new change then
                create new instance, 
                """
                del sta_insta 
                sta_insta = None
                control = CSteps.CREATE

            code_db = self.stations.get(ids, {}).get('db')
            code = self.stations.get(ids, {}).get('code')
            idd = self.get_id_by_code('DBDATA', code_db)
            idc = self.idc.get(ids)
            if idc and sta_insta:
                if idc not in sta_insta.clients:
                    del sta_insta
                    sta_insta = None
                    control = CSteps.CREATE
            #############
            # For some actions that modify status of
            # the variables on this coroutine
            # self.free_ids[ids] = False
            # while self.wait.get(ids, False):
            #     await asyncio.sleep(.01)

            # if not self.status_sta[ids]:
            #     v = 1
            ##############
            """
            Si no se ha creado instancia de conexion a estación
            se crea

            sta_init un diccionario  {ids:bool}

            indice si la estación fue inicializada
            """
            check_0 = now()
            if control == CSteps.CREATE:
                # step 0 initialize the objects, source and end
                exc = MSGException()
                try:
                    sta_insta, table_name = self.add_sta_instance(
                        ids, loop)
                    # print(now(), f"STA INSTA {table_name} created")
                    try:
                        ring_buffer = kwargs.get("ring_buffer")                        
                        if not ring_buffer:
                            ring_buffer = RingBuffer(name=table_name,
                                                     size=self.buffer_size)
                            kwargs["ring_buffer"] = ring_buffer
                        else:
                            ring_buffer.clear()
                    except Exception as e:
                        print("Error al crear ring buffer", e)
                        message = f"RingBuffer for {table_name} can't be created because {e}"
                        level = Logger.ERROR
                        exc = MSGException(*sys.exc_info())
                        messages.append(MessageLog(rdbnow(), coroname, level, message, exc))
                            
                    
                    kwargs["table_name"] = table_name

                    message = f"Station instance {sta_insta} created "+\
                        f"for {table_name}, control {control.value}"
                    level = Logger.INFO
                    if sta_insta:
                        control = CSteps.CONNECT
                        self.changes[ids] = False
                except Exception as ex:
                    exc = MSGException(*sys.exc_info())
                    message = f"PD_00: Conexión de estación con falla-> {ids}:{code}"
                    level = Logger.ERROR
                    idc = self.idc.get(ids, None)
                    msg, close_level = await self.reset_station_conn(sta_insta, ids, idc)
                    control = CSteps.CREATE
                    kwargs["origin_exception"] = f"PD_00 + {code}"
                if message:
                    messages.append(MessageLog(rdbnow(), coroname, level, message, exc))

            """
            Si no se ha creado la instanca de database:
            se crea la db instancia
            """
            """
            En caso que instancia de collect a estacion se haya iniciado
            1° conectar
            2° extraer datos
            """
        else:
            await asyncio.sleep(.1)

        exc = MSGException()
        message = ""
        check_1 = now()
        
        if sta_insta:
            queue_db = kwargs.get("queue_db")
            table_name = kwargs.get("table_name")

            if control == CSteps.CONNECT:
                # step 1
                # si es primera vez de acceso
                # conectar al socket correspondiente
                # step 1.a connect and set flags to run data
                code = sta_insta.station            
                idc = None
                exc = MSGException()
                try:

                    future = asyncio.create_task(sta_insta.connect())
                    stage = "connect"
                    # print(now(), f"STA INSTA {table_name} connected")
                    # drop control
                    # await queue_control.put((
                    #     task_name,
                    #     now(),
                    #     stage,
                    #     future))

                    idc = await wait_for(
                        shield(future),
                        timeout=20)
                    check_1 = now()
                    kwargs["connected"] = True
                    if idc:
                        self.idc[ids] = idc
                        self.set_status_sta(ids, True)
                        self.set_status_conn(ids, True)
                        self.first_time[ids] = False
                        check_a = now()
                        
                        
                        control = CSteps.COLLECT
                        message = f"Station {sta_insta} connected at"+\
                            f" {ipt} "+\
                            f" to address {sta_insta.address}"
                        level = Logger.INFO
                    else:
                        control = CSteps.CONNECT
                        message = f"Station {sta_insta} not connected at"+\
                            f" {ipt} "+\
                            f" to address {sta_insta.address}"
                        level = Logger.WARNING

                    messages.append(MessageLog(rdbnow(), coroname, level, message, exc))
                except asyncio.TimeoutError as e:
                    exc = MSGException(*sys.exc_info())
                    message = f"Tiempo fuera para conectar instancia " +\
                        f"de estación {sta_insta} en ipt {ipt}, idc <{idc}>"
                    level = Logger.ERROR               
                    control = CSteps.CONNECT
                    msg, lvl = await self.reset_station_conn(
                        sta_insta,
                        ids,
                        idc)
                    control = CSteps.CONNECT
                    kwargs["connected"] = False
                    messages.append(MessageLog(rdbnow(), coroname, level, message, exc))


                except Exception as ex:
                    exc = MSGException(*sys.exc_info())
                    message = f"PD_02: Error al conectar estación {sta_insta}, ids {ids}, ipt  {ipt}, {ex}"
                    level = Logger.ERROR
                    control = CSteps.CONNECT
                    msg, lvl = await self.reset_station_conn(
                        sta_insta,
                        ids,
                        idc)
                    control = CSteps.CONNECT
                    kwargs["connected"] = False
                    messages.append(MessageLog(rdbnow(), coroname, level, message, exc))

                # si ya esta conectado :), obtener dato

            """
            Si ya está inicializado y conectad
            proceder a obtener datos
            """
            sta_dict = {}
            # print(now(), f"STA INSTA {table_name} pre-collect", control, table_name)
            
            if control == CSteps.COLLECT and table_name:
                check_2 = now()
                # if connected:
                #     print(f"Table {table_name}", f"Check connect {check_1}", f"{check_2}", "Connected", connected)
                #     print(f"From connect to collect first {(check_2-check_1)}")
                #     connected = False
                ring_buffer = kwargs.get("ring_buffer")
                code = sta_insta.station
                idc = self.idc.get(ids)
                exc = MSGException()
                # just for checking
                # step 1.b collect data and process to save the raw data
                try:
                    pre_get = now()                  
                    
                    async def get_records():
                        try:
                            set_header = await sta_insta.get_message_header(idc)
                            done, sta_dict = await sta_insta.get_records()
                            #print(gps_time, inspect.signature(gps_time))
                            dt0, source = gps_time(sta_dict)
                                                   #sta_insta.tipo)
                            dt_iso = rdb.iso8601(dt0.isoformat())
                            rnow = now()
                            recv_now = rdbnow()
                            # print(rnow)
                            delta = (rnow - dt0).total_seconds()
                            sta_dict.update({
                                "TRACE": (ipt, ids, idc),
                                'DT_GEN': dt_iso,
                                'DT_RECV': recv_now,
                                "DELTA_TIME": delta})
                            data = Data(**{v:sta_dict.get(key) for key,v in DATA_KEYS.items()})
                            ring_buffer.add(data)
                            last_data = recv_now
                        except Exception as ex:
                            print("Falla en get_records", ex)
                            raise ex
                        await queue_db.put((table_name, sta_dict))                
                        return delta, last_data
                    
                    # Control criteria
                    # queue_db.put((table_name, sta_dict))
                    delta, last_data = await get_records()
                    # if delta>1:
                    #     print(last_data, table_name, f"Delta {delta}")
                    
                    post_get = now()
                    # control ring buffer
                    n = 0
                    # print("MU",ring_buffer.mu,ring_buffer.mu**3) 
                    mu_control = lambda delta: delta + ring_buffer.sigma**3
                    inside = False
                    delta_mu_control = mu_control(delta)
                    if  delta_mu_control  >= self.u_base:
                        try:
                            #print(table_name, self.u_base,mu_control(delta) >= self.u_base, "DELTA", delta, "mu_control", mu_control(delta))                       
                            inside = True
                            lvl = Logger.WARNING
                            msg = f"Giving priority to {table_name}, latency {delta}, iter {n}"
                            messages.append(MessageLog(rdbnow(), coroname, lvl, msg, exc))
                            new_delta = delta
                            #print(table_name, "NEw delta", new_delta)
                            control_ring_buffer = RingBuffer(name="control_acc", size=5)
                            control_ring_buffer.add(Data(dt_gen=last_data,latency=new_delta))
                            while control_ring_buffer.mu > self.u_base:
                                val  = delta
                                for i in range(int(val) + 1):
                                    # pendiente:
                                    delta, last_data = await get_records()
                                    n += 1
                                val  = delta
                                control_ring_buffer.add(Data(dt_gen=last_data,latency=val))
                                new_delta = delta
                            #print(now(), table_name, new_delta, n, new_delta>.9 and n<=20)
                        except Exception as e:
                            print(now(),"Exception",e)
                    if inside:
                        #print("Last delta", table_name, delta,
                        #      ring_buffer, f"iteraciones {n}")
                        pass
                    await asyncio.sleep(0)

                    # await queue_control.put((
                    #     task_name, 
                    #     now(), 
                    #     stage, 
                    #     {"DT_GEN":dt0.isoformat(),"station":table_name}))

                    counter += 1
                    if counter == 60:
                        message = f"At ipt {ipt} ico {ico} sended successfully last {counter}"+\
                            f" messages for {code} at {last_data}"
                        level = Logger.INFO
                        messages.append(MessageLog(rdbnow(), coroname, level, message, exc))
                        counter = 0
                    await sta_insta.heart_beat(idc)
                    control = CSteps.COLLECT                    

                except asyncio.IncompleteReadError as incomplete_read:
                    exc = MSGException(*sys.exc_info())

                    message = f"At ipt {ipt} ico {ico} imcomplete read {incomplete_read},"+\
                        f"station {sta_insta}"
                    level = Logger.ERROR
                    msg, lvl = await self.reset_station_conn(
                        sta_insta,
                        ids,
                        idc)
                    control = CSteps.CONNECT
                    kwargs["connected"] = False
                    messages.append(MessageLog(rdbnow(), coroname, level, message, exc))
                    messages.append(MessageLog(rdbnow(), coroname, lvl, msg, MSGException()))

                except Exception as e:
                    exc = MSGException(*sys.exc_info())
                    message = f"At ipt {ipt} ico {ico} error al obtener dato de estación {e},"+\
                        f"station {sta_insta}"
                    level = Logger.ERROR
                    msg, lvl = await self.reset_station_conn(
                        sta_insta,
                        ids,
                        idc)
                    control = CSteps.CONNECT
                    kwargs["connected"] = False
                    messages.append(MessageLog(rdbnow(), coroname, level, message, exc))
                    messages.append(MessageLog(rdbnow(), coroname, lvl, msg, MSGException()))
                    #raise e # test
                except asyncio.TimeoutError as e:
                    exc = MSGException(*sys.exc_info())
                    message = f"At ipt {ipt}, ico {ico} tiempo fuera para"+\
                        f"obtener datos de estación {sta_insta}"
                    level = Logger.ERROR
                    kwargs["origin_exception"] = f"PD_T12_00 + {sta_insta}"                                     
                    msg, lvl = await self.reset_station_conn(
                        sta_insta,
                        ids,
                        idc)
                    kwargs["connected"] = False
                    messages.append(MessageLog(rdbnow(), coroname, level, message, exc))
                    messages.append(MessageLog(rdbnow(), coroname, lvl, msg, MSGException()))

                    control = CSteps.CONNECT
                except asyncio.ConnectionError as e:
                    exc = MSGException(*sys.exc_info())
                    message = f"At ipt {ipt}, ico {ico} Error de conexión para conectar instancia de estación {sta_insta}"
                    level = Logger.ERROR
                    kwargs["origin_exception"] = f"PD_T13_00 + {sta_insta}"                                     
                    msg, lvl = await self.reset_station_conn(sta_insta, ids, idc)

                    kwargs["connected"] = False
                    messages.append(MessageLog(rdbnow(), coroname, level, message, exc))
                    messages.append(MessageLog(rdbnow(), coroname, lvl, msg, MSGException()))
                    control = CSteps.CONNECT


            if ids in self.first_time:
                idd = self.db_instances_sta.get(ids)
                self.first_time[ids] = False

            else:
                idd = self.db_instances_sta.get(ids)

            if not table_name:
                message = f"There are no table name for {code} instance {sta_insta}"
                level = Logger.WARNING
                messages.append(MessageLog(rdbnow(), coroname, level, message, exc))

            # control last data received
            # si aun no hay last_data
            if not last_data:
                control = CSteps.CONNECT
                kwargs["connected"] = False
                msg, lvl = await self.reset_station_conn(
                    sta_insta,
                    ids,
                    idc)

            elif isinstance(last_data, datetime):
                rnow = now()
                if last_data + timedelta(seconds=60) <= rnow:
                    code = sta_insta.station
                    idc = self.idc.get(ids)
                    message, level = await self.reset_station_conn(
                        sta_insta,
                        ids,
                        idc)
                    messages.append(MessageLog(rdbnow(), coroname, level, message, exc))
                    message = f"Last data was along time"+\
                        f" ago... <{last_data}>, try reconnect for {sta_insta}"
                    level  = Logger.WARNING
                    messages.append(MessageLog(rdbnow(), coroname, level, message, exc))
                    control = CSteps.CONNECT
            else:
                message = f"last data for station {sta_insta} doesn't"+\
                    " exists or isn't a datetime object"

            """
            Procesar los datos
            """
            """
            Conclusión del cliclo
            esta tarea se termina. ... (por un momento)
            se preparan los parámetros de retorno

            Si todo va bien debería llegar hasta acá:
            """
            # [input, output] controls
            #self.free_ids[ids] = True
        else:
            message = "Sleeping because there are no task, table name {table_name}"
            level = Logger.WARNING
        if now() >= last_time + timedelta(seconds=10):
            last_time = now()
        
        # args result
        out = [ipt, ico,  control, 
               sta_insta, last_data, 
               last_time, counter, 
               queue_control, queue_log]

        if messages:
            for msg in messages:
                await queue_db.put(("log", msg.rdb))                
            #await queue_log.put(messages)
            # log.save(level, message)
        if level not in {logging.INFO, logging.DEBUG}:
            await asyncio.sleep(.1)
        return out, kwargs
    
    # task to receive log message and save to file
    async def queue_log_join(self, ipt, queue_log, **kwargs):
        """
        By thread/process receive all messages and join to send to log
        process task -> manage_log
        
        """
        if not queue_log.empty():
            dataset = []
            
            for i in range(queue_log.qsize()):
                message_list = await queue_log.get()
                if isinstance(message_list, Iterable):
                    dataset += message_list
                else:
                    print(message_list)
            self.queue_log.put(dataset)

        await asyncio.sleep(5)
        return (ipt, queue_log), kwargs

    async def manage_log(self, log, queue_log, **kwargs):
        """
        an multiprocessing queue to manage all log messages
        """
        if not queue_log.empty():
            for i in range(queue_log.qsize()):
                messages = queue_log.get()
                for msg in messages:
                    # print(now(), msg)
                    if msg.exception:
                        pass
                        #log.logger.error(exc_info=msg.exc)
                    else:
                        log.logger.log(*msg.log)               

            queue_log.task_done()
            # collect garbage manually
        return (log, queue_log), kwargs


    def manage_log_task(self):
        rprint("Manage log task doing")
        log = FileLog("Engine@Collector",
                      f"LogTask",
                      "localhost@atlas",
                      path=self.log_path,
                      max_bytes=10100204)
        args = [log, self.queue_log]
        task_name = "log_task"
        task = TaskLoop(self.manage_log, args, {}, name=task_name)
        task.create()

    """
    To run this process add the task in a process like
        loop.run_in_executor(executor, collector.manage_log_task)
    Or in a process with another low intensity tasks
    """

    ##


    async def status_proc_task(self, ipt, loop, ipt_result_dict):
        """
        Coroutine que chequea el status
        """
        log = self.log_manager[ipt]
        ids_list = self.proc_tasks[ipt]
        if len(ids_list) > 0:
            print("Recolectando %s" % format(ids_list))
        results_dict = {}
        await asyncio.sleep(5)

        return [ipt, loop, results_dict]

    def check_iteration(self, maxv, task, coro):
        """
        Is a demo fn to create a hyperiteration and possible add new stations
        ->not impletented yet
        """
        result = task.result()
        value = result[0][1]
        if value <= maxv:
            renew(task, coro, simple_fargs_out)

    def set_init_args_kwargs(self, ipt):
        """
        This definition is for collector instance
        """
        return [ipt, (None, None)], {}

    def set_pst(self, ids, args, kwargs):
        """
        This definition is for collector instance
        """
        return [args[0], ids, *args[1:]], kwargs

    def msg_network_task(self):
        # get from queue status
        # read_queue -> rq
        # process msg -> f(
        queue_list = [self.queue_n2t, self.queue_t2n]
        loop = asyncio.get_event_loop()
        try:
            args = [queue_list]
            kwargs = {}
            # Create instances
            task_name = "check_status_task"
            # task = TaskLoop(
            #         self.check_status,
            #         args, kwargs, name=task_name)
            # task.create()
            self.status_tasks["status_check"] = task_name
            ## log task
            #self.manage_log_task()
            queue_log = asyncio.Queue()
            self.manage_db_loop(queue_log)
            ipt = "msg_network_task"
            args = [ipt,  queue_log]
            task_name = f"queue_log_join:{ipt}"
            task_db = TaskLoop(
                self.queue_log_join,
                args,
                {},
                **{"name": task_name})
            task_db.set_name(task_name)
            task_db.create()
            
            # self.status_task_monitor_task()
            if not loop.is_running():
                loop.run_forever()
        except Exception as ex:
            print("Error o exception que se levanta con %s" %
                  format(queue_list))
            raise ex

    def manage_db_loop(self, queue_log):
        args = [ORMSteps.DISTRIBUTE, queue_log]
        task_name = "db_loop_task"
        task = TaskLoop(self.db_loop, args, {}, name=task_name)
        task.create()
        self.status_tasks["db_loop"] = task_name
        
    async def db_loop(
            self, 
            control:ORMSteps, 
            queue_log: asyncio.Queue, 
            *args,
            **kwargs
    ) -> Tuple[
        Tuple[ORMSteps, asyncio.Queue], 
        Dict[str, Any]
    ]:
        """
        Control for new stations or update conection credentials
        """
        messages = []
        keys = ['id', 'code', 'db', 'dblist', 'ecef_x', 'ecef_y', 'protocol_host',
                'ecef_z', 'port', 'protocol', 'host', 'dbname']
        exc = MSGException()
        coroname = 'db_loop'
        if control == ORMSteps.DISTRIBUTE:
            control = ORMSteps.EXECUTE
        if control == ORMSteps.EXECUTE:
            """
            Needs:
            - list of stations
            - assignation of stations 
            - check for new stations
            - drop if not listed in new list of databases
            """
            # Obtener las estaciones
            ids_stations = {station.get("code"):ids for ids, station in self.stations.items()}
            base_stations = [station for station in self.stations.values()]
            codes = [station.get("code") for station in base_stations]
            set_codes = set(codes)
            address = {
                station.get("code"):(station.get("host"),station.get("port")) 
                for station in base_stations
            }
            # obtain all ids assigned
            assigned_tasks  = set()      # 
            if self.assigned_tasks:
                assigned_tasks = reduce(
                    lambda a,b: a|b, 
                    [set(ids_set.values()) for ipt, ids_set in
                     self.assigned_tasks.items()])
            assigned_ids = set(filter(lambda e:e,[self.stations.get(ids, {}).get("code") for
                            ids in assigned_tasks]))

            try:
                
                stations = load_stations(ORM_URL)

            except Exception as e:
                print("Error al obtener lista", control)
                raise e
            try:
                new_codes = set()
                for m in stations:
                    station = dict(**m, on_db=True)
                    code = station["code"]
                    new_codes.add(code)
                    if code not in assigned_ids:
                        """
                        add new station to list, and send by queue to assignator
                        """
                        ids, station = self.add_station(**station)
                        message = f"New station added to collector {station}"
                        level = Logger.INFO
                        messages.append(MessageLog(rdbnow(),coroname, level, message, exc))
                        self.queue_process.put(ids)
                        self.changes[ids] = True
                    else:
                        """
                        if there is in codes, but check address data
                        is the important information for this use case
                        """
                        base_address = address.get(code)
                        if base_address:
                            now_address = (station["host"],
                                           station["port"])
                            ids = ids_stations.get(code)
                            if now_address != base_address:
                                """
                                If new info is correct, the connection
                                will raise and check for new info
                                (check control)
                                """
                                station = self.update_station(ids, **station)
                                self.changes[ids] = True

                # drop deactivated codes
                dropped = set_codes - new_codes
                ids_drop = [ids_stations.get(code) for code in
                            dropped]
                for ids in ids_drop:
                    self.changes[ids] = True
                    if ids in self.stations:
                        station = self.stations.get(ids)
                        del self.stations[ids]
                        for ipt, task_set in self.assigned_tasks.items():
                            if ids in task_set.values():
                                for ico, nids in task_set.items():
                                    if ids == nids:
                                        message = f"Station {station} with ids {ids},"+\
                                            "ico {ico}, ipt {ipt}  dropped"
                                        level = Logger.INFO
                                        messages.append(MessageLog(rdbnow(), coroname, level, message, exc))
                                        
                                        self.unset_sta_assigned(ipt,
                                                                ico, 
                                                                ids)
            except Exception as e:
                exc = MSGException(*sys.exc_info())                
                message = f"At db_loop the session is disconnected"
                level = Logger.ERROR
                messages.append(MessageLog(rdbnow(),coroname, level, message, exc))
                control = ORMSteps.DISTRIBUTE

        if messages:
            for msg in messages:
                await queue_log.put(("db_loop", msg.rdb))                

        await asyncio.sleep(30)
        return (control, queue_log), kwargs


    async def check_status(self, queue_list, *args, **kwargs):
        wq = queue_list[0]
        rq = queue_list[1]
        process = dict()
        idc = ""
        await asyncio.sleep(5)
        try:
            msg_from_source = []
            if not rq.empty():
                for i in range(rq.qsize()):
                    msg = rq.get()
                    # msg is a dict deserialized
                    msg_from_source.append(msg)
                    m = msg.get('dt', {})
                    idc = msg.get('idc', {})
                    if isinstance(msg, dict):
                        c_key = m.get('command',{}).get('action',None)
                        if c_key in self.message_manager.commands.keys():
                            result = await self.message_manager.interpreter(m)
                            wq.put({'msg': result, 'idc': idc})
                        else:
                            wq.put({'msg': "Hemos recibido %s" % m, 'idc': idc})
                    else:
                        wq.put(
                            {'msg': "Es un mensaje que no es un comando de sistema %s" % msg,
                             'idc': idc})

            # bprint(self.instances.keys())
        except Exception as ex:
            raise ex
        return [queue_list, *args], kwargs


    async def manage_data(self, queue_list, *args, **kwargs):
      
        # idd = self.get_id_by_code('DBDATA', code_db)        
        # code = None        

        # if not self.db_init.get(idd, False):
        #     db_insta = self.add_db_instance(ids, idd)

        return [queue_list, *args], kwargs

    async def status_task_monitor(self, *args, **kwargs):
        tasks_list = [task for task in asyncio.all_tasks() 
                      if task.get_name() in
                      self.status_tasks.values()]
        for task in tasks_list:
            print(now(), "Monitor ::", task.get_name(), "Cancelled", task.cancelled(),
                  "Done", task.done())
        await asyncio.sleep(20)
        return args, kwargs

    def status_task_monitor_task(self):
        loop = asyncio.get_event_loop()
        task_name = "status_task_monitor_task"
        task = TaskLoop(self.status_task_monitor, (), {}, name=task_name)
        task.create()
        self.status_tasks["status_task_monitor"] = task_name

    # async def manage_log(self, log, queue_log, **kwargs):
    #     """
    #     an multiprocessing queue to manage all log messages
    #     """
    #     if not queue_log.empty():
    #         for i in range(queue_log.qsize()):
    #             (function, message, level, exc) = queue_log.get()
    #             print(now(), function, "::", message, exc)
                
    #             log.logger.log(level, f"{function} :: {message}")               
    #             if exc:
    #                 tb = exc.get("exc_traceback")
    #                 traceback.print_tb(tb)
    #                 info = tuple(exc.values())
    #                 log.logger.error(f"{function} :: {message}", 
    #                                  exc_info=info)
    #         queue_log.task_done()
    #     return (log, queue_log), kwargs


    # def manage_log_task(self):
    #     rprint("Manage log task doing")
    #     loop = asyncio.get_event_loop()
    #     log = FileLog("Engine@Collector",
    #                   f"LogTask",
    #                   "localhost@atlas",
    #                   path=self.log_path/"engine",
    #                   max_bytes=10100204)
    #     args = [log, self.queue_log]
    #     task_name = "log_task"
    #     task = TaskLoop(self.manage_log, args, {}, name=task_name)
    #     task.create()
    #     self.status_tasks["log"] = task_name


    async def queue_join(self, ipt, queue_db, queue_to_db, **kwargs):
        """
        Receive from process data and send to process where dbwork is doing
        """

        if not queue_db.empty():
            dataset = {}
            
            for i in range(queue_db.qsize()):
                table, item = await queue_db.get()
                if table not in dataset:
                    dataset[table] = []
                dataset[table].append(item)
            queue_to_db.put(dataset)

        return (ipt, queue_db, queue_to_db), kwargs
        
    def manage_tasks(self, ipt):
        """
        A method to manage the tasks assigned to *ipt* process

        Initialize an event loop, and assign idle tasks for this process

        Create the tasks for every source assigned to this process.

        Create task for database

        Check the cases unidirectional and bidirectional.

        :param ipt: the key or identifier of a process
        """
        # loop = asyncio.get_event_loop()
        gprint(f"New ipt task {ipt}")
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        bprint(f"New loop on ipt {ipt}")
        queue_db = asyncio.Queue()
        queue_to_db = self.queue_db
        args = [ipt, queue_db, queue_to_db]
        task_name = f"queue_db:{ipt}"
        task_db = TaskLoop(
            self.queue_join,
            args,
            {},
            **{"name": task_name})
        task_db.set_name(task_name)
        task_db.create()

        # Task to join all messages to log 

        # Queue log join
        queue_log = asyncio.Queue()

        #args = [ipt, queue_log,]
        #task_name = f"queue_log_join:{ipt}"
        #task_db = TaskLoop(
        #    self.queue_log_join,
        #    args,
        #    {},
        #    **{"name": task_name})
        #task_db.set_name(task_name)
        #task_db.create()

       
        # creating the ico values

        queue_control = asyncio.Queue()

        tasks = []
        self.assigned_tasks[ipt] = {}
        new_dict = {}
        # inicia n tareas en procesados
        for i in range(self.lnproc):
            ico = f"ICO_{i}"
            new_dict.update({ico:  None})
        self.assigned_tasks[ipt] = new_dict
        tasks_on_this_ipt = self.assigned_tasks.get(ipt)
        

        #tasks.append(db_task)
        #self.status_tasks["db_task"] = task_name 
        # end db task
        for ico in tasks_on_this_ipt.keys():
            if self.run_task:
                try:
                    #ids = self.assigned_tasks.get(ipt, {}).get(ico,
                    #None)
                    control_collect = CSteps.CREATE
                    args = [ipt, ico, control_collect, None, 
                            now(), now(), 0, queue_control, queue_log]
                    task_name = f"process_sta_task:{ipt}:{ico}"
                    task_1 = TaskLoop(
                        self.process_data,
                        args,
                        {"queue_db": queue_db, "connected":False, "created":False},
                        **{"name": task_name})
                    #task_1.set_name(task_name)
                    task_1.create()
                    tasks.append(task_1)
                    key = f"collect_{ico}"
                    self.status_tasks[key] = task_name
                except Exception as ex:
                    print(
                        "Error en collect_task, gather stations, process_sta(task) %s, error %s"
                        % (ipt, ex))
                    print(ex)
                    raise ex
        try:
            args = [ipt]
            kwargs = {}
            # task_4 = TaskLoop(
            #     self.process_sta_manager,
            #     args,
            #     kwargs,
            #     {"name": "task_process_sta_manager"}
            # )
            # task_4.create()
            # for task in tasks:
            #     bprint(f"Iniciando tarea->{task}")
            #     task.create()
            

            """
            Controller, check for the running tasks
            """
            control = ControlActions.ACTIVATE
            monitoring = {}
            counter = {}
            stages = {}
            reserva = {}
            args = [ipt, control, queue_control, tasks, monitoring,
                    counter, stages, reserva, queue_log]
            kwargs = {}
            print(now(),"Creating control tasks to dynamic management")

            # control_task = TaskLoop(
            #     self.control_tasks,
            #     args,
            #     kwargs,
            #     {"name": "task_control_tasks"}
            # )
            # print(now(),"Created")
            # control_task.create()


        except Exception as exe:
            print("Error en collect_task, manager %s, error %s" % (ipt, exe))
            print(exe)
            raise exe
        if not loop.is_running():
            loop.run_forever()


    async def control_tasks(self, ipt, control,  
                            queue, 
                            tasks, 
                            monitoring, 
                            counter,
                            stages,
                            reserva,
                            queue_log,
                            **kwargs):
        DEBUG = False
        loop = asyncio.get_event_loop()
        delta_time = 5
        limit = 60
        print(now(), f"Control Tasks :: at {ipt}, {control.name}, "+\
              f"queue {queue.qsize()}") 
        messages = []
        if control == ControlActions.ACTIVATE:
            for task in tasks:
                future = task.create()#asyncio.run_coroutine_threadsafe(run_task(task), loop)
                monitoring[task.name] = {
                    "task": task,
                    "future": future,
                    "last_check": now(), 
                    "instance": None
                }
                message = f"Control Tasks At ipt {ipt} task running at threadsafe {task.name}"
                messages.append(MessageLog(rdbnow(),Logger.INFO, message, MSGException()))
                stages[task.name] = {}
            control = ControlActions.MONITOR

        observable = {}

        if control == ControlActions.MONITOR:
            if not queue.empty():
                for i in range(queue.qsize()):
                    # can get many of same source but save last
                    origin, data, stage, information = await queue.get()

                    if stage == "update":
                        client_address = information
                        if origin in monitoring:
                            last_check = monitoring[origin]["last_check"]
                            observable[origin] = data
                            #comment this to develop fast ::
                            if not DEBUG:
                                monitoring[origin]["last_check"] = data
                            monitoring[origin]["client"] = client_address
                        else:
                            message = f"Control Tasks Trash received origin :: {origin} data :: {data}"
                            messages.append(MessageLog(Logger.INFO, message, MSGException()))
                            
                    elif stage in ("connect", "save", "collect"):
                        stages[origin] = {
                            "time": data, 
                            "task": information,
                            "stage": stage
                        }
                        observable[origin] = data
                        #comment this to develop fast ::
                        if not DEBUG:
                            monitoring[origin]["last_check"] = data

                    elif stage in {"sendq", "todb"}:
                        dtgen = information.get("DT_GEN")
                        station = information.get("station")
                        if station not in counter:
                            counter[station] = {"sendq":{}, "todb":{}}
                        counter[station][stage][dtgen] = data

                    elif stage == "free":
                        reserva[origin] = True
                        for station in counter:
                            counter[station] = {"sendq":{}, "todb":{}}
                queue.task_done()
        
        # now, do the control based at the information
        factor = limit/delta_time
        
        for key, item_task in monitoring.items():
            monitoring_check = item_task["last_check"]
            # counter[key] do the control in case observable didn't
            # receive new data
            #if counter[key] >= factor:
            comp = now()
            drop_loop = False
            differences = []

            reserva_key = reserva.get(key, True)

            if key.startswith("db_task_"):
                station = ""
                for station, data in counter.items():
                    send_time = counter[station]["sendq"]
                    todb_time = counter[station]["todb"]
                    differences = []
                    discard = []
                    for dtgen, value in send_time.items():
                        todb_value = todb_time.get(dtgen)
                        final = todb_value
                        if not todb_value:
                            final = now()
                        else:
                            discard.append(dtgen)
                            dest = [dt for dt, val in
                                    todb_time.items() if val<=value]
                            discard += dest
                        check = (final - value) > timedelta(seconds=limit)
                        differences.append(check)
                        if check:
                            break
                        else:
                            discard.append(dtgen)
                    for dtkey in discard:
                        if dtkey in counter[station]["sendq"]:
                            del counter[station]["sendq"][dtkey]
                        if dtkey in counter[station]["todb"]:
                            del counter[station]["todb"][dtkey]
                    drop_loop = any(differences)
                    if drop_loop:
                        print("LOCKED -> drop", station, data)
                        break
                print(now(), key, f"LOCKED If loop locked {drop_loop}, {differences}")
                
            loop_locked = comp >= (monitoring_check +
                                   timedelta(seconds=limit))
            # if not reserva_key:
            #     item = stages[key]
            #     # here cancel the inner task that is blocked
            #     stage_task = item.get("task")
            #     if not stage_task.done():
            #         print(now(), f"Cancelling stage at {ipt}, with  delta {delta}")
            #         if not stage_task.cancelled():
            #             stage_task.cancel()
            #         exc = {}
            #         try:
            #             stage_task.exception()
            #         except Exception as e:
            #             exc = dict(
            #                 zip(
            #                     ("exc_type","exc_value","exc_traceback"), 
            #                     sys.exc_info()))


            if (loop_locked or drop_loop) and reserva_key:
                reserva[key] = False
                delta = comp - (monitoring_check + timedelta(seconds=limit))
                main_task = item_task.get("task")
                future = item_task.get("future")

                """
                works: run a new task 
                doesnt' work :: close db connection!! :S
                """
                # options :: dropped yet
                # entry here if the task is blocked, so we 
                # can redefine the callbacks, finish and give
                # one to show
                print(now(), f"The {main_task.name} is forced"+\
                                         " to  finish at ipt"+\
                                         f" {ipt} Control Tasks")
                #main_task.finish()
                if key in stages:
                    item = stages[key]
                    # here cancel the inner task that is blocked
                    stage_task = item.get("task")
                    print(now(), f"Cancelling stage at {ipt}, with  delta {delta}")
                    if stage_task:
                        if not stage_task.cancelled():
                            stage_task.cancel()
                        exc = MSGException()
                        try:
                            stage_task.exception()
                        except Exception as e:
                            exc = MSGException(*sys.exc_info())
                        # close rdb conn
                        result_args, result_kwargs = future.result()
                        for i, elem in result_kwargs.items():
                            if isinstance(elem, Rethink_DBS):
                                instance = elem
                                flag = True
                                while flag:
                                    await instance.close()
                                    flag = instance.active
                                    print(now(), instance.client_host,
                                          instance.client_port)
                                    print(now(), 
                                          f"""Instance {instance}
                                          close connection,
                                          active
                                          {instance.active},
                                          at {ipt}, falg {flag}""")

                        # recreate future
                        datenow = now()

                        message = f"At ipt {ipt} cancel stage {stage} for {key} at"+\
                            f" {datenow}, previous future coroutine cancelled"+\
                            f" the previous result, delta time {delta}"+\
                            f" or an exception {exc}"+\
                            f" counter was at {key}"
                        level = Logger.CRITICAL
                        messages.append(MessageLog(rdbnow(),Logger.INFO, message, MSGException()))                        
                        counter[station] = {"sendq":{}, "todb":{}}

                # while not future.done():
                #     await asyncio.sleep(.1)

                # instance = None
                # position = 0
                # if future.done():
                #     result = future.result()
                #     if len(result) == 2:
                #         margs, mkwargs = result
                #         for i, elem in enumerate(margs):
                #             if isinstance(elem, Rethink_DBS):
                #                 instance = elem
                #                 while instance.active:
                #                     await instance.close()
                #                     await asyncio.sleep(1)
                #                     print(now(), instance.client_host,
                #                           instance.client_port)
                #                     print(now(), 
                #                           f"""Instance {instance}
                #                           close connection,
                #                           active
                #                           {instance.active},
                #                           at {ipt}""")
                #                 #main_task.coro_args[i] = elem
                #             if isinstance(elem, DBSteps):
                #                 #main_task.coro_args[i] = DBSteps.SAVE
                #                 pass

                #             if isinstance(elem,Gsof):
                #                 instance = elem
                #                 while instance.status:
                #                     await instance.close()
                #                     await asyncio.sleep(.1)
                #                     print(now(), 
                #                           f"""Instance {instance}
                #                           close connection,
                #                           active
                #                           {instance.active},
                #                           at {ipt}""")

                # if key.startswith("db_task_"):
                #     # pass
                #     if isinstance(instance, Rethink_DBS):
                #         message = f"Control Tasks Closing rethinkdb {instance} "+\
                #               f" to spawn another at {ipt}"
                #         print(now(), message)
                #         address = instance.client_address
                #         # await instance.close()
                #         # await asyncio.sleep(3)
                #         # print(now(), f"Control Tasks ipt {ipt} Closing to client port"+\
                #         #       f" address {address}")
                #         # del instance
                #         messages.append((Logger.INFO, message,
                #                          {}))

                #     future = main_task.create()

                #     datenow = now()

                #     monitoring[main_task.name] = {
                #         "task": main_task,
                #         "future": future,
                #         "last_check": datenow
                #     }

                #     message = f"At ipt {ipt} spawned new task for {key} at"+\
                #         f" {datenow}, previous future coroutine cancelled"+\
                #         f" the previous result"+\
                #         f" or an exception {exc}"+\
                #         f" counter was at {key}"
                #     level = Logger.CRITICAL
                #     messages.append((level, message, exc))


                # if key.startswith("process_sta_task_"):
                #     task.coro_args[1] = CSteps.CREATE 
                #     instance = mkwargs.get("instance")

                #     if isinstance(instance, Gsof):
                #         message = f"Control Tasks Closing protocol {instance}"+\
                #               f" to spawn another at {ipt}"
                #         print(now(), message)
                #         del instance
                #         messages.append((Logger.INFO, message, {}))


                #     # create new future task at threadsafe

                #     # future = asyncio.run_coroutine_threadsafe(
                #     #     run_task(main_task), 
                #     #     loop)

                #     future = main_task.create()

                #     datenow = now()

                #     monitoring[main_task.name] = {
                #         "task": main_task,
                #         "future": future,
                #         "last_check": datenow
                #     }

                #     message = f"At ipt {ipt} spawned new task for {key} at"+\
                #         f" {datenow}, previous future coroutine cancelled"+\
                #         f" the previous result"+\
                #         f" or an exception {exc}"+\
                #         f" counter was at {counter[key]}"
                #     level = Logger.CRITICAL
                #     messages.append((level, message, exc))

                # else:
                # task = item_task.get("task")
                # future = item_task.get("future")
                # if not future.cancelled():
                #     future.cancel()

                # r_kwargs = {}
                # instance = None

                # if future.done():
                #     result = future.result()
                #     r_args, r_kwargs = result
                #     for i, elem in enumerate(r_args):
                #         if isinstance(elem, Rethink_DBS):
                #             instance = elem
                #     await asyncio.sleep(1)
                # exc = {}
                # try:
                #     future.exception()
                # except Exception as e:
                #     exc = dict(
                #         zip(
                #             ("exc_type", "exc_value", "exc_traceback"), 
                #             sys.exc_info()))


                # if key.startswith("db_task_"):
                #     task.coro_args[1] = DBSteps.CREATE 
                #     instance = r_kwargs.get("instance")

                #     if isinstance(instance, Rethink_DBS):
                #         message = f"Control Tasks Closing rethinkdb {instance} "+\
                #               f"to spawn another at {ipt}"
                #         print(now(), message)
                #         address = instance.client_address
                #         await instance.close()
                #         await asyncio.sleep(5)
                #         print(now(), f"Control Tasks ipt {ipt} Closing to client port"+\
                #               f" address {address}")
                #         del instance
                #         close_socket(address)
                #         messages.append((Logger.INFO, message, {}))
                # if key.startswith("process_sta_task_"):
                #     task.coro_args[1] = CSteps.CREATE 
                #     instance = r_kwargs.get("instance")

                #     if isinstance(instance, Gsof):
                #         message = f"Control Tasks Closing protocol {instance}"+\
                #               f" to spawn another at {ipt}"
                #         print(now(), message)
                #         await instance.close()
                #         del instance
                #         messages.append((Logger.INFO, message, {}))



                # task = monitoring[key]["task"]
                # future = task.create()#asyncio.run_coroutine_threadsafe(
                #     #run_task(task), 
                #     #loop)

                # datenow = now()

                # monitoring[task.name] = {
                #     "task": task,
                #     "future": future,
                #     "last_check": datenow
                # }

                # message = f"At ipt {ipt} spawned new task for {key} at"+\
                #     f" {datenow}, previous future coroutine cancelled"+\
                #     f" the previous result"+\
                #     f" or an exception {exc}"+\
                #     f" counter was at {counter[key]}"
                # level = Logger.CRITICAL
                # messages.append((level, message, exc))
            # elif last_check:
            #     monitoring[key]["last_check"] = last_check
            #     counter[key] = 0
            # else:
            #     counter[key] += 1


        # 5 is a period reasonable to check operation
        # at every object observed the period is multiplied by 5

        if messages:
            await queue_log.put(messages)

        await asyncio.sleep(delta_time)
        return [ipt, control, queue, tasks, monitoring, counter,
                stages, reserva], kwargs





async def run_task(task):
    task.create()


import socket

from contextlib import closing
   
def close_socket(address):
    with closing(socket.socket(socket.AF_INET, socket.SOCK_STREAM)) as sock:
        if sock.connect_ex(address) == 0:
            print(f"Port is open {address}")
        else:
            print(f"Port is not open {address}")
