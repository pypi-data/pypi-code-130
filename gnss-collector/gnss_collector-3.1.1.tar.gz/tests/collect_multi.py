import asyncio
from tasktools.taskloop import TaskLoop
from gnss_collector.engine.steps import (
    CollectSteps as CSteps, 
    DBSteps, 
    Logger, 
    ORMSteps,
    ControlActions)

from dataprotocols import Gsof

import click
from rich import print
from data_rdb import Rethink_DBS
from crb import RingBuffer, Data
from basic_logtools.filelog import LogFile as FileLog
from datetime import timedelta, datetime
from dataclasses import dataclass
from tblib import pickling_support
pickling_support.install()
import multiprocessing as mp
import concurrent.futures
from multiprocessing import Manager, Queue
from networktools.messages import MSGException, MessageLog
from networktools.colorprint import gprint, bprint, rprint
from pathlib import Path
from typing import Dict,Set
from dataclasses import field
from networktools.time import timestamp, now, gps_time
import logging
import sys
from asyncio import shield, wait_for
from rethinkdb import RethinkDB
import functools


rdb = RethinkDB()
DATA_KEYS = {"DT_GEN":"dt_gen","DELTA_TIME":"latency"}

from dataclasses import dataclass
from dataclasses_json import dataclass_json

def rdbnow():
    return rdb.iso8601(now().isoformat())


@dataclass_json
@dataclass(frozen=True)
class StationBase:
    code:str = None
    host:str = None 
    port:int = 5017

"""
Create station connection
"""

