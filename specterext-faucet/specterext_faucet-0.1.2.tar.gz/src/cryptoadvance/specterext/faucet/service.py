import logging

from cryptoadvance.specter.services.service import Service, devstatus_alpha, devstatus_prod, devstatus_beta
# A SpecterError can be raised and will be shown to the user as a red banner
from cryptoadvance.specter.specter_error import SpecterError
from flask import current_app as app
from cryptoadvance.specter.wallet import Wallet
from flask_apscheduler import APScheduler

logger = logging.getLogger(__name__)

class FaucetService(Service):
    id = "faucet"
    name = "Faucet Service"
    icon = "faucet/img/logo.png"
    logo = "faucet/img/logo.png"
    desc = "Control your regtest node."
    has_blueprint = True
    blueprint_module = "cryptoadvance.specterext.faucet.controller"
    devstatus = devstatus_beta
    isolated_client = True

    # TODO: As more Services are integrated, we'll want more robust categorization and sorting logic
    sort_priority = 2

    # ServiceEncryptedStorage field names for this service
    # Those will end up as keys in a json-file
    SPECTER_WALLET_ALIAS = "wallet"

    return_addr = ""