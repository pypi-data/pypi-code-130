import hashlib
import json
import time
import re
from data_shipper import config
from pypact.pact import Pact

pact = Pact()

def get_data_hash(data):
    return hashlib.sha256(json.dumps(data).encode('utf-8')).hexdigest()


def default_meta(sender="not real"):

    return pact.lang.mk_meta(sender, config.chain_id, 0.000001, 80000, time.time().__round__()-15, 28800)


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


def write_rules_json(rules):
    rules_object = json.dumps(rules, indent=4)
    with open("rules.json", "w") as outfile:
        outfile.write(rules_object)


def read_rules_json() -> dict:
    with open('rules.json', 'r') as openfile:
        json_object = json.load(openfile)
        return json_object


def make_rule(rule: dict) -> str:
    rule = json.loads(rule)
    variable = rule['variable']
    operator = rule['operator']
    value = rule['value']
    if not is_number(value):
        value = '"{}"'.format(value)
    return variable+' '+operator+' '+value


def publish(client, data, network_id, key_pair):
    data = json.loads(data)
    device_list = make_list(data['to_devices'])
    for device_id in device_list:
        cmd = make_cmd(device_id, data['data'], network_id, key_pair)
        try:
            client.publish(device_id, payload=json.dumps(cmd))
            print("published to device {}".format(device_id))
        except Exception as e:
            print(e.__str__())


def make_cmd(device_id, data, network_id, key_pair):
    pact_code = '({}.{}.auth-device "{}")'.format(config.namespace, config.module, device_id)
    cmd = {
        "pactCode": pact_code,
        "envData": {"device_exec": data},
        "meta": default_meta(),
        "networkId": network_id,
        "nonce": time.time().__round__() - 15,
        "keyPairs": [{"publicKey": key_pair['publicKey'], "secretKey":key_pair['secretKey'],
                      "clist": [{'name': 'coin.GAS', 'args': []},
                                {'name': '{}.{}.DEVICE_GUARD'.format(config.namespace, config.module),
                                'args': [device_id]}]}]
    }

    signed_cmd = pact.api.prepare_exec_cmd(cmd['pactCode'], cmd['envData'], cmd['meta'], cmd['networkId'],
                                           cmd['nonce'], cmd['keyPairs'])
    return signed_cmd


def is_number(s):
    try:
        complex(s)
    except ValueError:
        return False
    return True


def make_list(s):
    if isinstance(s, list):
        return s
    return [s]
