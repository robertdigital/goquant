import unittest

from util.date import date_to_milliseconds
from dateutil.parser import parse


class TestDate(unittest.TestCase):
    def test_date_to_milliseconds(self):
        datetime_object = parse("2019-12-21T10:06:00-08:00")
        out_ms = date_to_milliseconds(datetime_object)
        self.assertEqual(out_ms, 1576951560000)
