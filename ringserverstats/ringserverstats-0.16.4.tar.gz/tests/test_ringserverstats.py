import pytest
import os
from ringserverstats.ringserverstats import *

FIXTURE_DIR = os.path.join(
    os.path.dirname(os.path.realpath(__file__)),
    'test_files',
    )

@pytest.mark.datafiles(os.path.join(FIXTURE_DIR, 'txlog.log'))
def test_parse_ringserver_log(datafiles):
    path = str(datafiles)
    events = parse_ringserver_log(os.path.join(path, 'txlog.log'))
    for k in ['time','geohash','ip','bytes','agent']:
        for e in events:
            assert k in e

@pytest.mark.datafiles(os.path.join(FIXTURE_DIR, 'badtx.log'))
def test_parse_ringserver_badlog(datafiles):
    path = str(datafiles)
    events = parse_ringserver_log(os.path.join(path, 'badtx.log'))
    for k in ['time','geohash','ip','bytes','agent']:
        for e in events:
            assert k in e

@pytest.mark.datafiles(os.path.join(FIXTURE_DIR, 'badevent.log'))
def test_parse_ringserver_badlog(datafiles):
    path = str(datafiles)
    events = parse_ringserver_log(os.path.join(path, 'badevent.log'))
    for k in ['time','geohash','ip','bytes','agent']:
        for e in events:
            assert k in e
