# -*- coding: utf-8 -*-
__author__ = 'raek'


import requests
import datetime
import getdangers as gd


def get_warnings_as_json(region_id, start_date, end_date, lang_key=1):
    """
    Selects warnings and returns the json structured result as given on the api.

    :param region_id:   [int]       RegionID as given in the forecast api [1-99] or in regObs [101-199]
    :param start_date:  [string]    date as yyyy-mm-dd
    :param end_date:    [string]    date as yyyy-mm-dd

    :return warnings:   [string]    String as json

    Eg. http://api01.nve.no/hydrology/forecast/avalanche/v2.0.2/api/AvalancheWarningByRegion/Detail/10/1/2013-01-10/2013-01-20
    """

    if region_id > 100:
        region_id = region_id - 100

    print"getForecastApi -> get_warnings_as_json: Getting AvalancheWarnings for {0} from {1} til {2}"\
        .format(region_id, start_date, end_date)

    url = "http://api01.nve.no/hydrology/forecast/avalanche/v2.0.2/api/AvalancheWarningByRegion/Detail/{0}/{3}/{1}/{2}"\
        .format(region_id, start_date, end_date, lang_key)

    # If at first you don't succeed, try and try again.
    try:
        warnings = requests.get(url).json()
        print(".. {} warnings found.".format(len(warnings)))
        return warnings
    except:
        print("!!Exception occurred!!")
        warnings = get_warnings_as_json(region_id, start_date, end_date, lang_key)
        return warnings


def get_warnings(region_id, start_date, end_date, lang_key=1):
    """Selects warnings and returns a list of AvalancheDanger Objects. This method does NOT add the
    avalanche problems to the warning.

    :param region_id:   [int]       RegionID as given in the forecast api [1-99] or in regObs [101-199]
    :param start_date:  [string]    date as yyyy-mm-dd
    :param end_date:    [string]    date as yyyy-mm-dd

    :return avalanche_danger_list: List of AvalancheDanger objects
    """

    warnings = get_warnings_as_json(region_id,start_date, end_date, lang_key=lang_key)
    avalanche_danger_list = []

    for w in warnings:
        region_id = int(w['RegionId'])
        region_name = w['RegionName']
        date = datetime.datetime.strptime(w['ValidFrom'][0:10], '%Y-%m-%d').date()
        danger_level = int(w['DangerLevel'])
        danger_level_name = w['DangerLevelName']

        danger = gd.AvalancheDanger(region_id, region_name, 'Forecast API', date, danger_level, danger_level_name)
        danger.set_source('Varsel')

        if lang_key == 1:
            danger.set_main_message_no(w['MainText'])
        if lang_key == 2:
            danger.set_main_message_en(w['MainText'])

        avalanche_danger_list.append(danger)

    return avalanche_danger_list


def get_valid_regids(region_id, start_date, end_date):
    """Method looks up all forecasts for a region and selects and returns the RegIDs used in regObs. Thus, the list of
    RegIDs are for published forecasts.

    :param region_id:   [int]       RegionID as given in the forecast api [1-99] or in regObs [101-199]
    :param start_date:  [string]    date as yyyy-mm-dd
    :param end_date:    [string]    date as yyyy-mm-dd
    :return:
    """

    warnings = get_warnings_as_json(region_id, start_date, end_date)
    valid_regids = {}

    for w in warnings:
        danger_level = int(w["DangerLevel"])
        if danger_level > 0:
            valid_regids[w["RegId"]] = w["ValidFrom"]

    return valid_regids


if __name__ == "__main__":

    # get data for Bardu (112) and Tamokdalen (129)
    warnings_for_129 = get_warnings(129, "2014-12-01", "2015-06-01")
    # p = get_valid_regids(10, "2013-03-01", "2013-03-09")

    a = 1