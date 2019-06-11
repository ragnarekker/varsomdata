# -*- coding: utf-8 -*-
"""Request to get data used in the paper with Frank Techel"""

from varsomdata import getdangers as gd
from varsomdata import getobservations as go
from utilities import makepickle as mp
from varsomdata import getmisc as gm
from utilities import fencoding as fe
from utilities import makemisc as mm
import setenvironment as env
import datetime as dt


__author__ = 'kmu'


def stability_tests():
    #region_ids = [3012, 3016, 3028, 3034]
    from_date = dt.date(2014, 12, 1)
    to_date = dt.date(2019, 5, 31)
    region_ids = [3003, 3007, 3009, 3010, 3011, 3012, 3013, 3014, 3015, 3016, 3017, 3022, 3023, 3024, 3027, 3028, 3029,
                  3031, 3032, 3034, 3035]
    stest = go.get_tests(from_date, to_date, region_ids=region_ids, location_id=None, countries=None, time_zone=None,
              group_id=None, observer_ids=None, observer_nick=None, observer_competence=None,
              output='DataFrame', lang_key=1)

    return stest


if __name__ == "__main__":
    stest = stability_tests()
    stest.to_csv('../localstorage/stability_tests.csv', sep=';', index_label='index')

    a = 0
