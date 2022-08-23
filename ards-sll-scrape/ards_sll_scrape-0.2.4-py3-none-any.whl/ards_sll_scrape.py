import sys
import json
import math
from datetime import datetime, timedelta, timezone
import time
import os

from aliyunsdkrds.request.v20140815.DescribeSlowLogRecordsRequest import DescribeSlowLogRecordsRequest
from aliyunsdkcore.client import AcsClient
import mysql.connector
from playhouse.mysql_ext import MySQLConnectorDatabase
from peewee import Model, CharField, IntegerField, DateTimeField, fn, SmallIntegerField


__version__ = "0.2.4"

cdbip = os.environ.get('cdbip')
cdbport = int(os.environ.get('cdbport', "3306"))
cdbuser = os.environ.get('cdbuser')
cdbpass = os.environ.get('cdbpass')
cdbdatabase = os.environ.get('cdbdatabase')

db = MySQLConnectorDatabase(cdbdatabase, host=cdbip, port=cdbport, user=cdbuser, password=cdbpass)


class BaseModel(Model):
    class Meta:
        database = db


class T_SLOWLOGRECORDS(BaseModel):
    DBInstanceId = CharField()
    DBName = CharField()
    SQLText = CharField()
    QueryTimes = IntegerField()
    LockTimes = CharField()
    ParseRowCounts = CharField()
    ReturnRowCounts = CharField()
    ExecutionStartTime = DateTimeField()
    HostAddress = CharField()
    QueryTimeMS = CharField()
    SQLHash = CharField()


class T_JOBSTATUS(BaseModel):
    jobid = IntegerField(primary_key=True)
    jobname = CharField()
    DBInstanceId = CharField()
    row = CharField()
    status = SmallIntegerField()
    gmt_create = DateTimeField()
    gmt_finsh = DateTimeField()
    gmt_begin = DateTimeField()
    gmt_end = DateTimeField()
    ext = CharField()

# for user in query:


class CollectSlowLogRecordsJob:
    def __init__(self, ak, secret, region_id, rdsinst_id, startT, endT, scrape_window: int, shift_time: int):
        self.aliyuncoreClient = AcsClient(ak, secret, region_id)

        self.startT = (datetime.now() - timedelta(minutes=scrape_window)) if startT is None else datetime.strptime(
            startT, "%Y-%m-%d %H:%M")
        self.endT = datetime(9999, 1, 1) if endT is None else datetime.strptime(
            endT, "%Y-%m-%d %H:%M")
        self.scrape_window = scrape_window
        self.shift_time = shift_time
        self.rdsinst_id = rdsinst_id
        self.tcdb = CollectDatabase()
        self.region_id = region_id

    def toCollectDB(self, record):
        record['DBInstanceId'] = self.rdsinst_id
        d = record['ExecutionStartTime']
        record['ExecutionStartTime'] = datetime.strptime(
            d + '+0000', "%Y-%m-%dT%H:%M:%SZ%z").astimezone()
        self.tcdb.insertSlowlogrecords(record)

    def recordJob(self, update, record):
        if update:
            record['err'] = ''
            record['gmt_finsh'] = datetime.now()
            self.tcdb.updateSlowlogJb(record)
        else:
            r = {}
            r['DBInstanceId'] = self.rdsinst_id
            r['jobname'] = "r:{}-i:{}-sw:{}-st:{}_{}-{}".format(self.region_id,
                                                                self.rdsinst_id, self.scrape_window, self.shift_time, record['s'], record['e'])
            r['status'] = 0
            r['gmt_create'] = datetime.now()
            r['gmt_begin'] = record['s']
            r['gmt_end'] = record['e']
            return self.tcdb.createSlowlogJob(r)

    def dateToStr(self, d):
        return d.strftime("%Y-%m-%dT%H:%MZ")

    def isScrape(self, e):
        return e < datetime.now() - timedelta(minutes=self.shift_time)

    def checkoutStartTime(self):
        q = self.tcdb.queryUnSuccessSlowLogJob(self.rdsinst_id)
        if len(q) == 0:
            q = self.tcdb.queryLastSuccessSlowLogJob(self.rdsinst_id)
            if(len(q) == 0):
                return (-1, self.startT)
            else:
                return (0, q[0][0])
        else:
            return q[0]

    def start(self):
        while True:
            jobId, _local_startT = self.checkoutStartTime()
            if jobId == 0:
                _local_startT += timedelta(minutes=self.scrape_window)
            _local_endT = _local_startT + timedelta(minutes=self.scrape_window)
            if self.isScrape(_local_endT):
                print("dbinst: {} -> start scrape {} - {}".format(self.rdsinst_id, _local_startT, _local_endT))
                arsrr = AliyunRdsSRR(self.aliyuncoreClient, self.rdsinst_id, self.dateToStr(_local_startT.astimezone(timezone.utc)),
                                     self.dateToStr(_local_endT.astimezone(timezone.utc)))
                cnt = 0
                if jobId in [0, -1]:
                    jobId = self.recordJob(False, {"s": _local_startT, "e": _local_endT})
                for i in arsrr.getAllSlr():
                    self.toCollectDB(i)
                    cnt += 1
                self.recordJob(True, {'row': cnt, 'jobid': jobId})
                print("dbinst: {} -> end scrape {} - {}, {} row".format(self.rdsinst_id,
                                                                        _local_startT, _local_endT, cnt))
                _local_startT = _local_endT
            else:
                print(
                    "dbinst: {} -> sleep waitting 60 second retry next scrape. next scrape start time: {}".format(self.rdsinst_id, _local_endT))
                time.sleep(60)


