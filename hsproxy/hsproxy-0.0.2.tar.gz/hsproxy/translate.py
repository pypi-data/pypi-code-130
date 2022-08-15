#!/usr/bin/env python3

import json

from volcengine.ApiInfo import ApiInfo
from volcengine.Credentials import Credentials
from volcengine.ServiceInfo import ServiceInfo
from volcengine.base.Service import Service
from os import getenv

HS_PK = getenv('HS_PK')
HS_SK = getenv('HS_SK')


def _translate(src, target, txt):
  k_timeout = 5  # second
  k_service_info = \
      ServiceInfo('open.volcengineapi.com',
                  {'Content-Type': 'application/json'},
                  Credentials(HS_PK, HS_SK, 'translate', 'cn-north-1'),
                  k_timeout,
                  k_timeout)
  k_query = {'Action': 'TranslateText', 'Version': '2020-06-01'}
  k_api_info = {'translate': ApiInfo('POST', '/', k_query, {}, {})}
  service = Service(k_service_info, k_api_info)
  body = {
      'TargetLanguage': target,
      'TextList': txt,
  }
  if src:
    body['SourceLanguage'] = src
  res = service.json('translate', {}, json.dumps(body))
  for i in json.loads(res)['TranslationList']:
    yield i['Translation']


def translate(src, target, txt):
  limit = 128
  for i in range(0, len(txt), limit):
    yield from _translate(src, target, txt[i:i + limit])
