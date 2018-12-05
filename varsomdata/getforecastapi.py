# -*- coding: utf-8 -*-
"""Contains methods for accessing data on the forecast api's. See api.nve.no for more info"""

import requests
import datetime as dt
from varsomdata import varsomclasses as vc
from utilities import makelogs as ml
import setenvironment as env

__author__ = 'raek'


def get_avalanche_warnings_as_json(region_ids, from_date, to_date, lang_key=1, recursive_count=5):
    """Selects warnings and returns the json structured as given on the api.

    :param region_ids:      [int or list of ints]       RegionID as given in the forecast api [1-99] or in regObs [101-199]
    :param from_date:       [date or string as yyyy-mm-dd]
    :param to_date:         [date or string as yyyy-mm-dd]
    :param lang_key:        [int]                       Language setting. 1 is norwegian and 2 is english.
    :param recursive_count  [int]                       by default attempt the same request # times before giving up

    :return warnings:       [string]                    String as json

    Eg. http://api01.nve.no/hydrology/forecast/avalanche/v2.0.2/api/AvalancheWarningByRegion/Detail/10/1/2013-01-10/2013-01-20
        http://api01.nve.no/hydrology/forecast/avalanche/v2.0.2/api/AvalancheWarningByRegion/Detail/29/1/2015-12-02/2015-12-02
    """

    # If input isn't a list, make it so
    if not isinstance(region_ids, list):
        region_ids = [region_ids]

    warnings = []
    recursive_count_default = recursive_count   # need the default for later

    for region_id in region_ids:

        if len(region_ids) > 1:
            # if we are looping the initial list make sure each item gets the recursive count default
            recursive_count = recursive_count_default

        # In nov 2016 we updated all regions to have ids in th 3000´s. GIS and regObs equal.
        # Before that GIS har numbers 0-99 and regObs 100-199. Messy..
        if region_id > 100 and region_id < 3000:
            region_id = region_id - 100

        url = "http://api01.nve.no/hydrology/forecast/avalanche/{4}/api/AvalancheWarningByRegion/Detail/{0}/{3}/{1}/{2}"\
            .format(region_id, from_date, to_date, lang_key, env.forecast_api_version)

        # If at first you don't succeed, try and try again.
        try:
            warnings_region = requests.get(url).json()
            ml.log_and_print('[info] getforecastapi.py -> get_avalanche_warnings_as_json: {0} warnings found for {1} in {2} to {3}'
                             .format(len(warnings_region), region_id, from_date, to_date))
            warnings += warnings_region

        except:
            ml.log_and_print('[error] getforecastapi.py -> get_avalanche_warnings_as_json: EXCEPTION. RECURSIVE COUNT {0} for {1} in {2} to {3}'
                             .format(recursive_count, region_id, from_date, to_date))
            if recursive_count > 1:
                recursive_count -= 1        # count down
                warnings += get_avalanche_warnings_as_json(region_id, from_date, to_date, lang_key, recursive_count=recursive_count)

    return warnings


