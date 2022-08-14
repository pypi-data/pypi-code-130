import datetime
import unittest
import json

from . import print_test_ok, session_creds, token_session, pw_session


class TestPlaceholder(unittest.TestCase):

    # def test_valid_after_dates_against_a_start_date(self):
    #     for i in [
    #         ['2011-08-04', '2011-08-03'],
    #         [datetime.datetime.now().isoformat(), '2011-08-03'],
    #     ]:
    #         self.assertTrue(is_after(*i))
    #     print_test_ok()
    #
    # def test_invalid_after_dates_against_a_start_date(self):
    #     for i in [
    #         ['2011-07-02', '2011-08-03'],
    #         ['2011-08-03', '2011-08-03'],
    #         [datetime.datetime.utcfromtimestamp(0).isoformat(), '2011-08-03'],
    #         ['foo', '2011-08-03'],
    #     ]:
    #         self.assertFalse(is_after(*i))
    #     print_test_ok()

    def test_sample(self):
        # results = cli.session.actions.list_streams(search_text="met", verify_stream_states=True)

        # print(json.dumps(results, indent=2))
        # print(json.dumps(results))

        print(session_creds)

        print("Token auth test")
        _ = token_session.api.cases_get_prefix()

        print("Password auth test")
        _ = pw_session.api.cases_get_prefix()

        print_test_ok()
