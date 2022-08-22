import hashlib
import json
import time
import re
from data_shipper import config
from pypact.pact import Pact


def get_data_hash(data):
    return hashlib.sha256(json.dumps(data).encode('utf-8')).hexdigest()


def default_meta(sender="not real"):
    pact = Pact()
    return pact.lang.mk_meta(sender, config.chain_id, 0.0000001, 3000, time.time().__round__()-15, 28800)


def extract_device_id(pact_code):
    regex = r"(?<=\(free\.cyberfly_devices\.auth-device\s\")([0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12})"
    match = re.search(regex, pact_code)
    if match:
        return True, match.group(1)
    else:
        return False, "Invalid code"


def get_api_host(network_id):
    if network_id == "testnet04":
        return "https://api.testnet.chainweb.com/chainweb/0.0/testnet04/chain/{}/pact".format(config.chain_id)
    else:
        return "https://api.chainweb.com/chainweb/0.0/mainnet01/chain/{}/pact".format(config.chain_id)
