import datetime
import unittest

from flowable.external_worker_client.utils import parse_date_time


class TestUtils(unittest.TestCase):

    def test_parse_date_time_with_millis(self):
        date = parse_date_time('2024-09-23T15:23:08.123Z')
        self.assertEqual(datetime.datetime(2024, 9, 23, 15, 23, 8, 123000), date)

    def test_parse_date_time_without_millis(self):
        date = parse_date_time('2024-09-23T15:23:08Z')
        self.assertEqual(datetime.datetime(2024, 9, 23, 15, 23, 8, 0), date)
