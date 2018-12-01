# -*- coding: utf-8 -*-
__author__ = 'raek'

from varsomdata import getforecastapi as gfa
from varsomdata import getkdvelements as gkdv
from datetime import date as date

if __name__ == '__main__':

    """Lists how many times different forecasters hva made a forecast for a given reigon."""

    # Get all regions
    # regions = gkdv.get_kdv('ForecastRegionKDV')

    # Get forecasts
    nordenskiold_warnings_201516 = gfa.get_avalanche_warnings(130, '2016-01-27', '2016-07-01')
    nordenskiold_warnings_201617 = gfa.get_avalanche_warnings(3003, '2016-12-02', date.today())
    nordenskiold_warnings = nordenskiold_warnings_201516 + nordenskiold_warnings_201617

    # Count occurences
    dict_of_forecasters = {}
    for w in nordenskiold_warnings:
        forecaster = w.nick
        if w.danger_level > 0:
            if forecaster in dict_of_forecasters.keys():
                dict_of_forecasters[forecaster] += 1
            else:
                dict_of_forecasters[forecaster] = 1

    a = 1