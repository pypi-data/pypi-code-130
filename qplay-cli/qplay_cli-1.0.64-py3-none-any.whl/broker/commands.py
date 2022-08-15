import click

from qplay_cli.broker.zerodha.z_broker import ZBroker
from quantplay.brokerage.angelone.angel_broker import AngelBroker
from quantplay.config.qplay_config import QplayConfig
from qplay_cli.api_clients.user_api import UserAPIClient

@click.group()
def broker():
    pass

@broker.command()
@click.option('--broker_name', default=None)
def generate_token(broker_name):
    if broker_name == None:
        print("--broker_name [Zerodha/AngelOne] argument is missing")
        exit(1)
    if broker_name not in ["Zerodha", "AngelOne"]:
        print("broker_name must be in [Zerodha/AngelOne]")
        exit(1)

    credentials = QplayConfig.get_credentials()
    access_token = credentials['DEFAULT']['access_token']

    if broker_name == "Zerodha":
        ZBroker().generate_token()
    elif broker_name == "AngelOne":
        AngelBroker(["minute"], None)
        angel_one_wrapper = QplayConfig.get_value(AngelBroker.angelone_wrapper)
        UserAPIClient().update_info(access_token, {
            'angel_one_wrapper' : angel_one_wrapper
        })



    