def get_avalanche_warnings(region_ids, from_date, to_date, lang_key=1):
    """Selects warnings and returns a list of AvalancheDanger Objects. This method adds the
    avalanche problems to the warning.

    :param region_ids:  [int or list of ints]       RegionID as given in the forecast api [1-99] or in regObs [101-199]
    :param from_date:   [date or string as yyyy-mm-dd]
    :param to_date:     [date or string as yyyy-mm-dd]
    :param lang_key:    [int]                       Language setting. 1 is norwegian and 2 is english.

    :return avalanche_danger_list: List of AvalancheDanger objects
    """

    warnings_as_json = get_avalanche_warnings_as_json(region_ids, from_date, to_date, lang_key=lang_key)
    avalanche_warning_list = []
    exception_counter = 0

    for w in warnings_as_json:
        #try:
        region_id = int(w['RegionId'])
        region_name = w['RegionName']
        date = dt.datetime.strptime(w['ValidFrom'][0:10], '%Y-%m-%d').date()
        danger_level = int(w['DangerLevel'])
        danger_level_name = w['DangerLevelName']
        author = w['Author']
        avalanche_forecast = w['AvalancheDanger']

        try:
            avalanche_nowcast = w['AvalancheWarning']
        except:
            avalanche_nowcast = ''
            ml.log_and_print('No nowcast available.')


        warning = vc.AvalancheDanger(region_id, region_name, 'Forecast API', date, danger_level, danger_level_name)
        warning.set_source('Forecast')
        warning.set_nick(author)
        warning.set_avalanche_nowcast(avalanche_nowcast)
        warning.set_avalanche_forecast(avalanche_forecast)

        try:
            warning.set_mountain_weather(w['MountainWeather'])
        except:
            ml.log_and_print('No MountainWeather tag found in json-string - set forecast_api_version to 4.0.1 or higher')

        # http://www.varsom.no/Snoskred/Senja/?date=18.03.2015
        # http://www.varsom.no/snoskredvarsling/varsel/Indre%20Sogn/2017-01-19
        varsom_name = region_name  # .replace(u'æ', u'a').replace(u'ø', u'o').replace(u'å', u'a')
        varsom_date = date.strftime("%Y-%m-%d")
        url = "http://www.varsom.no/snoskredvarsling/varsel/{0}/{1}".format(varsom_name, varsom_date)
        warning.set_url(url)

        if lang_key == 1:
            warning.set_main_message_no(w['MainText'])
        if lang_key == 2:
            warning.set_main_message_en(w['MainText'])

        if w['AvalancheProblems'] is not None:
            for p in w['AvalancheProblems']:

                order = p['AvalancheProblemId']              # sort order of the avalanche problems in this forecast
                problem_tid = p['AvalancheProblemTypeId']
                problem_name = p['AvalancheProblemTypeName']
                cause_tid = p['AvalCauseId']                            # weak layer
                cause_name = p['AvalCauseName']

                aval_main_type_tid = p['AvalancheTypeId']               # used on varsom
                aval_main_type_name = p['AvalancheTypeName']
                aval_type_tid = p['AvalancheExtId']                     # used in regObs
                aval_type_name = p['AvalancheExtName']

                destructive_size_tid = p['DestructiveSizeExtId']
                destructive_size_name = p['DestructiveSizeExtName']

                trigger_tid = p['AvalTriggerSimpleId']
                trigger_name = p['AvalTriggerSimpleName']
                distribution_tid = p['AvalPropagationId']
                distribution_name = p['AvalPropagationName']
                probability_tid = p['AvalProbabilityId']
                probability_name = p['AvalProbabilityName']

                exposed_height_1 = p['ExposedHeight1']
                exposed_height_2 = p['ExposedHeight2']
                exposed_height_fill = p['ExposedHeightFill']                # based on values in exp heigt 1 and 2 this colores the mountain
                valid_expositions = p['ValidExpositions']                   # north is first cahr and it goes clockwize

                problem = vc.AvalancheProblem(region_id, region_name, date, order, cause_name, 'Forecast', problem_inn=problem_name)

                problem.set_cause_tid(cause_tid)
                problem.set_problem(problem_name, problem_tid)
                problem.set_aval_type(aval_type_name, aval_type_tid)
                problem.set_aval_size(destructive_size_name, destructive_size_tid)
                problem.set_aval_trigger(trigger_name, trigger_tid)
                problem.set_aval_distribution(distribution_name)
                problem.set_aval_probability(probability_name)

                problem.set_danger_level(danger_level_name, danger_level)
                problem.set_url(url)

                problem.set_regobs_table('AvalancheWarnProblem')
                problem.set_nick_name(author)
                problem.set_lang_key(lang_key)

                warning.add_problem(problem)

        avalanche_warning_list.append(warning)
        '''
        except:
            ml.log_and_print('[error] getForecastApi -> get_avalanche_warnings: Exception at {0} of {1}'.format(len(avalanche_warning_list) + exception_counter, len(warnings_as_json)))
            exception_counter += 1
        '''
    # Sort by date
    avalanche_danger_list = sorted(avalanche_warning_list, key=lambda AvalancheDanger: AvalancheDanger.date)

    return avalanche_danger_list


