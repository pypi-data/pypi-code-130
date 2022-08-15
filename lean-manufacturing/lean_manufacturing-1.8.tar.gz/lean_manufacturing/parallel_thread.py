import pymongo
from datetime import datetime
from time import sleep
localdb                             = pymongo.MongoClient('mongodb://localhost:27017')

def track_availability():
    started_setup_at                = datetime.now()
    minute                          = started_setup_at.replace(second=0, microsecond=0)
    register_availability           = localdb['monitor']['availability'].update_one({'minute': minute}, {'$set': {'availability':True}}, upsert=True)
    sleep(60)
    track_availability()
