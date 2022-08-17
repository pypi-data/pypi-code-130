import click
import pandas as pd
from src.DI import DI
from src.application.NginxToDatabase import NginxToDatabase
from src.domain.Server.Server import Server
from src.infrastructure.CanadaThreeDatabase import CanadaThreeDatabase


@click.command()
def process_remote_nginx_logs():
    remote_servers: list[Server] = []
    tb_nginx = Server(host="tbnginxasroot", source_path="/var/log/nginx/", name="TB Nginx Server")
    remote_servers.append(tb_nginx)
    local_server = Server(source_path=DI.logs_path(), name="Local Server", includes="seb.access.log*")
    database = CanadaThreeDatabase()
    database.connect()
    database.truncate_table()
    NginxToDatabase(pd, database=database).process(remote_servers, local_server)


if __name__ == "__main__":
    process_remote_nginx_logs()
