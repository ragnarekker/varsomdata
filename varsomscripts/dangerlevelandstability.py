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
import pandas as pd


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


def observed_danger_levels():
    from_date = dt.date(2014, 12, 1)
    to_date = dt.date(2019, 5, 31)

    #region_ids = [3014, 3028]
    region_ids = [3003, 3007, 3009, 3010, 3011, 3012, 3013, 3014, 3015, 3016, 3017, 3022, 3023, 3024, 3027, 3028, 3029,
                  3031, 3032, 3034, 3035]

    obs_dangers = gd.get_observed_dangers(region_ids, from_date, to_date, lang_key=1, output='List')

    return obs_dangers

if __name__ == "__main__":
    # stest = stability_tests()
    # stest.to_csv('../localstorage/stability_tests.csv', sep=';', index_label='index')
    start = dt.datetime.now()
    obs_dangers = observed_danger_levels()
    stop1 = dt.datetime.now()
    print(stop1-start)
    df = pd.DataFrame(columns=['danger_level', 'danger_level_name', 'date', 'forecast_correct', 'forecast_correct_id', 'region_name', 'region_regobs_id', 'nick', 'regid'])
    for ad in obs_dangers:
        df = df.append({'danger_level': ad.danger_level,
                        'danger_level_name': ad.danger_level_name,
                        'date': ad.date,
                        'forecast_correct': ad.forecast_correct,
                        'forecast_correct_id': ad.forecast_correct_id,
                        'region_name': ad.region_name,
                        'region_regobs_id': ad.region_regobs_id,
                        'nick': ad.nick,
                        'regid': ad.regid}, ignore_index=True)
    stop2 = dt.datetime.now()
    print(stop2-stop1)
    print(stop2-start)

    df.to_csv('../localstorage/obs_dangers.csv', sep=';', index_label='index')
    a = 0
