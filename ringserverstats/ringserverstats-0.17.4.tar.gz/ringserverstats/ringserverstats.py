__version__ = '0.17'
from datetime import datetime
import psycopg2
import geohash2
import logging
from geolite2 import geolite2
import re
from typing import List, Dict, Union
from hashlib import sha256
from base64 import b64encode
from os import access, R_OK, getenv
from os.path import isfile
from io import StringIO
from fdsnnetextender import FdsnNetExtender


Event = Dict[str,Union[str, Dict]]

logger = logging.getLogger('ringserverstats')
logger.setLevel(getenv('LOGLEVEL',logging.INFO))
# create console handler and set level to debug
ch = logging.StreamHandler()
ch.setLevel(logging.INFO)
# create formatter
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
# add formatter to ch
ch.setFormatter(formatter)
# add ch to logger
logger.addHandler(ch)

netextender = FdsnNetExtender()

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

def parse_ringserver_log(data: str) -> List[Event]:
    """
    Read a txlog file and parses information.
    Returns a list of events (dictionary)
    """
    logstart_pattern = r'START CLIENT (?P<hostname>\b(?:[0-9A-Za-z][0-9A-Za-z-]{0,62})(?:\.(?:[0-9A-Za-z][0-9A-Za-z-]{0,62}))*(\.?|\b)) \[(?P<ip>(?<![0-9])(?:(?:[0-1]?[0-9]{1,2}|2[0-4][0-9]|25[0-5])[.](?:[0-1]?[0-9]{1,2}|2[0-4][0-9]|25[0-5])[.](?:[0-1]?[0-9]{1,2}|2[0-4][0-9]|25[0-5])[.](?:[0-1]?[0-9]{1,2}|2[0-4][0-9]|25[0-5]))(?![0-9]))\] \((?P<agent>.*)\) @ (?P<time>[0-9]+-[0-9]+-[0-9]+ (?:2[0123]|[01]?[0-9]):(?:[0-5][0-9]):(?:[0-5][0-9])).*'
    logevent_pattern = '(?P<network>[A-Z0-9]*)_(?P<station>[A-Z0-9]*)_(?P<location>[A-Z0-9]*)_(?P<channel>[A-Z0-9]*)/MSEED (?P<bytes>[0-9]+) (?P<packets>[0-9]+)'
    temporary_network_pattern = r'[0-9XYZ][0-9A-Z]'
    georeader = geolite2.reader()
    process_events = True
    events = []
    linecount = 0
    for log in iterable_log(data):
        linecount +=1
        logger.debug(f"Parsing log {log}")
        # log line exemple: START CLIENT 52.red-88-2-197.staticip.rima-tde.net [88.2.197.52] (SeedLink|SeedLink Client) @ 2016-11-28 00:00:00 (connected 2016-11-26 16:37:07) TX
        if log.startswith('START CLIENT'):
            events_data = re.search(logstart_pattern, log)
            if events_data == None:
                logger.warning("Unable to parse START log at line %d : %s"%(linecount, log))
                process_events = False
                continue
            events_data = events_data.groupdict()
            location = georeader.get(events_data['ip'])
            # hash location and get the city name
            if location != None:
                events_data['geohash'] = geohash2.encode(location['location']['latitude'], location['location']['longitude'])
                try:
                    events_data['countrycode'] = location['country']['iso_code']
                except KeyError:
                    events_data['countrycode'] = ''
                try:
                    events_data['city'] = location['city']['names']['en']
                except KeyError:
                    events_data['city'] = ''
            else:
                logger.warning("No location available at line %d : %s\nAssuming it was in Grenoble"%(linecount, log))
                events_data['geohash'] = 'u0h0fpnzj9ft'
                events_data['city'] = 'Grenoble'
                events_data['countrycode'] = 'FR'
            # hash hostname
            events_data['client'] = events_data['hostname']
            events_data['hostname'] = b64encode(sha256(events_data['hostname'].encode()).digest())[:12].decode() # overcomplicated oneliner to hash the hostname
            logger.debug(f"Parsed log: {events_data}")
        elif log.startswith('END CLIENT'):
            process_events = True
        elif process_events:
            # line exemple :
            # FR_SURF_00_HHZ/MSEED 21511168 42014
            event = re.search(logevent_pattern, log)
            if event == None:
                logger.warning("Unable to parse log at %d : %s"%(linecount, log))
                continue
            event = event.groupdict()
            if re.match(temporary_network_pattern, event['network']):
                event['network'] = netextender.extend(event['network'], datetime.now().strftime('%Y-%m-%d'))
            logger.debug(event)
            events.append({**events_data, **event})
    return(events)

def register_events(events: List[Event], dburi: str):
    if len(events) == 0:
        return(0)
    logger.info("Storing %d metrics"%len(events))
    strio = StringIO()
    # Créer une chaine de caractère avec tous les éléments séparés par \t
    items = []
    for e in events:
        items.append('\t'.join((e['time'],
                                e['bytes'],
                                e['network'],
                                e['station'],
                                e['location'],
                                e['channel'],
                                e['city'],
                                e['countrycode'],
                                e['agent'],
                                e['geohash'],
                                e['client']))+'\n'
        )
    strio.writelines(items)
    strio.seek(0)
    try:
        conn = psycopg2.connect(dburi)
        cur = conn.cursor()
        cur.copy_from(strio, 'ringserver_events')
        cur.close()
        conn.commit()
        conn.close()
    except Exception as e:
        logger.error("Error writing to postgres %s database"%(dburi))
        logger.error(e)
    logger.info("Wrote %d entries between '%s' and '%s' to %s"%(len(items), events[0]['time'], events[-1]['time'], dburi))
    return(len(items))
