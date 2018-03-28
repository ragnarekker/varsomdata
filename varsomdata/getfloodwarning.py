# -*- coding: utf-8 -*-
import datetime as dt
import requests as rq
import json as json

__author__ = 'ragnarekker'


def get_flood_warning_by_county(county_no, lang_key, from_date, to_date):
    """

    :return:

    https://api01.nve.no/hydrology/forecast/flood/v1.0.5/api/Warning/County/18/1/2017-12-01/2018-01-10
    """

    url = 'https://api01.nve.no/hydrology/forecast/flood/v1.0.5/api/Warning/County/{0}/{1}/{2}/{3}'.format(county_no, lang_key, from_date, to_date)

    responds = rq.get(url)
    data = json.loads(responds.text)

    a = 1

if __name__ == '__main__':

    get_flood_warning_by_county(18, 1, '2018-01-01', '2018-01-10')