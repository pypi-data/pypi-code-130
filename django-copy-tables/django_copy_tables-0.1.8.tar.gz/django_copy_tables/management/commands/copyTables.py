#!/usr/bin/python
from django.core.management.base import BaseCommand
from django.db import transaction
from django.core import serializers
from django.conf import settings

from importlib import import_module

import requests
import json
import pprint


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
        if settings.DEBUG:
            print('Getting table object for %s - %s' % (kwargs['modName'][0], kwargs['tableName'][0]))

        models = import_module("%s.models" % kwargs['modName'][0])
        t = getattr(models, kwargs['tableName'][0])

        step = 100
        if 'step' in kwargs and kwargs['step'] is not None:
            step = kwargs['step'][0]
            if settings.DEBUG:
                print('Step set to %s' % step)

        reqdata = {'modName': kwargs['modName'][0],
                   'tableName': kwargs['tableName'][0],
                   'copyPass': kwargs['copyPass'][0],
                   'qLimit': step,
                   }

        if kwargs['clear']:
            if settings.DEBUG:
                print('Clear requested, deleting all objects in table.')
            for r in t.objects.all():
                r.delete()

        offset = 0
        while 1:
            if offset:
                offset += step
                reqdata['qOffset'] = offset

            if settings.DEBUG:
                print("Requesting %s records starting at record %s" % (step, offset))
                print("Request Url: %s" % kwargs['srcUrl'][0])
                print("Post request data:")
                pprint.pprint(reqdata)
            res = requests.post(kwargs['srcUrl'][0], data=reqdata)
            if settings.DEBUG:
                print("Request result code: %s" % res.status_code)
                print("Request content:\n%s" % res.content)
            d = res.json()
            if settings.DEBUG:
                print("Request Json result:")
                pprint.pprint(d)
            jdo = json.loads(d['obj'])
            if settings.DEBUG:
                print("Request Json objects:")
                pprint.pprint(jdo)
            cnt = 0
            if 'ignore' in kwargs and kwargs['ignore'] is not None:
                if settings.DEBUG:
                    print("Removing ignored fields")
                for r in jdo:
                    for ifield in kwargs['ignore']:
                        del r['fields'][ifield]
            if settings.DEBUG:
                print("Loading Json objects:")
                pprint.pprint(jdo)
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
        if settings.DEBUG:
            print("Success")
