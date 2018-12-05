# -*- coding: utf-8 -*-
"""Requests all forecasts (danger levels and problems) from the forecast api and writes to .csv file or plot."""

import datetime as dt
from varsomdata import getforecastapi as gf
import pandas

__author__ = 'kmunve'


def test_AvalancheDanger_to_dict():
    region_ids = [3022]  # Trollheimen

    from_date = dt.date(2018, 12, 1)
    to_date = dt.date(2018, 12, 5)

    warnings_ = gf.get_avalanche_warnings(region_ids, from_date, to_date, lang_key=1)

    _d = warnings_[2].to_dict()

    df = pandas.DataFrame.from_dict(_d)

    k = 'm'


def test_MountainWeather_class():
    """
    Requires "forecast_api_version" : "v4.0.1" in /config/api.json
    """
    region_ids = [3022]  # Trollheimen

    from_date = dt.date(2018, 12, 1)
    to_date = dt.date(2018, 12, 4)

    warnings_as_json = gf.get_avalanche_warnings_as_json(region_ids, from_date, to_date, lang_key=1)
    warnings_ = gf.get_avalanche_warnings(region_ids, from_date, to_date, lang_key=1)

    w = warnings_as_json[2]
    mw = w['MountainWeather']

    for _mt in mw['MeasurementTypes']:
        if _mt['Id'] == 10: # precipitation
            for _st in _mt['MeasurementSubTypes']:
                if _st['Id'] == 60: # most exposed
                    precip_most_exposed = float(_st['Value'])
                elif _st['Id'] == 70: # regional average
                    precip_region = float(_st['Value'])

        elif _mt['Id'] == 20: # wind
            for _st in _mt['MeasurementSubTypes']:
                if _st['Id'] == 20: # wind_speed
                    wind_speed = _st['Value']
                elif _st['Id'] == 50: # wind_direction
                    wind_direction = _st['Value']

        elif _mt['Id'] == 30: # changing wind
            for _st in _mt['MeasurementSubTypes']:
                if _st['Id'] == 20: # wind_speed
                    change_wind_speed = _st['Value']
                elif _st['Id'] == 50: # wind_direction
                    change_wind_direction = _st['Value']
                elif _st['Id'] == 100:  # hour_of_day_start
                    change_hour_of_day_start = int(_st['Value'])
                elif _st['Id'] == 110: # hour_of_day_stop
                    change_hour_of_day_stop = int(_st['Value'])

        elif _mt['Id'] == 40: # temperature
            for _st in _mt['MeasurementSubTypes']:
                if _st['Id'] == 30: # temperature_min
                    temperature_min = float(_st['Value'])
                elif _st['Id'] == 70: # temperature_max
                    temperature_max = float(_st['Value'])
                elif _st['Id'] == 90: # temperature_elevation
                    temperature_elevation = float(_st['Value'])

        elif _mt['Id'] == 50: # freezing level
            for _st in _mt['MeasurementSubTypes']:
                if _st['Id'] == 90: # wind_speed
                    freezing_level = float(_st['Value'])
                elif _st['Id'] == 100:  # hour_of_day_start
                    fl_hour_of_day_start = int(_st['Value'])
                elif _st['Id'] == 110: # hour_of_day_stop
                    fl_hour_of_day_stop = int(_st['Value'])

    k = 'm'

if __name__ == '__main__':
    test_MountainWeather_class()
    #test_AvalancheDanger_to_dict()
