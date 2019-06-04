# -*- coding: utf-8 -*-
"""Contains methods for retrieving large data sets and adding them to local storage. If locally stored
data exists and files are newer that a given max datetime limit, these files are used to return data.
Else, new requests are made."""

import setenvironment as env
from varsomdata import getobservations as go
from varsomdata import getmisc as gm
from varsomdata import getforecastapi as gfa
from utilities import makepickle as mp
import logging as lg
import datetime as dt
import os as os

__author__ = 'raek'


def _observation_is_not_empty(o):
    """Test if an observation form is empty. Might occur when making list of nests and only pictures are given.
    Method will need to expand if empty cases occur on other forms."""

    if o.RegistrationTID == 10:
        if o.ObsComment is None and o.ObsHeader is None and o.Comment is None and len(o.URLs) == 0:
            return False

    return True


def get_all_observations(year, output='List', geohazard_tids=None, lang_key=1, max_file_age=23):
    """Specialized method for getting all observations for one season (1. sept to 31. august).
    For the current season (at the time of writing, 2018-19), if request has been made the last 23hrs,
    data is retrieved from a locally stored pickle, if not, new request is made to the regObs api. Previous
    seasons are not requested if a pickle is found in local storage.

    :param year:                [string] Eg. season '2017-18' (sept-sept) or one single year '2018'
    :param output:              [string] 'List' or 'FlatList'
    :param geohazard_tids:      [int or list of ints] Default None gives all. Note, pickle stores all,
                                but this option returns a select
    :param lang_key             [int] 1 is norwegian, 2 is english
    :param max_file_age:        [int] hrs how old the file is before new is retrieved

    :return:
    """

    from_date, to_date = gm.get_dates_from_season(year=year)
    file_name_list = '{0}all_observations_list_{1}_lk{2}.pickle'.format(env.local_storage, year, lang_key)
    file_name_flat = '{0}all_observations_flat_{1}_lk{2}.pickle'.format(env.local_storage, year, lang_key)
    get_new = True
    file_date_limit = dt.datetime.now() - dt.timedelta(hours=max_file_age)

    # if we are well out of the current season (30 days) its little chance the data set has changed.
    current_season = gm.get_season_from_date(dt.date.today() - dt.timedelta(30))

    if geohazard_tids:
        if not isinstance(geohazard_tids, list):
            geohazard_tids = [geohazard_tids]

    if os.path.exists(file_name_list):
        # if file contains a season long gone, dont make new.
        if year == current_season:
            file_age = dt.datetime.fromtimestamp(os.path.getmtime(file_name_list))
            # If file is newer than the given time limit, dont make new.
            if file_age > file_date_limit:
                # If file size larger than that of an nearly empty file, dont make new.
                if os.path.getsize(file_name_list) > 100:   # 100 bytes limit
                    get_new = False
        else:
            get_new = False

    if get_new:
        # When get new, get all geo hazards
        listed_observations = go.get_all_observations(from_date=from_date, to_date=to_date,
                                                      output='List', geohazard_tids=None, lang_key=lang_key)
        mp.pickle_anything(listed_observations, file_name_list)

        flat_listed_observations = [o for lo in listed_observations for o in lo.Observations]
        mp.pickle_anything(flat_listed_observations, file_name_flat)

    if output == 'List':
        all_listed_observations = mp.unpickle_anything(file_name_list)
        listed_observations = []

        if geohazard_tids:
            for o in all_listed_observations:
                if o.GeoHazardTID in geohazard_tids:
                    listed_observations.append(o)

        else:
            listed_observations = all_listed_observations

        return listed_observations

    elif output == 'FlatList':
        all_flat_listed_observations = mp.unpickle_anything(file_name_list)
        flat_listed_observations = []

        if geohazard_tids:
            for o in all_flat_listed_observations:
                if o.GeoHazardTID in geohazard_tids:
                    flat_listed_observations.append(o)

        else:
            flat_listed_observations = all_flat_listed_observations

        return flat_listed_observations

    else:
        lg.warning("getvarsompickles.py -> get_all_observations: Unknown output option.")
        return []


def get_all_forecasts(year, lang_key=1, max_file_age=23):
    """Specialized method for getting all forecasts for one season.
    For the current season (at the time of writing, 2018-19), if a request
    has been made the last 23hrs, data is retrieved from a locally stored pickle,
    if not, new request is made to the regObs api. Previous seasons are not
    requested if a pickle is found in local storage.

    :param year:                [string] Eg. season '2017-18'
    :param lang_key             [int] 1 is norwegian, 2 is english
    :param max_file_age:        [int] hrs how old the file is before new is retrieved

    :return valid_forecasts:    [list of AvalancheWarning]
    """

    from_date, to_date = gm.get_forecast_dates(year=year)
    file_name = '{0}all_forecasts_{1}_lk{2}.pickle'.format(env.local_storage, year, lang_key)
    file_date_limit = dt.datetime.now() - dt.timedelta(hours=max_file_age)

    # if we are well out of the current season (30 days) its little chance the data set has changed.
    current_season = gm.get_season_from_date(dt.date.today() - dt.timedelta(30))

    # Get forecast regions used in the current year
    region_ids = gm.get_forecast_regions(year, get_b_regions=True)

    get_new = True

    if os.path.exists(file_name):
        # if file contains a season long gone, dont make new.
        if year == current_season:
            file_age = dt.datetime.fromtimestamp(os.path.getmtime(file_name))
            # If file is newer than the given time limit, dont make new.
            if file_age > file_date_limit:
                # If file size larger than that of an nearly empty file, dont make new.
                if os.path.getsize(file_name) > 100:   # 100 bytes limit
                    get_new = False
        else:
            get_new = False

    if get_new:
        lg.info("getvarsompickles.py -> get_all_forecasts: Get new {0} forecasts and pickle.".format(year))

        all_forecasts = gfa.get_avalanche_warnings(region_ids, from_date, to_date, lang_key=lang_key)

        # Valid forecasts have a danger level. The other are empty.
        valid_forecasts = []
        for f in all_forecasts:
            if f.danger_level > 0:
                valid_forecasts.append(f)

        mp.pickle_anything(valid_forecasts, file_name)

    else:
        lg.info("getvarsompickles.py -> get_all_forecasts: Unpickle {0} forecasts.".format(year))

        valid_forecasts = mp.unpickle_anything(file_name)

    return valid_forecasts


if __name__ == "__main__":

    # all_regs = get_all_observations('2017-18', output='List')
    # all_regs = get_all_observations('2016-17', output='List')
    # all_regs = get_all_observations('2015-16', output='List')

    all_forecasts_1819 = get_all_forecasts('2018-19')
    # all_forecasts_1718 = get_all_forecasts('2017-18')
    # all_forecasts_1617 = get_all_forecasts('2016-17')
    # all_forecasts_1516 = get_all_forecasts('2015-16')

    pass