class CollectDatabase:
    def insertSlowlogrecords(self, slrData):
        T_SLOWLOGRECORDS.insert(**slrData).execute()

    def createSlowlogJob(self, data):
        return T_JOBSTATUS.insert(**data).execute()

    def updateSlowlogJb(self, data):
        T_JOBSTATUS.update(row=data['row'], ext=data["err"], gmt_finsh=datetime.now(
        ), status=1).where(T_JOBSTATUS.jobid == data["jobid"]).execute()

    def queryUnSuccessSlowLogJob(self, inst_id):
        return T_JOBSTATUS.select(T_JOBSTATUS.jobid, T_JOBSTATUS.gmt_begin).where(
            (T_JOBSTATUS.status == 0) & (T_JOBSTATUS.DBInstanceId == inst_id)).order_by(T_JOBSTATUS.gmt_begin.asc()).limit(1).tuples().execute()

    def queryLastSuccessSlowLogJob(self, inst_id):
        return T_JOBSTATUS.select(T_JOBSTATUS.gmt_begin).where(
            (T_JOBSTATUS.status == 1) & (T_JOBSTATUS.DBInstanceId == inst_id)).order_by(T_JOBSTATUS.gmt_begin.desc()).limit(1).tuples().execute()


class AliyunRdsSRR:

    pn = 1  # page number
    req = DescribeSlowLogRecordsRequest()

    def __init__(self, acsClient, instId, st: str, et: str, pageSize=100):
        self.acsClient = acsClient
        self.instId = instId
        self.st = st
        self.et = et
        self.pageSize = pageSize
        self.initSlrReq()

    def initSlrReq(self):
        self.req.set_accept_format('json')
        self.req.set_DBInstanceId(self.instId)
        self.req.set_StartTime(self.st)
        self.req.set_EndTime(self.et)
        self.req.set_PageSize(self.pageSize)

    def reqSlrByPn(self, pn: int):
        self.req.set_PageNumber(pn)
        response = self.acsClient.do_action_with_exception(self.req)
        return json.loads(response.decode('utf-8'))

    def getAllSlr(self):
        retry = 0
        while True:
            try:
                res = self.reqSlrByPn(self.pn)
                if self.isMoreData(res['PageRecordCount']):
                    for r in res["Items"]['SQLSlowRecord']:
                        yield r
                    self.pn += 1
                    time.sleep(1)
                else:
                    return
            except BaseException as e:
                if retry < 10:
                    print('inst id: {} scrape retry {}. error: {}'.format(self.instId, retry, e))
                else:
                    print('inst id: {} scrape faile.'.format(self.instId))
                    sys.exit(1)
                retry += 1
                time.sleep(60)

    def isMoreData(self, prc):
        return prc >= 1  # prc > 0


if __name__ == "__main__":
    import os
    ak = os.environ.get('ak')
    secret = os.environ.get('secret')
    region_id = os.environ.get('region_id')
    inst_id = os.environ.get('inst_id')
    start_time = os.environ.get('start_time', None)
    end_time = os.environ.get('end_time', None)
    scrape_window = int(os.environ.get('scrape_window', "1"))
    shift_time = int(os.environ.get('shift_time', "1"))

    # cdbip = os.environ.get('cdbip')
    # cdbport = int(os.environ.get('cdbport', "3306"))
    # cdbuser = os.environ.get('cdbuser')
    # cdbpass = os.environ.get('cdbpass')
    # cdbdatabase = os.environ.get('cdbdatabase')

    for env in ['ak', 'secret', 'region_id', 'inst_id', 'cdbip',  'cdbuser', 'cdbpass', 'cdbdatabase']:
        if os.environ.get(env) is None:
            print("env {} is Nnone.".format(env))
            sys.exit(1)

    job = CollectSlowLogRecordsJob(ak, secret, region_id, inst_id,
                                   start_time, end_time, scrape_window, shift_time)

    job.start()
