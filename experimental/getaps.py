# -*- coding: utf-8 -*-
__author__ = 'raek'


import requests as rq
import datetime as dt

region_id = 3027
from_date = '2016-11-01'
to_date = '2017-01-01'

url = 'http://tst-h-int-api01/APSServices/SeasonHistoryReader.svc/GetSeasonalHistory/{0}/{1}/{2}'.format(region_id, from_date, to_date)
# eg: http://tst-h-int-api01/APSServices/SeasonHistoryReader.svc/GetSeasonalHistory/3027.0/2016-11-01/2017-01-01

aps_data_region = rq.get(url).json()

first_date = aps_data_region['FirstDate'][6:-7]
first_date_unix = int(first_date)
first_date_unix_in_seconds = first_date_unix / 1000  # For some reason they are given in miliseconds
firs_time_date = dt.datetime.fromtimestamp(int(first_date_unix_in_seconds))

a = 1