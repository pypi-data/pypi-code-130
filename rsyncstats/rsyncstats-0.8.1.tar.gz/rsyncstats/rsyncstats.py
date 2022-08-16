__version__ = '0.8'

from os import access, R_OK, getenv
from os.path import isfile
from io import StringIO
import psycopg2
import geohash2
import logging
from geolite2 import geolite2
import re
from typing import List, Dict, Union
from hashlib import sha256
from base64 import b64encode
from datetime import datetime


Event = Dict[str,Union[str, Dict]]

logger = logging.getLogger('rsyncstats')
logger.setLevel(getenv('LOGLEVEL'),logging.INFO)
# create console handler and set level to debug
ch = logging.StreamHandler()
ch.setLevel(logging.INFO)

# create formatter
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')

# add formatter to ch
ch.setFormatter(formatter)

# add ch to logger
logger.addHandler(ch)


def iterable_log(data: str):
    """
    Generator to iterate over lines in file or in string.
    Very nice.
    """
    if isfile(data) and access(data, R_OK):
        with open(data,'r') as loglines:
            for logline in loglines:
                yield logline.strip()
    else:
       # Consider data is the log lines to analyse
       for logline in data.split("\n"):
           yield logline


def parse_log(filename: str) -> List[Event]:
    """
    Read a rsync log file and parses information.
    Returns a list of events (dictionary)
    """
    global_pattern = r'(?P<timestamp>20[0-9][0-9]-[0-9]{1,2}-[0-9]{1,2}\s+[012][0-9]:[0-5][0-9]:[0-5][0-9])\s+\S+ rsyncd\[(?P<pid>[0-9]+)\]: (?P<logtype>(rsync (to|on)|sent)) ((?P<sentbytes>[0-9]+) bytes\s+received (?P<receivedbytes>[0-9]+) bytes\s+total size (?P<totalbytes>[0-9]+)|(?P<module>[-\w_]+)(?P<directory>\/\S*) from (?P<user>\S+)@(?P<hostname>\S+) \((?P<clientip>\S+)\))'
    georeader = geolite2.reader()
    events = []
    events_buffer = {} # dict of events started but not ended. Key is the PID
    linecount = 0

    for log in iterable_log(filename):
        linecount +=1
        event = re.search(global_pattern, log)
        if event == None:
            logger.debug("Ignoring log at %s:%d : %s"%(filename, linecount, log))
            continue
        event_data = event.groupdict()
        # store time as epoch
        event_data['timestamp'] = event_data['timestamp']
        # 2 possible logs are captured by the pattern : connection log and transfer log.
        if event_data['logtype'] == 'rsync to' or event_data['logtype'] == 'rsync on':
            location = georeader.get(event_data['clientip'])
            # hash location and get the city name
            if location != None:
                event_data['geohash'] = geohash2.encode(location['location']['latitude'], location['location']['longitude'])
                try:
                    event_data['city'] = location['city']['names']['en']
                except KeyError:
                    event_data['city'] = ''
            else:
                logger.warning("No location available at %s:%d : %s\nAssuming it was in Grenoble"%(filename, linecount, log))
                event_data['geohash'] = 'u0h0fpnzj9ft'
                event_data['city'] = 'Grenoble'
            # hash hostname
            event_data['hosthash'] = b64encode(sha256(event_data['hostname'].encode()).digest())[:12].decode('utf-8') # overcomplicated oneliner to hash the hostname
            logger.debug("Storing event in buffer (pid %s)"%(event_data['pid']))
            event_data = {k:event_data[k] for k in event_data if event_data[k] != None}
            events_buffer[event_data['pid']] = event_data
            logger.debug(event_data)
        elif event_data['logtype'] == 'sent':
            event_data['endtime'] = event_data['timestamp']
            # get the data from the events_buffer and merge with what we have
            try:
                previous_data = events_buffer.pop(event_data['pid'])
                events.append({ **event_data, **previous_data })
            except KeyError as e:
                logger.info("Event will not be accounted : "+str(event_data))
    return(events)

def register_events(events, dburi):
    if len(events) == 0 :
        return(0)
    logger.info("Storing %d metrics"%len(events))
    strio = StringIO()
    # Créer une chaine de caractère avec tous les éléments séparés par \t
    items = []
    for e in events:
        items.append('\t'.join((e['timestamp'],
                                e['sentbytes'],
                                e['receivedbytes'],
                                e['totalbytes'],
                                e['module'],
                                e['user'],
                                e['endtime'],
                                e['geohash'],
                                e['hosthash'],
                                e['hostname'],
                                e['clientip'] ))+'\n'
        )
    strio.writelines(items)
    strio.seek(0)
    try:
        conn = psycopg2.connect(dburi)
        cur = conn.cursor()
        cur.copy_from(strio, 'rsyncstats')
        cur.close()
        conn.commit()
        conn.close()
    except Exception as e:
        logger.error("Error writing to postgres %s database"%(dburi))
        logger.error(e)
    logger.info("Wrote %d entries between '%s' and '%s' to %s"%(len(items), events[0]['timestamp'], events[-1]['timestamp'], dburi))
    return(len(items))
