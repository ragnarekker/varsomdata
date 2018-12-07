# -*- coding: utf-8 -*-
"""Requests all forecasts (danger levels and problems) from the forecast api and writes to .csv file or plot."""

import datetime as dt
from varsomdata import getforecastapi as gf
from varsomdata import varsomclasses as vc
import pandas

__author__ = 'kmunve'


def test_AvalancheDanger_to_dict():
    region_ids = [3022]  # Trollheimen

    from_date = dt.date(2018, 12, 1)
    to_date = dt.date(2018, 12, 5)

    warnings_ = gf.get_avalanche_warnings(region_ids, from_date, to_date, lang_key=1)

    _d = warnings_[0].to_dict()

    k = 'm'


def test_AvalancheDanger_as_df():
    """
    Put class data into a pandas.DataFrame
    :return:
    """
    region_ids = [3022]  # Trollheimen

    from_date = dt.date(2018, 12, 1)
    to_date = dt.date(2018, 12, 6)

    warnings_ = gf.get_avalanche_warnings(region_ids, from_date, to_date, lang_key=1, as_dict=True)

    df = pandas.DataFrame.from_dict(warnings_)
    df.to_csv(r'../localstorage/aval_danger.csv', header=True)

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

    w = warnings_as_json[0]
    mw = gf.MountainWeather()
    mw.from_dict(w['MountainWeather'])

    k = 'm'

def test_AvalancheWarning_class():
    """
        Requires "forecast_api_version" : "v4.0.1" in /config/api.json
        """
    region_ids = [3003]

    from_date = dt.date(2018, 12, 3)
    to_date = dt.date(2018, 12, 7)

    warnings_as_json = gf.get_avalanche_warnings_as_json(region_ids, from_date, to_date, lang_key=1)

    warnings_ = []
    for w in warnings_as_json:
        _aw = gf.AvalancheWarning()
        _aw.from_dict(w)
        warnings_.append(_aw)

    print(warnings_[0])

    k = 'm'


if __name__ == '__main__':
    #test_MountainWeather_class()
    test_AvalancheWarning_class()
    #test_AvalancheDanger_to_dict()
    #test_AvalancheDanger_as_df()