@dataclass
class CollectorMulti:
    collection:Dict[str,StationBase] = field(default_factory= lambda: dict())
    stations:Dict[str,Set[str]] = field(default_factory= lambda: dict())

    lnproc:int = 2
    queue_log:mp.Queue = None
    log_path:Path =  Path(__file__).resolve().absolute().parent / "log"
    assigned_tasks:Dict[str,str] = field(default_factory= lambda: dict())
    status_sta:Dict[str,str] = field(default_factory= lambda: dict())
    changes:Dict[str,str] = field(default_factory= lambda: dict())
    # now is importante for group
    # code: str = None
    # host: str = 'localhost'
    # port: int = 5017

    db_data:Dict[str,str] = field(default_factory= lambda: dict())

    idc:Dict[str,str] = field(default_factory= lambda: dict())
    status_conn:Dict[str,str] = field(default_factory= lambda: dict())
    status_sta:Dict[str,str] = field(default_factory= lambda: dict())
    first_time:Dict[str,str] = field(default_factory= lambda: dict())
    db_instances_sta:Dict[str,str] = field(default_factory= lambda: dict())


    mu:float = 0.5
    factor:float = 0.8
    sigma:float = 0.3
    buffer_size:int = 120*60
    u_base:float = mu + factor * sigma 
    acc:int = 3

    def set_status_sta(self, ids, value):
        if isinstance(value, bool):
            self.status_sta[ids] = value
            # True: connect to sta
            # False: maintain status_conn01

    def set_status_conn(self, ids, value):
        if isinstance(value, bool):
            self.status_conn[ids] = value
            # True: connected
            # False: unconnected


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


    def manage_tasks(self, ipt:str="test_collector_multi"):
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

        args = [ipt, queue_db,]
        task_name = f"queue_db:{ipt}"
        task_db = TaskLoop(
            self.queue_join,
            args,
            {},
            **{"name": task_name})
        task_db.set_name(task_name)
        task_db.create()

        # Queue log join
        queue_log = asyncio.Queue()

        args = [ipt, queue_log,]
        task_name = f"queue_log_join:{ipt}"
        task_db = TaskLoop(
            self.queue_log_join,
            args,
            {},
            **{"name": task_name})
        task_db.set_name(task_name)
        task_db.create()


        queue_control = asyncio.Queue()

        tasks = []
        self.assigned_tasks[ipt] = {}
        new_dict = {}
        # inicia n tareas en proceados
        seleccion = self.stations[ipt]
        for code in seleccion:
            ico = f"ICO_{code}"
            new_dict[ico] = code
        self.assigned_tasks[ipt] = new_dict
        tasks_on_this_ipt = self.assigned_tasks.get(ipt)
        

        #tasks.append(db_task)
        #self.status_tasks["db_task"] = task_name 
        # end db task
        for ico in tasks_on_this_ipt.keys():
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
                    {"queue_db": queue_db},
                    **{"name": task_name})
                #task_1.set_name(task_name)
                task_1.create()
                tasks.append(task_1)
                key = f"collect_{ico}"
                #self.status_tasks[key] = task_name
            except Exception as ex:
                print(
                    "Error en collect_task, gather stations, process_sta(task) %s, error %s"
                    % (ipt, ex))
                print(ex)
                raise ex
        if not loop.is_running():
            loop.run_forever()


    def add_sta_instance(self, ids, loop):
        """
        Crear la instancia que accederá a los datos
        a través del socket
        """
        print(f"Creating instance for {ids}")
        station = self.collection[ids] 
        kwargs = station.to_dict()
        kwargs['sock'] = None
        kwargs['timeout'] = 20
        kwargs["raise_timeout"] = False
        kwargs['loop'] = loop
        instance = Gsof(**kwargs)
        
        table_name = f"{station.code}_GSOF"
        print("Result _>", instance, table_name)
        return instance, table_name

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



    async def process_data(self, ipt, ico, control, sta_insta,
                           last_data, last_time, counter,
                           queue_control, 
                           queue_log_join,
                           *args, **kwargs):
        loop = asyncio.get_event_loop()
        ids = self.assigned_tasks.get(ipt, {}).get(ico, None)
        assigned_tasks = self.assigned_tasks.get(ipt, {})
        ids = assigned_tasks.get(ico)
        level = Logger.INFO
        messages = []
        message = ""
        task_name = f"process_sta_task:{ipt}:{ico}"
        coroname = "process_data"
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

            if control == CSteps.CREATE:
                # step 0 initialize the objects, source and end
                exc = MSGException()
                try:
                    sta_insta, table_name = self.add_sta_instance(ids,
                                                                  loop)

                    rprint(f"Created station {sta_insta} -> {table_name}")
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
                        messages.append(MessageLog(rdbnow(), coroname, level, message, MSGException()))
                    
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
            await asyncio.sleep(5)
        
        exc = MSGException()
        message = ""

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

                    await queue_control.put((
                        task_name,
                        now(),
                        stage,
                        future))


                    idc = await wait_for(
                        shield(future),
                        timeout=20)

                    gprint(f"Connected station {sta_insta} -> {table_name}, idc {idc}")

                    try:
                        future.exception()
                    except Exception as e:
                        exc = MSGException(*sys.exc_info())

                        message = f"Excepcion at {ipt} tipo {e} for {sta_insta}"
                        messages.append(MessageLog(rdbnow(), coroname, Logger.ERROR, message, exc))

                    if idc:
                        self.idc[ids] = idc
                        self.set_status_sta(ids, True)
                        self.set_status_conn(ids, True)
                        self.first_time[ids] = False
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

                # si ya esta conectado :), obtener dato
                if message:
                    messages.append(MessageLog(rdbnow(), coroname, level, message, exc))

            """
            Si ya está inicializado y conectad
            proceder a obtener datos
            """
            sta_dict = {}
            if control == CSteps.COLLECT and table_name:
                ring_buffer = kwargs.get("ring_buffer")
                code = sta_insta.station
                idc = self.idc.get(ids)
                exc = MSGException()
                # just for checking
                # step 1.b collect data and process to save the raw data
                try:
                    # set idc and header
                    # set_header =
                    # wait_for(sta_insta.get_message_header(idc),
                    #          timeout=self.timeout)
                    async def get_records():
                        set_header = sta_insta.get_message_header(idc)
                        await shield(set_header)
                        get_records = wait_for(
                            sta_insta.get_records(),
                            timeout=10)

                        future = asyncio.create_task(get_records)
                        # stage = "collect"

                        # await queue_control.put((
                        #     task_name, 
                        #     now(), 
                        #     stage, 
                        #     future))

                        # TODO ADD STAGE GET RECORD
                        done, sta_dict = await shield(future)
                        dt0, source = gps_time(sta_dict, sta_insta.tipo)
                        dt_iso = rdb.iso8601(dt0.isoformat())
                        rnow = now()
                        recv_now = rdb.iso8601(rnow.isoformat())
                        # print(rnow)
                        delta = (rnow - dt0).total_seconds()
                        sta_dict.update({
                            'DT_GEN': dt_iso,
                            'DT_RECV': recv_now,
                            "DELTA_TIME": delta})
                        data = Data(**{v:sta_dict.get(key) for key,v in DATA_KEYS.items()})
                        ring_buffer.add(data)
                        # Control criteria
                        await queue_db.put((table_name, sta_dict))
                        await asyncio.sleep(0)# change to another task
                        return delta, rnow 
                    # queue_db.put((table_name, sta_dict))
                    delta, last_data = await get_records()
                    print(last_data, table_name, delta)
                    # control ring buffer
                    # particular value for every station
                    # u_base = self.mu + self.factor * self.sigma 
                    n = 0
                    mu_control = lambda delta: delta + ring_buffer.mu**3
                    # print(table_name, "MU CONTROL", mu_control,
                    #       "MU",ring_buffer.mu,
                    #       self.u_base,"Priority", mu_control >=
                    # self.u_base)
                    inside = False
                    while  mu_control(delta) >= self.u_base:
                        inside = True
                        print("Giving priority to", table_name,
                              "TIMES", self.acc)
                        lvl = Logger.WARNING
                        msg = f"Giving priority to {table_name}, latency {delta}, iter {n}"
                        messages.append(MessageLog(rdbnow(), coroname, lvl, msg, exc))
                        for i in range(self.acc):
                            delta, last_data = await get_records()
                            n += 1
                    if inside:
                        print("Last delta", table_name, delta, ring_buffer)

                    stage = "sendq"

                    # await queue_control.put((
                    #     task_name, 
                    #     now(), 
                    #     stage, 
                    #     {"DT_GEN":dt0.isoformat(),"station":table_name}))

                    counter += 1
                    if counter == 60:
                        print(now(), counter, table_name, delta,
                              ring_buffer)
                        print(self.u_base, ring_buffer.mu)
                        message = f"At ipt {ipt} ico {ico} sended successfully last {counter}"+\
                            f" messages for {code} at {last_data}"
                        level = Logger.INFO
                        messages.append(MessageLog(rdbnow(), coroname, level, message, MSGException()))   
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
                    messages.append(MessageLog(rdbnow(), coroname, level, message, exc))
                    messages.append(MessageLog(rdbnow(), coroname, lvl, msg, MSGException()))

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
                    messages.append(MessageLog(rdbnow(), coroname, level, message, exc))
                    messages.append(MessageLog(rdbnow(), coroname, lvl, msg, MSGException()))
                    control = CSteps.CONNECT
                except asyncio.ConnectionError as e:
                    exc = MSGException(*sys.exc_info())
                    message = f"At ipt {ipt}, ico {ico} Error de conexión para conectar instancia de estación {sta_insta}"
                    level = Logger.ERROR
                    kwargs["origin_exception"] = f"PD_T13_00 + {sta_insta}"                                     
                    msg, lvl = await self.reset_station_conn(sta_insta, ids, idc)

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
                #messages.append((level, message, {}))
                messages.append(MessageLog(rdbnow(), coroname, level, message, exc))

            # control last data received
            # si aun no hay last_data
            if not last_data:
                control = CSteps.CONNECT
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
        out = [ipt, ico,  control, 
               sta_insta, last_data, 
               last_time, counter, queue_control, 
               queue_log_join]
        if not self.status_sta.get(ids):
            out = [ipt, ico,  control, 
                   sta_insta, last_data,
                   last_time, counter, queue_control, 
                   queue_log_join]

        if messages:
            await queue_log_join.put(messages)
            #log.save(level, message)
        if level not in {logging.INFO, logging.DEBUG}:
            await asyncio.sleep(5)
        return out, kwargs


    async def queue_join(self, ipt, queue_db, **kwargs):
        """
        receiva all data by thread and send tp db process / print
        """
        if not queue_db.empty():
            dataset = {}
            
            for i in range(queue_db.qsize()):
                table, item = await queue_db.get()
                if table not in dataset:
                    dataset[table] = []
                dataset[table].append(item)
            if len(dataset)>10:
                print(now(), ipt, "Dataset to save", len(dataset))
                print(dataset)
            # queue_to_db.put(dataset)
            # print("Saving", dataset)
        return (ipt, queue_db), kwargs



    async def queue_log_join(self, ipt, queue_log, **kwargs):
        """
        By thread/process receive all messages and join to send to log
        process task -> manage_log
        
        """
        if not queue_log.empty():
            dataset = []
            
            for i in range(queue_log.qsize()):
                message_list = await queue_log.get()
                dataset += message_list

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
                    print(now(), msg)
                    if msg.exception:
                        pass
                        #log.logger.error(str(msg), 
                        #                 exc_info=msg.exc)
                    else:
                        log.logger.log(*msg.log)               

            queue_log.task_done()
        return (log, queue_log), kwargs


    def manage_log_task(self):
        rprint("Manage log task doing")
        loop = asyncio.get_event_loop()
        log = FileLog("Engine@Collector",
                      f"LogTask",
                      "localhost@atlas",
                      path=self.log_path,
                      max_bytes=10100204)
        args = [log, self.queue_log]
        task_name = "log_task"
        task = TaskLoop(self.manage_log, args, {}, name=task_name)
        task.create()
        if not loop.is_running():
            loop.run_forever()


