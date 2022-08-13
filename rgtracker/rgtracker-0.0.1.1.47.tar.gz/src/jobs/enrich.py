from rgtracker.common import *
from rgtracker.record import *
from rgtracker.tracker import *
from rgtracker.website import *
from rgtracker.section import *
from rgtracker.page import *
from rgtracker.device import *
from redisgears import executeCommand as execute
import json
import sys
import requests
import datetime


def enrich_page(record):
    key = record['value']['key']
    article_id = record['value']['article_id']
    api_url = f"http://rtl-curator.back.k8s.rtl/items/urn:newstool:article:{article_id}"
    try:
        response = requests.get(api_url)
        response.raise_for_status()
        response_json = response.json()
        element = datetime.datetime.strptime(response_json.get('display_date'), "%Y-%m-%dT%H:%M:%S%z")
        timestamp = round(datetime.datetime.timestamp(element) * 1000)
        result = {
            'kicker': response_json.get('kicker'),
            'title': response_json.get('title'),
            'display_date': timestamp
        }
        execute('JSON.SET', key, '$.metadata', json.dumps(result))
        tracker_log(f'{key} - {result} - OK', prefix='Enrich - ')
    except requests.exceptions.RequestException as e:
        tracker_log(f'{e} for {key}', prefix='Enrich - ')
        pass


desc_json = {
    "name": 'Enrich',
    "version": '99.99.99',
    "desc": f"Enrich Website, Section and Page"
}
# unregister_old_versions(desc_json.get('name'), desc_json.get('version'))
GB("StreamReader", desc=json.dumps(desc_json)). \
    foreach(enrich_page). \
    register(
    prefix='ST:ENRICH:P:::',
    convertToStr=True,
    collect=True,
    onFailedPolicy='abort',
    onFailedRetryInterval=1,
    batch=1,
    duration=0,
    trimStream=False)

# run('ST:ENRICH:P:::', trimStream=False)
# register(
# prefix='ST:ENRICH:P:::',
# convertToStr=True,
# collect=True,
# onFailedPolicy='abort',
# onFailedRetryInterval=1,
# batch=1,
# duration=0,
# trimStream=False)