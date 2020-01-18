from datetime import datetime, timedelta
import pytz
import time
from entity.constants import *


def interval_to_milliseconds(interval):
    """Convert a Binance interval string to milliseconds
    :param interval: Binance interval string 1m, 3m, 5m, 15m, 30m, 1h, 2h, 4h, 6h, 8h, 12h, 1d, 3d, 1w
    :type interval: str
    :return:
         None if unit not one of m, h, d or w
         None if string not in correct format
         int value of interval in milliseconds
    """
    ms = None
    seconds_per_unit = {
        "m": 60,
        "h": 60 * 60,
        "d": 24 * 60 * 60,
        "w": 7 * 24 * 60 * 60
    }

    unit = interval[-1]
    if unit in seconds_per_unit:
        try:
            ms = int(interval[:-1]) * seconds_per_unit[unit] * 1000
        except ValueError:
            pass
    return ms


def date_to_milliseconds(d):
    # get epoch value in UTC
    epoch = datetime.utcfromtimestamp(0).replace(tzinfo=pytz.utc)

    # if the date is not timezone aware apply UTC timezone
    if d.tzinfo is None or d.tzinfo.utcoffset(d) is None:
        d = d.replace(tzinfo=pytz.utc)

    # return the difference in time
    return int((d - epoch).total_seconds() * 1000.0)


def datestr_to_datetime(date_str, str_fmt):
    try:
        return datetime.strptime(date_str, str_fmt)
    except ValueError:
        raise ValueError("Incorrect data format, should be {}".format(str_fmt))


def get_datetime_list_between(start_datetime, end_datetime, freq):
    if freq == FREQ_MINUTE:
        cur_datetime = datetime(year=start_datetime.year,
                                month=start_datetime.month,
                                day=start_datetime.day,
                                hour=start_datetime.hour,
                                minute=start_datetime.minute,
                                second=0,
                                tzinfo=pytz.utc)
        time_delta = timedelta(minutes=1)
    elif freq == FREQ_DAY:
        cur_datetime = datetime(year=start_datetime.year,
                                month=start_datetime.month,
                                day=start_datetime.day,
                                hour=0,
                                minute=0,
                                second=0,
                                tzinfo=pytz.utc
                                )
        time_delta = timedelta(days=1)
    else:
        raise ValueError("unsupported freq: {}".format(freq))
    ret = []
    while cur_datetime <= end_datetime:
        ret.append(cur_datetime)
        cur_datetime += time_delta
    return ret
