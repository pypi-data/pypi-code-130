from pypact.utils import get_headers
from data_shipper import utils
import requests as rt
from jsonschema import validate
from data_shipper import schema
import json


def check_auth(cmd, network_id):
    res = rt.post(utils.get_api_host(network_id)+'/api/v1/local', json=cmd, headers=get_headers())
    if res.ok:
        if res.json()['result']['status'] == 'success':
            return True
        else:
            return False
    else:
        return False


def validate_device_id(device_id, msg):
    try:
        validate(instance=msg, schema=schema.pact_cmd_schema)
        cmd = json.loads(msg['cmd'])
        validate(instance=cmd, schema=schema.cmd_schema)
        matched, d_id = utils.extract_device_id(cmd['payload']['exec']['code'])
        if matched:
            if d_id == device_id:
                return True
            else:

                return False
        else:
            return False
    except Exception as e:
        print(e.__str__())
        return False
