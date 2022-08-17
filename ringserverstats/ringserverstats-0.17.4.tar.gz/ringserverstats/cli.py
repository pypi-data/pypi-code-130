from ringserverstats import ringserverstats
import click

@click.command()
@click.option('--dburi', 'dburi', help='Postgres URI (eg. postgresql://[user[:password]@][host][:port][/dbname])', envvar='DATABASE_URI')
@click.argument('files', type=click.Path(exists=True), nargs=-1)
def cli(dburi: str, files):
    for f in files:
        events = ringserverstats.parse_ringserver_log(f)
        ringserverstats.register_events(events, dburi)
