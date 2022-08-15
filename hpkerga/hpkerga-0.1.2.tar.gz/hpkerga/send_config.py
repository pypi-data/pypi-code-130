import json
import logging
import os
from pprint import pprint

import requests
import treefiles as tf

CONF_FNAME = tf.Str(os.path.expanduser("~")) / ".hpkerga_conf.yaml"


def get_token() -> str:
    fname = tf.f(__file__) / ".secret_token.json"
    if not tf.isfile(fname):
        tf.dump_json(fname, {})
    res = tf.load_json(fname)
    force = "access_token" not in res
    if not tf.greedy_download(fname, force=force):
        return res["access_token"]
    else:
        from getpass import getpass

        name = input("Usename: ")
        password = getpass()
        data = f"username={name}&password={password}"

        api_endpoint = "https://api.kerga.fr/u/please-give-me-a-token"
        headers = {
            "Accept": "application/json",
            "Content-Type": "application/x-www-form-urlencoded",
        }
        r = requests.post(url=api_endpoint, headers=headers, data=data)
        tf.dump_str(fname, json.dumps(r.json()))
        return get_token()


def check_conf(path):
    if not tf.isfile(path):
        tf.copyFile(tf.f(__file__) / "empty_conf.yaml", path)


def send_config(yaml_path: str):
    check_conf(yaml_path)
    API_TOKEN = get_token()
    API_ENDPOINT = "https://api.kerga.fr/hp/set-my-data"

    headers = {
        "Accept": "application/json",
        "Content-Type": "application/json",
        "Authorization": "Bearer " + API_TOKEN,
    }
    data = tf.load_yaml(yaml_path)
    r = requests.post(url=API_ENDPOINT, headers=headers, json=data)
    log.info(f"Reponse ({r.status_code}): {r.json()}")


def check_file():
    API_TOKEN = get_token()
    API_ENDPOINT = "https://api.kerga.fr/hp/"

    headers = {
        "Accept": "application/json",
        "Content-Type": "application/json",
        "Authorization": "Bearer " + API_TOKEN,
    }
    r = requests.get(url=API_ENDPOINT, headers=headers)
    log.info("File:")
    pprint(r.json())


log = logging.getLogger(__name__)

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    log = tf.get_logger()

    # print(get_token())

    send_config(CONF_FNAME)
    # check_file()

    log.info("Correct, visit https://hp.kerga.fr")
