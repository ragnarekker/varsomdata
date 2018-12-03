# -*- coding: utf-8 -*-
"""Requests all forecasts (danger levels and problems) from the forecast api and writes to .csv file or plot."""

import datetime as dt
import os as os
import pylab as plt
import setenvironment as env
from utilities import fencoding as fe, makelogs as ml, makepickle as mp
from varsomdata import getforecastapi as gf

__author__ = 'kmunve'


def get_warnings_():
    "Get avalanche warnings including problems and weather for analysis"
    pass


if __name__ == '__main__':
    region_ids = [3022]  # Trollheimen

    from_date = dt.date(2017, 12, 1)
    to_date = dt.date(2017, 12, 5)

    warnings_ = gf.get_avalanche_warnings(region_ids, from_date, to_date, lang_key=1)

    df_0 = warnings_[4].to_dict()
