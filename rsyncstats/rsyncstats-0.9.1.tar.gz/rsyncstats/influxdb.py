from influxdb import InfluxDBClient

def influx_group_query(idbclient: InfluxDBClient, start: int, end: int):
    """
    From a start and end (should be the first and last event in epoch format), make a grouping query to store to a downsampled measurement called rsyncstats
    parameter idbclient must be an instance of InfluxDBClient.
    """
    # check if start < end
    if end < start:
        raise ValueError("Start time (%d) must be before end time (%d)"%(start, end))

    # influxql request :
    query = "select sum(sent) as sent, sum(received) as received, sum(total) as total into rp_rsyncstats.rsyncstats from rp_rsyncevents.rsyncevents where time>=%ds and time<=%ds group by module,hosthash,geohash,city,time(1d) fill(none)"%(start, end)
    logger.debug("Sending grouping query: "+query)
    try:
        result = idbclient.query(query)
        logger.info(("Result: {0}".format(result)))
    except Exception as e:
        logger.error("Error writing group queries to influxdb")
        logger.error(e)


def influxdb_send_data(events, dburi) -> bool:
    """
    Sends data into influxdb
    """
    influxdb_json_data = []
    for event in  events:
        # get the first event time
        if firstevent_time == 0 or firstevent_time > event['timestamp']:
            firstevent_time = event['timestamp']
        # get the last event time
        if lastevent_time == 0 or lastevent_time < event['timestamp']:
            lastevent_time = event['timestamp']
        # Constructing an influxdb data from the event
        logger.debug(event)
        influxdb_json_data.append(
            {"measurement": 'rsyncevents',
             "tags": {
                 "module": event['module'],
                 "geohash": event['geohash'],
                 "city":    event['city'],
                 "hosthash": event['hosthash']
             },
             "time": event['endtime'],
             "fields": {
                 "sent": int(event['sentbytes']),
                 "received": int(event['receivedbytes']),
                 "total": int(event['totalbytes'])
             }
            }
        )


    logger.info("Sending %d metrics"%len(influxdb_json_data))

    try:
        logger.debug("host     = "+dbhost)
        logger.debug("database = "+dbname)
        logger.debug("username = "+dbuser)
        cxparams = re.search('^(?P<dbuser>\w):(?P<password>\w)@(?P<dbhost>\w):(?P<dbport>\w)/(?P<dbname>\w)',dburi)
        client = InfluxDBClient(host     = cxparams['dbhost'],
                                port     = cxparams['dbport'],
                                database = cxparams['dbname'],
                                username = cxparams['dbuser'],
                                password = cxparams['password'],
                                ssl      = False,
                                verify_ssl = False
        )
        i=0
        j=10000
        while j < len(influxdb_json_data) or i==0:
            logger.info("%d/%d"%(j,len(influxdb_json_data)))
            influxdb_send_data(client, influxdb_json_data[i:j])
            i=j
            j+=10000
        # Now lets group those events in statistics
        influx_group_query(client, firstevent_time, lastevent_time)
        client.close()
    except Exception as e:
        logger.error("Error writing to influxdb %s:%d database %s"%(dbhost,dbport,dbname))
        logger.error(e)

    try:
        idbclient.write_points(data, time_precision='s', retention_policy='rp_rsyncevents')
    except Exception as e:
        logger.error("Unexpected error writing data to influxdb")
        logger.error(e)
        return False
    return True
