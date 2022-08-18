#!/usr/bin/python
from django.core.management.base import BaseCommand
from django.db import transaction
from django.core import serializers

from importlib import import_module

import requests
import json


class Command(BaseCommand):
    def add_arguments(self, parser):
        parser.add_argument('modName', nargs="+", type=str)
        parser.add_argument('tableName', nargs="+", type=str)
        parser.add_argument('srcUrl', nargs="+", type=str)
        parser.add_argument('copyPass', nargs="+", type=str)

        parser.add_argument('--clear', action="store_true",
                            help="Clear the table before importing new data")
        parser.add_argument('--ignore', action="append",
                            help="Ignore (clear) field in table")
        parser.add_argument('--step', help="# of items to get per request")

    @transaction.atomic
    def handle(self, *args, **kwargs):
        models = import_module("%s.models" % kwargs['modName'][0])
        t = getattr(models, kwargs['tableName'][0])

        step = 100
        if 'step' in kwargs and kwargs['step'] is not None:
            step = kwargs['step'][0]

        reqdata = {'modName': kwargs['modName'][0],
                   'tableName': kwargs['tableName'][0],
                   'copyPass': kwargs['copyPass'][0],
                   'qLimit': step,
                   }

        if kwargs['clear']:
            for r in t.objects.all():
                r.delete()

        offset = 0
        while 1:
            if offset:
                offset += step
                reqdata['qOffset'] = offset
            d = requests.post(kwargs['srcUrl'][0], data=reqdata).json()
            cnt = 0
            jdo = json.loads(d['obj'])
            if 'ignore' in kwargs and kwargs['ignore'] is not None:
                for r in jdo:
                    for ifield in kwargs['ignore']:
                        del r['fields'][ifield]
            js = json.dumps(jdo)
            dsd = serializers.deserialize("json", js)
            for r in dsd:
                r.save()
                cnt += 1
            print("loaded %i records" % cnt)
            if cnt < int(step):
                break
            if cnt > int(step):
                raise Exception("Too many records sent, is server out of date?")
