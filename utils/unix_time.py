import datetime
import time


def now_unix_time():
    return int(time.time())


def get_datetime(unix_time: int):
    return datetime.datetime.fromtimestamp(unix_time)