import csv 

@click.command()
@click.option("--n", type=int, default=3)
@click.option("--workers", type=int, default=5)
def run(n, workers):
    reservar = 2
    stations = {str(i):set() for i in range(workers-reservar)}
    skeys = set(stations.keys())
    filename = Path(__file__).parent / "station.csv"
    keys = {"code", "host", "port"}
    collection = {}
    with filename.open() as f:
        reader = csv.DictReader(f, delimiter=';')
        for data in reader:
            code = data["code"]
            station = StationBase(**{key:data[key] for key in keys}) 
            elem = skeys.pop()
            if len(stations[elem])< n:
                collection[code] = station
                stations[elem].add(code) 
            if not skeys:
                skeys = set(stations.keys())

    print(stations)
    loop = asyncio.get_event_loop()
    lnproc = len(stations)
    with concurrent.futures.ProcessPoolExecutor(workers) as executor:
        m = Manager()
        queue_log = m.Queue()
        collector = CollectorMulti(collection, stations, lnproc, queue_log)
        loop.run_in_executor(executor, collector.manage_log_task)
        for i in stations:
            loop.run_in_executor(executor,
                                 functools.partial(collector.manage_tasks,
                                                   ipt=f"{i}"))

        loop.run_forever()

if __name__ == "__main__":
    run()
