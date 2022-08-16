import click
from rsyncstats import rsyncstats
import logging


@click.command()
@click.option('--dburi', 'dburi', help='Postgresql or Influxdb URI (postgresql://user:pass@dhost:port/database or influx://user:pass@dbhost:port/database)', envvar='DBURI')
@click.argument('files', type=click.Path(exists=True), nargs=-1)
def cli(dburi, files):
    for f in files:
        logging.info("Opening file %s"%(f))
        # Parsing events from a logfile
        lastevent_time = 0
        firstevent_time = 0
        events = rsyncstats.parse_log(f)
        rsyncstats.register_events(events, dburi)
