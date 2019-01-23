# -*- coding: utf-8 -*-
"""
Script to retrieve regobs data relevant for forecast analysis at NVE.
"""
__author__ = 'kmu'

import datetime as dt
from varsomdata import getobservations as go


def get_snow_obs(from_date, to_date):
    all_data_snow = go.get_data_as_class(from_date, to_date, geohazard_tids=10)
    return all_data_snow


def get_weak_layers_from_snow_profiles(from_date, to_date):
    snow_profiles = go.get_snow_profile('2018-12-13', '2018-12-26')


def get_danger_signs(from_date, to_date, region_ids):
    ds_list = go.get_danger_sign(from_date, to_date, region_ids=None, location_id=None, group_id=None,
                    observer_ids=None, observer_nick=None, observer_competence=None, output='List', geohazard_tids=10,
                    lang_key=1)
    df = go._make_data_frame(ds_list)

    return df


if __name__ == "__main__":
    region_ids = [3003, 3007, 3009, 3010, 3011, 3012, 3013, 3014, 3015, 3016, 3017, 3022, 3023, 3024, 3027, 3028, 3029,
                  3031, 3032, 3034, 3035]
    from_date = dt.date(2018, 2, 1)
    to_date = dt.date(2018, 2, 15)

    #all_data_snow = get_snow_obs(from_date, to_date)
    ds = get_danger_signs(from_date, to_date, region_ids)

    pass


    #aw_dict = gf.get_avalanche_warnings_2(region_ids, from_date, to_date, lang_key=1, as_dict=True)
    #df = pandas.DataFrame(aw_dict)
    #df.to_csv('../localstorage/norwegian_avalanche_warnings_season_17_18.csv', index_label='index')
