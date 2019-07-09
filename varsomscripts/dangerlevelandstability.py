# -*- coding: utf-8 -*-
"""Request to get data used in the paper with Frank Techel"""

from varsomdata import getdangers as gd
from varsomdata import getobservations as go
from varsomscripts import avalancheactivity as aa
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
    start = dt.datetime.now()

    obs_dangers = gd.get_observed_dangers(region_ids, from_date, to_date, lang_key=1, output='List')

    stop1 = dt.datetime.now()
    print(stop1 - start)
    _df = pd.DataFrame(
        columns=['danger_level', 'danger_level_name', 'date', 'forecast_correct', 'forecast_correct_id', 'region_name',
                 'region_regobs_id', 'nick', 'regid'])
    for ad in obs_dangers:
        _df = _df.append({'danger_level': ad.danger_level,
                        'danger_level_name': ad.danger_level_name,
                        'date': ad.date,
                        'forecast_correct': ad.forecast_correct,
                        'forecast_correct_id': ad.forecast_correct_id,
                        'region_name': ad.region_name,
                        'region_regobs_id': ad.region_regobs_id,
                        'nick': ad.nick,
                        'regid': ad.regid}, ignore_index=True)
    stop2 = dt.datetime.now()
    print(stop2 - stop1)
    print(stop2 - start)

    _df.to_csv('../localstorage/obs_dangers.csv', sep=';', index_label='index')


def get_elevation(_id):
    # utility function used in "add_metadata"
    _obs = go.get_data(reg_ids=_id)
    return _obs[0]['ObsLocation']['Height']


def add_metadata():
    _df = pd.read_csv(r'../localstorage/ect_loc_dl_norway.csv', sep=';', index_col=0)

    _df['Elevation'] = _df.apply(lambda row: get_elevation(row['RegID']), axis=1)

    _df.to_csv(r'../localstorage/ect_elev_norway.csv', sep=';', index_label='index')


def observed_avalanches():
    from_date = dt.date(2014, 12, 1)
    to_date = dt.date(2019, 5, 31)

    # region_ids = [3014, 3028]
    region_ids = [3003, 3007, 3009, 3010, 3011, 3012, 3013, 3014, 3015, 3016, 3017, 3022, 3023, 3024, 3027, 3028, 3029,
                  3031, 3032, 3034, 3035]
    start = dt.datetime.now()
    avals = go.get_avalanche(from_date, to_date, region_ids, lang_key=2)
    stop1 = dt.datetime.now()
    print(stop1 - start)
    _df = pd.DataFrame(
        columns=['aval_type', 'trigger', 'DestructiveSizeName', 'date', 'elevation', 'TerrainStartZoneName', 'Latitude', 'Longitude', 'ForecastRegionName',
                 'ForecastRegionTID', 'nick', 'RegID'])
    for av in avals:
        _df = _df.append({'aval_type': av.AvalancheName,
                          'trigger': av.AvalancheTriggerName,
                          'DestructiveSizeName': av.DestructiveSizeName,
                          'date': av.DtObsTime.strftime('%Y-%m-%d'),
                          'elevation': av.Height,
                          'TerrainStartZoneName': av.TerrainStartZoneName,
                          'Latitude': av.Latitude,
                          'Longitude': av.Longitude,
                          'ForecastRegionName': av.ForecastRegionName,
                          'ForecastRegionTID': av.ForecastRegionTID,
                          'nick': av.NickName,
                          'RegID': av.RegID}, ignore_index=True)
    stop2 = dt.datetime.now()
    print(stop2 - stop1)
    print(stop2 - start)

    _df.to_csv('../localstorage/obs_avalanches.csv', sep=';', index_label='index')


def observed_avalanche_activity():
    from_date = dt.date(2014, 12, 1)
    to_date = dt.date(2019, 5, 31)

    # region_ids = [3014, 3028]
    region_ids = [3003, 3007, 3009, 3010, 3011, 3012, 3013, 3014, 3015, 3016, 3017, 3022, 3023, 3024, 3027, 3028, 3029,
                  3031, 3032, 3034, 3035]
    start = dt.datetime.now()

    aval_act = go.get_avalanche_activity(from_date, to_date, region_ids)
    aval_act2 = go.get_avalanche_activity_2(from_date, to_date, region_ids, lang_key=2)
    a = 0
    # avals = go.get_avalanche(from_date, to_date, region_ids, lang_key=2)
    stop1 = dt.datetime.now()
    print(stop1 - start)
    _df = pd.DataFrame(
        columns=['Release_type', 'Avalanche_type', 'DestructiveSizeName', 'Date', 'Elevation', 'EstimatedNumName', 'EstimatedNumTID', 'Latitude', 'Longitude', 'ForecastRegionName',
                 'ForecastRegionTID', 'Nick', 'RegID'])
    for av in aval_act:
        _df = _df.append({'Release_type': av.AvalancheTriggerName,
                          'Avalanche_type': av.AvalancheName,
                          'DestructiveSizeName': av.DestructiveSizeName,
                          'Date': av.DtObsTime.strftime('%Y-%m-%d'),
                          'Elevation': av.Height,
                          'EstimatedNumName': av.EstimatedNumName,
                          'EstimatedNumTID': av.EstimatedNumTID,
                          'Latitude': av.Latitude,
                          'Longitude': av.Longitude,
                          'ForecastRegionName': av.ForecastRegionName,
                          'ForecastRegionTID': av.ForecastRegionTID,
                          'Nick': av.NickName,
                          'RegID': av.RegID}, ignore_index=True)

    for av in aval_act2:
        _df = _df.append({'Release_type': av.AvalTriggerSimpleName,
                          'Avalanche_type': av.AvalancheExtName,
                          'DestructiveSizeName': av.DestructiveSizeName,
                          'Date': av.DtObsTime.strftime('%Y-%m-%d'),
                          'Elevation': av.Height,
                          'EstimatedNumName': av.EstimatedNumName,
                          'EstimatedNumTID': av.EstimatedNumTID,
                          'Latitude': av.Latitude,
                          'Longitude': av.Longitude,
                          'ForecastRegionName': av.ForecastRegionName,
                          'ForecastRegionTID': av.ForecastRegionTID,
                          'Nick': av.NickName,
                          'RegID': av.RegID}, ignore_index=True)
    stop2 = dt.datetime.now()
    print(stop2 - stop1)
    print(stop2 - start)

    _df.to_csv('../localstorage/obs_aval_activity.csv', sep=';', index_label='index')


if __name__ == "__main__":
    # stest = stability_tests()
    # stest.to_csv('../localstorage/stability_tests.csv', sep=';', index_label='index')
    observed_danger_levels()
    # observed_avalanches()
    # add_metadata()
    # observed_avalanche_activity()

    a = 0
