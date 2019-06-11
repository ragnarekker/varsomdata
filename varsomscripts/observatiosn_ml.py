# -*- coding: utf-8 -*-
"""
Script to retrieve regobs data relevant for forecast analysis at NVE.
"""
__author__ = 'kmu'

import datetime as dt
import pandas as pd
from varsomdata import getobservations as go


def get_snow_obs(from_date, to_date):
    all_data_snow = go.get_all_observations(from_date, to_date, geohazard_tids=10)
    return all_data_snow


def get_weak_layers_from_snow_profiles(from_date, to_date):
    snow_profiles = go.get_snow_profile('2018-12-13', '2018-12-26')


def get_danger_signs(from_date, to_date, region_ids):
    ds_list = go.get_danger_sign(from_date, to_date, region_ids=None, location_id=None, group_id=None,
                    observer_ids=None, observer_nick=None, observer_competence=None, output='List', geohazard_tids=10,
                    lang_key=1)
    df = go._make_data_frame(ds_list)

    return df


def get_incident(from_date, to_date, region_ids=None, location_id=None, group_id=None, observer_ids=None, observer_nick=None, observer_competence=None, output='List', geohazard_tids=None, lang_key=1):
    inc_list = go.get_incident(from_date, to_date, region_ids=None, location_id=None, group_id=None, observer_ids=None, observer_nick=None, observer_competence=None, output='List', geohazard_tids=10, lang_key=1)
    inc_list = [i.to_dict() for i in inc_list]
    df = pd.DataFrame(inc_list)

    return df

def get_stability_tests_for_article(from_date, to_date, region_ids):
    st_list = go.get_column_test(from_date, to_date, region_ids)
    _st = []
    for st in st_list:
        _st.append(st.OriginalData)
    return _st


if __name__ == "__main__":
    region_ids = [3003, 3007, 3009, 3010, 3011, 3012, 3013, 3014, 3015, 3016, 3017, 3022, 3023, 3024, 3027, 3028, 3029,
                  3031, 3032, 3034, 3035]
    from_date = dt.date(2018, 12, 1)
    to_date = dt.date(2019, 1, 31)

    #all_data_snow = get_snow_obs(from_date, to_date)
    #ds = get_danger_signs(from_date, to_date, region_ids)
    #inc = get_incident(from_date, to_date, region_ids=region_ids)
    #inc.to_csv('../localstorage/aval_incidents_2013_2019.csv', index_label='index')
    st_list = get_stability_tests_for_article(from_date, to_date, region_ids)
    df = pd.DataFrame(st_list)
    df.to_csv('../localstorage/stability_tests.csv', index_label='index')
    k = 'm'


    #aw_dict = gf.get_avalanche_warnings(region_ids, from_date, to_date, lang_key=1, as_dict=True)
    #df = pandas.DataFrame(aw_dict)
    #df.to_csv('../localstorage/norwegian_avalanche_warnings_season_17_18.csv', index_label='index')
