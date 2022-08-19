#
#   Copyright EAVISE
#   Author: Tanguy Ophoff
#
#   Test log.deprecated function
#
import brambox as bb
import logging


def test_deprecated_log(caplog):
    """ Deprecation logs should only appear ones. """
    caplog.set_level(logging.DEBUG)

    bb.logger.deprecated('TESTING DEPRECATED LOG')
    assert len(caplog.records) == 1
    assert caplog.records[0].levelname == 'DEPRECATED'
    assert 'TESTING DEPRECATED LOG' in caplog.text

    bb.logger.deprecated('TESTING DEPRECATED LOG')
    assert len(caplog.records) == 1