def get_valid_regids(region_id, from_date, to_date):
    """Method looks up all forecasts for a region and selects and returns the RegIDs used in regObs. Thus, the list of
    RegIDs are for published forecasts.

    :param region_id:   [int]       RegionID as given in the forecast api [1-99] or in regObs [101-199]
    :param from_date:   [string]    date as yyyy-mm-dd
    :param to_date:     [string]    date as yyyy-mm-dd
    :return:            {RegID:date, RegID:date, ...}
    """

    warnings = get_avalanche_warnings_as_json(region_id, from_date, to_date)
    valid_regids = {}

    for w in warnings:
        danger_level = int(w["DangerLevel"])
        if danger_level > 0:
            valid_regids[w["RegId"]] = w["ValidFrom"]

    return valid_regids


def get_landslide_warnings_as_json(municipality, from_date, to_date, lang_key=1, recursive_count=5):
    """Selects landslide warnings and returns the json structured as given on the api as dict objects.

    :param municipality:    [int or list of ints]       Municipality numbers
    :param from_date:       [date or string as yyyy-mm-dd]
    :param to_date:         [date or string as yyyy-mm-dd]
    :param lang_key:        [int]                       Language setting. 1 is norwegian and 2 is english.
    :param recursive_count  [int]                       by default attempt the same request # times before giving up

    :return warnings:       [warnings]

    Eg. https://api01.nve.no/hydrology/forecast/landslide/v1.0.5/api/Warning/Municipality/1201/1/2018-06-03/2018-07-03
    """

    # If input isn't a list, make it so
    if not isinstance(municipality, list):
        municipality = [municipality]

    landslide_warnings = []
    recursive_count_default = recursive_count   # need the default for later

    for m in municipality:

        if len(municipality) > 1:
            # if we are looping the initial list make sure each item gets the recursive count default
            recursive_count = recursive_count_default

        landslide_api_base_url = 'https://api01.nve.no/hydrology/forecast/landslide/v1.0.5/api'
        headers = {'Content-Type': 'application/json'}
        url = landslide_api_base_url + '/Warning/Municipality/{0}/{1}/{2}/{3}'.format(m, lang_key, from_date, to_date)

        # If at first you don't succeed, try and try again.
        try:
            landslide_warnings_municipal = requests.get(url, headers=headers).json()
            ml.log_and_print('[info] getforecastapi.py -> get_landslide_warnings_as_json: {0} warnings found for {1} in {2} to {3}'
                             .format(len(landslide_warnings_municipal), m, from_date, to_date))
            landslide_warnings += landslide_warnings_municipal

        except:
            ml.log_and_print('[error] getforecastapi.py -> get_avalanche_warnings_as_json: EXCEPTION. RECURSIVE COUNT {0} for {1} in {2} to {3}'
                             .format(recursive_count, m, from_date, to_date))
            if recursive_count > 1:
                recursive_count -= 1        # count down
                landslide_warnings += get_landslide_warnings_as_json(m, from_date, to_date, lang_key, recursive_count=recursive_count)

    return landslide_warnings


if __name__ == "__main__":

    #land_slide_warnings = get_landslide_warnings_as_json([1201], dt.date(2018, 1, 1), dt.date(2018, 4, 1))
    warnings = get_avalanche_warnings([3022, 3014], dt.date(2016, 12, 1), dt.date(2016, 12, 21))
    # p = get_valid_regids(10, '2013-03-01', '2013-03-09')

    pass
