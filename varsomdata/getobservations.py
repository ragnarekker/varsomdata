# -*- coding: utf-8 -*-
"""
Contains classes and methods for accessing all on the Regobs webapi.

Modifications:
- 2019-05-29, raek: upgrade to use api v4 and logging with logger
"""

import datetime as dt
import requests as requests
import pandas as pd
import sys as sys
import logging as lg
from dateutil.parser import parse as parse
import setenvironment as env

__author__ = 'raek'


def _stringtime_2_datetime(stringtime):
    """
    Takes in a date as string, both given as unix datetime or normal local time, as string.
    Method returns a normal datetime object.

    :param stringtime:
    :return:           The date and time as datetime object
    """

    if stringtime is None:
        return None

    elif '/Date(' in stringtime:  # oData gives unix time. Unix date time in milliseconds from 1.1.1970
        unix_date_time = int(stringtime[6:-2])
        unix_datetime_in_seconds = unix_date_time / 1000  # For some reason they are given in miliseconds
        date = dt.datetime.fromtimestamp(int(unix_datetime_in_seconds))

    else:
        date = parse(stringtime)

    return date


def _reg_types_dict(registration_tids=None):
    """
    Method maps single RegistrationTID values to the query dictionary used in regObs webapi

    :param registration_tids:       [int or list of int] Definition given below
    :return:


    Registration IDs and names
    10	Notater, var Fritekst inntil april 2018
    11	Ulykke/hendelse
    12	Bilde
    13	Faretegn
    -14	Skader
    21	Vær
    22	Snødekke
    23	Snøprofil
    -24	Skredfaretegn
    25	Stabilitetstest
    26	Skredhendelse
    27	Observert skredaktivitet(2011)
    28	Skredfarevurdering (2012)
    -29	Svakt lag
    30	Skredfarevurdering (2013)
    31	Skredfarevurdering
    32	Skredproblem
    33	Skredaktivitet
    36  Topp-ned snøprofil (fra dec 2018)
    40	Snøskredvarsel
    50	Istykkelse
    51	Isdekningsgrad
    61	Vannstand (2017)
    62	Vannstand
    71	Skredhendelse
    80	Hendelser                   Grupperings type - Hendelser
    81	Skred og faretegn           Grupperings type - Skred og faretegn
    82	Snødekke og vær             Grupperings type - Snødekke og vær
    83	Vurderinger og problemer    Grupperings type - Vurderinger og problemer

    """

    # If input isn't a list, make it so
    if not isinstance(registration_tids, list):
        registration_tids = [registration_tids]

    registration_dicts = []
    for registration_tid in registration_tids:
        if registration_tid is None:
            return None
        elif registration_tid == 10:  # Notater
            registration_dicts.append({'Id': 10, 'SubTypes': []})
        elif registration_tid == 11:  # Ulykke/hendelse
            registration_dicts.append({'Id': 80, 'SubTypes': [11]})
        elif registration_tid == 12:  # Bilder
            return None  # Images cover all observation types
        elif registration_tid == 13:  # Faretegn
            registration_dicts.append({'Id': 81, 'SubTypes': [13]})
        elif registration_tid == 14:  # Skader
            registration_dicts.append({'Id': 14, 'SubTypes': []})
        elif registration_tid == 21:  # Vær
            registration_dicts.append({'Id': 82, 'SubTypes': [21]})
        elif registration_tid == 22:  # Snødekke
            registration_dicts.append({'Id': 82, 'SubTypes': [22]})
        elif registration_tid == 23:  # Snøprofil som bilder før dec 2018
            registration_dicts.append({'Id': 82, 'SubTypes': [23]})
        elif registration_tid == 25:  # Stabilitetstest
            registration_dicts.append({'Id': 82, 'SubTypes': [25]})
        elif registration_tid == 26:  # Skredhendelse
            registration_dicts.append({'Id': 81, 'SubTypes': [26]})
        elif registration_tid == 27:  # Skredaktivitet(2011)
            registration_dicts.append({'Id': 81, 'SubTypes': [27]})
        elif registration_tid == 28:  # Skredfarevurdering (2012)
            registration_dicts.append({'Id': 83, 'SubTypes': [28]})
        elif registration_tid == 30:  # Skredfarevurdering (2013)
            registration_dicts.append({'Id': 83, 'SubTypes': [30]})
        elif registration_tid == 31:  # Skredfarevurdering
            registration_dicts.append({'Id': 83, 'SubTypes': [31]})
        elif registration_tid == 32:  # Skredproblem
            registration_dicts.append({'Id': 83, 'SubTypes': [32]})
        elif registration_tid == 33:  # Skredaktivitet
            registration_dicts.append({'Id': 81, 'SubTypes': [33]})
        elif registration_tid == 36:  # Snøprofil
            registration_dicts.append({'Id': 82, 'SubTypes': [36]})
        elif registration_tid == 50:  # Istykkelse
            registration_dicts.append({'Id': 50, 'SubTypes': []})
        elif registration_tid == 51:  # Isdekningsgrad
            registration_dicts.append({'Id': 51, 'SubTypes': []})
        elif registration_tid == 61:  # Vannstand (2017)
            registration_dicts.append({'Id': 61, 'SubTypes': []})
        elif registration_tid == 62:  # Vannstand
            registration_dicts.append({'Id': 62, 'SubTypes': []})
        elif registration_tid == 71:  # Jordskredhendelse
            registration_dicts.append({'Id': 71, 'SubTypes': [0, 1, 2, 4, 11, 6, 7, 8, 10]})
        else:
            lg.warning("getobservations.py -> _reg_types_dict: RegistrationTID {0} not supported (yet)."
                       .format(registration_tid))

    return registration_dicts


def _look_up_name_and_summary(registration_tid, summaries):
    """Some common code used in all objects to map RegistrationName and Summary"""

    registration_name = None
    summary = None

    for s in summaries:
        if s['RegistrationTID'] == registration_tid:
            registration_name = s['RegistrationName']
            summary = s

    return registration_name, summary


def _get_object(registration_tid, d):
    """Given a RegistrationTID and data (d), map data to the right object. For forms that have a one-to-many
    relation, each data item must be mapped individually."""

    if registration_tid == 10:
        return [GeneralObservation(d)]

    elif registration_tid == 11:
        return [Incident(d)]

    elif registration_tid == 13:
        i = -1
        _objects = []
        for do in d['DangerObs']:
            i += 1
            _objects.append(DangerSign(d, i))
        return _objects

    elif registration_tid == 14:
        i = -1
        _objects = []
        for do in d['DamageObs']:
            i += 1
            _objects.append(DamageObs(d, i))
        return _objects

    elif registration_tid == 21:
        return [WeatherObservation(d)]

    elif registration_tid == 22:
        return [SnowSurfaceObservation(d)]

    elif registration_tid == 25:
        i = -1
        _objects = []
        for do in d['CompressionTest']:
            i += 1
            _objects.append(ColumnTest(d, i))
        return _objects

    elif registration_tid == 26:
        return [AvalancheObs(d)]

    elif registration_tid == 27:
        i = -1
        _objects = []
        for do in d['AvalancheActivityObs']:
            i += 1
            _objects.append(AvalancheActivityObs(d, i))
        return _objects

    elif registration_tid == 33:
        i = -1
        _objects = []
        for do in d['AvalancheActivityObs2']:
            i += 1
            _objects.append(AvalancheActivityObs2(d, i))
        return _objects

    elif registration_tid == 28:
        return [AvalancheEvaluation(d)]

    elif registration_tid == 30:
        return [AvalancheEvaluation2(d)]

    elif registration_tid == 31:
        return [AvalancheEvaluation3(d)]

    elif registration_tid == 32:
        i = -1
        _objects = []
        for do in d['AvalancheEvalProblem2']:
            i += 1
            _objects.append(AvalancheEvalProblem2(d, i))
        return _objects

    elif registration_tid == 36:
        return [SnowProfile(d)]

    elif registration_tid == 50:
        return [IceThickness(d)]

    elif registration_tid == 51:
        return [IceCover(d)]

    elif registration_tid == 61:
        return [WaterLevel(d)]

    elif registration_tid == 62:
        return [WaterLevel2(d)]

    elif registration_tid == 71:
        return [LandSlideObs(d)]

    else:
        lg.warning("getobservations.py -> _get_object: Unknown RegistrationTID.")
        return []


def _make_common_dict(o):
    """
    The common part of the dictionary representation.

    All Classes has a to_dict() method. A part of this dictionary representation is common for all and
    the code for making this is separated out here.

    :return _dict:"""

    _dict = {'RegistrationTID': o.RegistrationTID,
             'RegistrationName': o.RegistrationName,
             'RegID': o.RegID,
             'DtObsTime': o.DtObsTime,
             'DtRegTime': o.DtRegTime,
             'GeoHazardName': o.GeoHazardName,
             'GeoHazardTID': o.GeoHazardTID,
             'LangKey': o.LangKey,
             'LocationName': o.LocationName,
             'LocationID': o.LocationID,
             'UTMZone': o.UTMZone,
             'UTMEast': o.UTMEast,
             'UTMNorth': o.UTMNorth,
             'Latitude': o.Latitude,
             'Longitude': o.Longitude,
             'ForecastRegionName': o.ForecastRegionName,
             'ForecastRegionTID': o.ForecastRegionTID,
             'MunicipalName': o.MunicipalName,
             'NickName': o.NickName,
             'ObserverID': o.ObserverID,
             'CompetenceLevelName': o.CompetenceLevelName
             }

    return _dict


def _make_one_request(from_date=None, to_date=None, reg_id=None, registration_types=None,
                      region_ids=None, location_id=None, countries=None, time_zone=None,
                      observer_id=None, observer_nick=None, observer_competence=None, group_id=None,
                      geohazard_tids=0, lang_key=1, recursive_count=5, output='List'):
    """
    Part of get_data and the get_count method.
    Parameters mostly the same except observer_id and reg_id can not be lists.
    Exception is output ('List' or 'Count'). If 'Count' only the number of obs is returned.
    """

    log_ref = 'getobservations.py -> _make_one_request'
    records_requested = 100

    # Dates in the web-api request are strings
    if isinstance(from_date, dt.date):
        from_date = dt.date.strftime(from_date, '%Y-%m-%d')
    elif isinstance(from_date, dt.datetime):
        from_date = dt.datetime.strftime(from_date, '%Y-%m-%d')

    if isinstance(to_date, dt.date):
        to_date = dt.date.strftime(to_date, '%Y-%m-%d')
    elif isinstance(to_date, dt.datetime):
        to_date = dt.datetime.strftime(to_date, '%Y-%m-%d')

    # Only norwegian (lang_key = 1) and english (lang_key = 2) are supported. If other, default to english.
    if lang_key not in [1, 2]:
        lang_key = 2

    data = []  # data from one query

    # query object posted in the request
    search_query = {'LangKey': lang_key,
                    'RegId': reg_id,
                    'ObserverGuid': None,
                    'SelectedRegistrationTypes': _reg_types_dict(registration_types),
                    'SelectedRegions': region_ids,
                    'SelectedGeoHazards': geohazard_tids,
                    'ObserverId': observer_id,
                    'ObserverNickName': observer_nick,
                    'ObserverCompetence': observer_competence,
                    'GroupId': group_id,
                    'LocationId': location_id,
                    'TimeZone': time_zone,
                    'Countries': countries,
                    'FromDate': from_date,
                    'ToDate': to_date,
                    'NumberOfRecords': records_requested,  # int
                    'Offset': 0}

    url = 'https://api.regobs.no/v4/Search'

    count_request = requests.post(url + '/Count', json=search_query).json()
    total_count = count_request['TotalMatches']
    lg.info("{0}: {1} observations match the request.".format(log_ref, total_count))

    if output == 'Count':
        return total_count

    # get data from regObs api. It returns 100 items at a time. If more, continue requesting with an offset. Paging.
    while len(data) < total_count:

        # try and if there is an exception, try again.
        try:
            r = requests.post(url, json=search_query)
            responds = r.json()
            data += responds

            # log request status
            if r.status_code <= 299:

                if len(data) == 0:
                    lg.info("{0}: no data".format(log_ref))
                else:
                    lg.info("{0}: {1:.2f}%".format(log_ref, len(data) / total_count * 100))

                # get more data until we reach total_count
                if len(data) < total_count:
                    search_query['Offset'] += records_requested

            else:
                lg.warning("{0}: http {1} {2}".format(log_ref, r.status_code, r.reason))

        except Exception:
            error_msg = sys.exc_info()[0]
            lg.error("{0}: EXCEPTION. RECURSIVE COUNT {1} {2}".format(log_ref, recursive_count, error_msg))

            # When exception occurred, start requesting again. All that has happened in this scope is not important.
            # Call the current method again and make sure the received data goes direct to return within this scope.
            data_by_exception = []

            if recursive_count > 1:
                recursive_count -= 1  # count down
                data_by_exception = _make_one_request(from_date=from_date,
                                                      to_date=to_date,
                                                      reg_id=reg_id,
                                                      registration_types=registration_types,
                                                      region_ids=region_ids,
                                                      location_id=location_id,
                                                      countries=countries,
                                                      time_zone=time_zone,
                                                      observer_id=observer_id,
                                                      observer_nick=observer_nick,
                                                      observer_competence=observer_competence,
                                                      group_id=group_id,
                                                      geohazard_tids=geohazard_tids,
                                                      lang_key=lang_key,
                                                      output=output,
                                                      recursive_count=recursive_count)

            return data_by_exception

    return data


def get_count(from_date=None, to_date=None, registration_types=None,
              reg_ids=None, region_ids=None, location_id=None, countries=None, time_zone=None,
              observer_ids=None, observer_nick=None, observer_competence=None, group_id=None,
              geohazard_tids=0, lang_key=1):
    """
    Gets the count of observations for a given query.

    :param from_date:           [string] 'yyyy-mm-dd'. Result includes from date.
    :param to_date:             [string] 'yyyy-mm-dd'. Result includes to date.
    :param registration_types:  [string or list of strings] Default None gives all.
    :param reg_ids:             [int or list of ints] Default None gives all.
    :param region_ids:          [int or list of ints] Default None gives all.
    :param location_id:         [int]
    :param countries:           [int or list of ints] Default None gives all.
    :param time_zone:           [string] If Summaries should return a specific timezone.
    :param observer_ids:        [int or list of ints] Default None gives all.
    :param observer_nick        [string] Part of a observer nick name
    :param observer_competence  [int or list of int] as given in CompetenceLevelKDV
    :param group_id:            [int]
    :param geohazard_tids:      [int or list] Geohazards requested.
    :param lang_key:            [int] Default 1 gives Norwegian.

    :return:                    [int] Total matches to one query.
    """

    # If input isn't a list, make it so
    if not isinstance(registration_types, list):
        registration_types = [registration_types]

    if not isinstance(region_ids, list):
        region_ids = [region_ids]

    if not isinstance(countries, list):
        countries = [countries]

    if not isinstance(geohazard_tids, list):
        geohazard_tids = [geohazard_tids]

    # Regobs weabapi does not support multiple ObserverIDs and RegIDs. Making it so.
    if not isinstance(observer_ids, list):
        observer_ids = [observer_ids]

    if not isinstance(reg_ids, list):
        reg_ids = [reg_ids]

    total_count = 0

    for reg_id in reg_ids:
        for observer_id in observer_ids:
            part_count = _make_one_request(
                from_date=from_date, to_date=to_date, lang_key=lang_key, reg_id=reg_id,
                registration_types=registration_types, region_ids=region_ids, countries=countries,
                time_zone=time_zone, geohazard_tids=geohazard_tids,
                observer_id=observer_id, observer_nick=observer_nick, observer_competence=observer_competence,
                group_id=group_id, location_id=location_id, output='Count')

            total_count += part_count

    return total_count


def get_data(from_date=None, to_date=None, registration_types=None,
             reg_ids=None, region_ids=None, location_id=None, countries=None, time_zone=None,
             observer_ids=None, observer_nick=None, observer_competence=None, group_id=None,
             geohazard_tids=0, lang_key=1):
    """
    Gets data from Regobs webapi. Each observation returned as a dictionary in a list.

    :param from_date:           [string] 'yyyy-mm-dd'. Result includes from date.
    :param to_date:             [string] 'yyyy-mm-dd'. Result includes to date.
    :param registration_types:  [string or list of strings] Default None gives all.
    :param reg_ids:             [int or list of ints] Default None gives all.
    :param region_ids:          [int or list of ints] Default None gives all.
    :param location_id:         [int]
    :param countries:           [int or list of ints] Default None gives all.
    :param time_zone:           [string] If Summaries should return a specific timezone.
    :param observer_ids:        [int or list of ints] Default None gives all.
    :param observer_nick        [string] Part of a observer nick name
    :param observer_competence  [int or list of int] as given in CompetenceLevelKDV
    :param group_id:            [int]
    :param geohazard_tids:      [int or list] Geohazards requested.
    :param lang_key:            [int] Default 1 gives Norwegian.

    :return:                    [list] of dictionaries as given directly from the api.
    """

    # If input isn't a list, make it so
    if not isinstance(registration_types, list):
        registration_types = [registration_types]

    if not isinstance(region_ids, list):
        region_ids = [region_ids]

    if not isinstance(countries, list):
        countries = [countries]

    if not isinstance(geohazard_tids, list):
        geohazard_tids = [geohazard_tids]

    # regObs weabapi does not support multiple ObserverIDs and RegIDs. Making it so.
    if not isinstance(observer_ids, list):
        observer_ids = [observer_ids]

    if not isinstance(reg_ids, list):
        reg_ids = [reg_ids]

    all_data = []

    for reg_id in reg_ids:
        for observer_id in observer_ids:
            data = _make_one_request(
                from_date=from_date, to_date=to_date, lang_key=lang_key, reg_id=reg_id,
                registration_types=registration_types, region_ids=region_ids, countries=countries,
                time_zone=time_zone, geohazard_tids=geohazard_tids,
                observer_id=observer_id, observer_nick=observer_nick, observer_competence=observer_competence,
                group_id=group_id, location_id=location_id)

            all_data += data

    return all_data


class Registration:
    def __init__(self, d):
        self.RegID = int(d['RegID'])
        self.DtObsTime = _stringtime_2_datetime(d['DtObsTime'])
        self.DtRegTime = _stringtime_2_datetime(d['DtRegTime'])
        self.DtChangeTime = _stringtime_2_datetime(d['DtChangeTime'])
        self.GeoHazardTID = d['GeoHazardTID']
        self.GeoHazardName = d['GeoHazardName']

        self.OriginalData = d


class Location:
    def __init__(self, d):
        self.LocationName = d['ObsLocation']['LocationName']
        self.LocationID = d['ObsLocation']['ObsLocationID']

        self.UTMZone = int(d['ObsLocation']['UTMZone'])
        self.UTMEast = int(d['ObsLocation']['UTMEast'])
        self.UTMNorth = int(d['ObsLocation']['UTMNorth'])
        self.Latitude = d['ObsLocation']['Latitude']
        self.Longitude = d['ObsLocation']['Longitude']
        self.UTMSourceName = d['ObsLocation']['UTMSourceName']
        self.UTMSourceTID = int(d['ObsLocation']['UTMSourceTID'])

        self.ForecastRegionName = d['ObsLocation']['ForecastRegionName']
        self.ForecastRegionTID = d['ObsLocation']['ForecastRegionTID']
        self.MunicipalName = d['ObsLocation']['MunicipalName']
        self.MunicipalNo = d['ObsLocation']['MunicipalNo']
        self.CountryName = d['ObsLocation']['CountryName']
        self.CountryID = d['ObsLocation']['CountryId']

        self.Title = d['ObsLocation']['Title']
        self.Height = d['ObsLocation']['Height']


class Observer:
    def __init__(self, d):
        self.NickName = d['Observer']['NickName']
        self.ObserverID = int(d['Observer']['ObserverID'])
        # self.ObserverGUID = d['Observer']['ObserverGUID']
        self.CompetenceLevelTID = d['Observer']['CompetenceLevelTID']
        self.CompetenceLevelName = d['Observer']['CompetenceLevelName']

        self.ObserverGroupName = d['Observer']['ObserverGroupName']
        self.ObserverGroupID = d['Observer']['ObserverGroupID']


class Picture:
    def __init__(self, p):
        self.PictureID = p['PictureID']
        self.URLoriginal = env.image_basestring_original + '{}'.format(self.PictureID)
        self.URLlarge = env.image_basestring_large + '{}'.format(self.PictureID)
        self.Photographer = p['Photographer']
        self.Copyright = p['Copyright']
        self.Aspect = p['Aspect']
        self.GeoHazardTID = p['GeoHazardTID']
        self.GeoHazardName = p['GeoHazardName']
        self.RegistrationTID = p['RegistrationTID']
        self.RegistrationName = p['RegistrationName']
        self.Comment = p['Comment']

        self.OriginalData = p


class Pictures:
    """A parent class for listing of the pictures related to the form in question."""

    def __init__(self, d, registration_tid):
        self.Pictures = []
        for a in d['Attachments']:
            picture = Picture(a)
            # Pictures with TID 23 were profiles, but data model for profiles weren't added before TID 36
            if (picture.RegistrationTID == registration_tid) \
                    or (picture.RegistrationTID == 23 and registration_tid == 36):
                self.Pictures.append(picture)


class Observation(Registration, Location, Observer):
    def __init__(self, d):

        Registration.__init__(self, d)
        Location.__init__(self, d)
        Observer.__init__(self, d)

        self.Observations = []

        if d['GeneralObservation']:
            self.Observations += _get_object(10, d)

        if d['Incident']:
            self.Observations += _get_object(11, d)

        if d['DangerObs']:
            self.Observations += _get_object(13, d)

        if d['DamageObs']:
            self.Observations += _get_object(14, d)

        if d['WeatherObservation']:
            self.Observations += _get_object(21, d)

        if d['SnowSurfaceObservation']:
            self.Observations += _get_object(22, d)

        if d['CompressionTest']:
            self.Observations += _get_object(25, d)

        if d['AvalancheObs']:
            self.Observations += _get_object(26, d)

        if d['AvalancheActivityObs']:
            self.Observations += _get_object(27, d)

        if d['AvalancheActivityObs2']:
            self.Observations += _get_object(33, d)

        if d['AvalancheEvaluation']:
            self.Observations += _get_object(28, d)

        if d['AvalancheEvaluation2']:
            self.Observations += _get_object(30, d)

        if d['AvalancheEvaluation3']:
            self.Observations += _get_object(31, d)

        if d['AvalancheEvalProblem2']:
            self.Observations += _get_object(32, d)

        if d['SnowProfile2']:
            self.Observations += _get_object(36, d)

        if d['IceThickness']:
            self.Observations += _get_object(50, d)

        if d['IceCoverObs']:
            self.Observations += _get_object(51, d)

        if d['WaterLevel']:
            self.Observations += _get_object(61, d)

        if d['WaterLevel2']:
            self.Observations += _get_object(62, d)

        if d['LandSlideObs']:
            self.Observations += _get_object(71, d)

        self.LangKey = int(d['LangKey'])


class GeneralObservation(Registration, Location, Observer, Pictures):
    def __init__(self, d):
        Registration.__init__(self, d)
        Location.__init__(self, d)
        Observer.__init__(self, d)

        self.RegistrationTID = 10
        self.RegistrationName, self.Summary = _look_up_name_and_summary(self.RegistrationTID, d['Summaries'])
        self.LangKey = d['LangKey']

        Pictures.__init__(self, d, self.RegistrationTID)

        if d['GeneralObservation']:
            self.ObsHeader = d['GeneralObservation']['ObsHeader']
            self.ObsComment = d['GeneralObservation']['ObsComment']
            self.Comment = d['GeneralObservation']['Comment']

            self.URLs = []
            for u in d['GeneralObservation']['Urls']:
                self.URLs.append({'URLLine': u['UrlLine'], 'URLDescription': u['UrlDescription']})

        else:
            self.ObsHeader = None
            self.ObsComment = None
            self.Comment = None
            self.URLs = []

    def to_dict(self):
        """Convert the object to a dictionary.

        :return: dictionary representation of the Incident class
        """

        _dict_common = _make_common_dict(self)

        _dict_unique = {'ObsHeader': self.ObsHeader,
                        'ObsComment': self.ObsComment,
                        'Comment': self.Comment
                        }

        _dict = {**_dict_common, **_dict_unique}

        return _dict


class Incident(Registration, Location, Observer, Pictures):
    def __init__(self, d):
        Registration.__init__(self, d)
        Location.__init__(self, d)
        Observer.__init__(self, d)

        self.RegistrationTID = 11
        self.RegistrationName, self.Summary = _look_up_name_and_summary(self.RegistrationTID, d['Summaries'])

        Pictures.__init__(self, d, self.RegistrationTID)

        if d['Incident']:
            self.ActivityInfluencedTID = d['Incident']['ActivityInfluencedTID']
            self.ActivityInfluencedName = d['Incident']['ActivityInfluencedName']
            self.DamageExtentTID = d['Incident']['DamageExtentTID']
            self.DamageExtentName = d['Incident']['DamageExtentName']
            self.IncidentHeader = d['Incident']['IncidentHeader']
            self.IncidentIngress = d['Incident']['IncidentIngress']
            self.IncidentText = d['Incident']['IncidentText']
            self.URLs = []
            for u in d['Incident']['IncidentURLs']:
                self.URLs.append({'URLLine': u['UrlLine'], 'URLDescription': u['UrlDescription']})
            self.GeoHazardName = d['Incident']['GeoHazardName']
            self.GeoHazardTID = d['Incident']['GeoHazardTID']
        else:
            self.ActivityInfluencedTID = None
            self.ActivityInfluencedName = None
            self.DamageExtentTID = None
            self.DamageExtentName = None
            self.IncidentHeader = None
            self.IncidentIngress = None
            self.IncidentText = None
            self.URLs = []
            self.GeoHazardName = None
            self.GeoHazardTID = None

        self.LangKey = d['LangKey']

    def to_dict(self):
        """Convert the object to a dictionary.

        :return: dictionary representation of the Incident class
        """

        _dict_common = _make_common_dict(self)

        _dict_unique = {'ActivityInfluencedTID': self.ActivityInfluencedTID,
                        'ActivityInfluencedName': self.ActivityInfluencedName,
                        'DamageExtentTID': self.DamageExtentTID,
                        'DamageExtentName': self.DamageExtentName,
                        'IncidentHeader': self.IncidentHeader,
                        'IncidentIngress': self.IncidentIngress,
                        'IncidentText': self.IncidentText
                        }

        _dict = {**_dict_common, **_dict_unique}

        return _dict


class DangerSign(Registration, Location, Observer, Pictures):
    def __init__(self, d, i):
        Registration.__init__(self, d)
        Location.__init__(self, d)
        Observer.__init__(self, d)

        self.RegistrationTID = 13
        self.RegistrationName, self.Summary = _look_up_name_and_summary(self.RegistrationTID, d['Summaries'])

        Pictures.__init__(self, d, self.RegistrationTID)

        if i > -1:
            self.DangerObsID = d['DangerObs'][i]['DangerObsID']
            self.GeoHazardName = d['DangerObs'][i]['GeoHazardName']
            self.GeoHazardTID = d['DangerObs'][i]['GeoHazardTID']
            self.Comment = d['DangerObs'][i]['Comment']
            self.DangerSignName = d['DangerObs'][i]['DangerSignName']
            self.DangerSignTID = d['DangerObs'][i]['DangerSignTID']
        else:
            self.DangerObsID = None
            self.GeoHazardName = None
            self.GeoHazardTID = None
            self.Comment = None
            self.DangerSignName = None
            self.DangerSignTID = None

        self.LangKey = d['LangKey']

    def to_dict(self):
        """Convert the object to a dictionary.

        :return: dictionary representation of the DangerSign class
        """

        _dict_common = _make_common_dict(self)

        _dict_unique = {'DangerObsID': self.DangerObsID,
                        'GeoHazardName': self.GeoHazardName,
                        'GeoHazardTID': self.GeoHazardTID,
                        'Comment': self.Comment,
                        'DangerSignName': self.DangerSignName,
                        'DangerSignTID': self.DangerSignTID
                        }

        _dict = {**_dict_common, **_dict_unique}

        return _dict


class DamageObs(Registration, Location, Observer, Pictures):
    def __init__(self, d, i):
        Registration.__init__(self, d)
        Location.__init__(self, d)
        Observer.__init__(self, d)

        self.RegistrationTID = 14
        self.RegistrationName, self.Summary = _look_up_name_and_summary(self.RegistrationTID, d['Summaries'])

        Pictures.__init__(self, d, self.RegistrationTID)

        if i > -1:
            self.DamageTypeTID = d['DamageObs'][i]['DamageTypeTID']
            self.DamageTypeName = d['DamageObs'][i]['DamageTypeName']
            self.DamagePosition = d['DamageObs'][i]['DamagePosition']
            self.Comment = d['DamageObs'][i]['Comment']
        else:
            self.DamageTypeTID = None
            self.DamageTypeName = None
            self.DamagePosition = None
            self.Comment = None

        self.LangKey = d['LangKey']

    def to_dict(self):
        """Convert the object to a dictionary.

        :return: dictionary representation of the DamageObs class
        """

        _dict_common = _make_common_dict(self)

        _dict_unique = {'DamageTypeTID': self.DamageTypeTID,
                        'DamageTypeName': self.DamageTypeName,
                        'DamagePosition': self.DamagePosition,
                        'Comment': self.Comment
                        }

        _dict = {**_dict_common, **_dict_unique}

        return _dict


class WeatherObservation(Registration, Location, Observer, Pictures):
    def __init__(self, d):
        Registration.__init__(self, d)
        Location.__init__(self, d)
        Observer.__init__(self, d)

        self.RegistrationTID = 21
        self.RegistrationName, self.Summary = _look_up_name_and_summary(self.RegistrationTID, d['Summaries'])

        Pictures.__init__(self, d, self.RegistrationTID)

        if d['WeatherObservation']:
            self.PrecipitationTID = d['WeatherObservation']['PrecipitationTID']
            self.PrecipitationName = d['WeatherObservation']['PrecipitationName']
            self.AirTemperature = d['WeatherObservation']['AirTemperature']
            self.CloudCover = d['WeatherObservation']['CloudCover']
            self.WindDirection = d['WeatherObservation']['WindDirection']
            self.WindDirectionName = d['WeatherObservation']['WindDirectionName']
            self.WindSpeed = d['WeatherObservation']['WindSpeed']
            self.Comment = d['WeatherObservation']['Comment']
        else:
            self.PrecipitationTID = None
            self.PrecipitationName = None
            self.AirTemperature = None
            self.CloudCover = None
            self.WindDirection = None
            self.WindDirectionName = None
            self.WindSpeed = None
            self.Comment = None

        self.LangKey = d['LangKey']

    def to_dict(self):
        """Convert the object to a dictionary.

        :return: dictionary representation of the WeatherObservation class
        """

        _dict_common = _make_common_dict(self)

        _dict_unique = {'PrecipitationTID': self.PrecipitationTID,
                        'PrecipitationName': self.PrecipitationName,
                        'AirTemperature': self.AirTemperature,
                        'CloudCover': self.CloudCover,
                        'WindDirection': self.WindDirection,
                        'WindDirectionName': self.WindDirectionName,
                        'WindSpeed': self.WindSpeed,
                        'Comment': self.Comment
                        }

        _dict = {**_dict_common, **_dict_unique}

        return _dict


class SnowSurfaceObservation(Registration, Location, Observer, Pictures):
    def __init__(self, d):
        Registration.__init__(self, d)
        Location.__init__(self, d)
        Observer.__init__(self, d)

        self.RegistrationTID = 22
        self.RegistrationName, self.Summary = _look_up_name_and_summary(self.RegistrationTID, d['Summaries'])

        Pictures.__init__(self, d, self.RegistrationTID)

        if d['SnowSurfaceObservation']:
            self.SnowDepth = d['SnowSurfaceObservation']['SnowDepth']
            self.NewSnowDepth24 = d['SnowSurfaceObservation']['NewSnowDepth24']
            self.NewSnowLine = d['SnowSurfaceObservation']['NewSnowLine']
            self.SnowDriftTID = d['SnowSurfaceObservation']['SnowDriftTID']
            self.SnowDriftName = d['SnowSurfaceObservation']['SnowDriftName']
            self.HeightLimitLayeredSnow = d['SnowSurfaceObservation']['HeightLimitLayeredSnow']
            self.SnowLine = d['SnowSurfaceObservation']['SnowLine']
            self.SnowSurfaceTID = d['SnowSurfaceObservation']['SnowSurfaceTID']
            self.SnowSurfaceName = d['SnowSurfaceObservation']['SnowSurfaceName']
            self.SurfaceWaterContentTID = d['SnowSurfaceObservation']['SurfaceWaterContentTID']
            self.SurfaceWaterContentName = d['SnowSurfaceObservation']['SurfaceWaterContentName']
            self.Comment = d['SnowSurfaceObservation']['Comment']
        else:
            self.SnowDepth = None
            self.NewSnowDepth24 = None
            self.NewSnowLine = None
            self.SnowDriftTID = None
            self.SnowDriftName = None
            self.HeightLimitLayeredSnow = None
            self.SnowLine = None
            self.SnowSurfaceTID = None
            self.SnowSurfaceName = None
            self.SurfaceWaterContentTID = None
            self.SurfaceWaterContentName = None
            self.Comment = None

        self.LangKey = d['LangKey']

    def to_dict(self):
        """Convert the object to a dictionary.

        :return: dictionary representation of the SnowSurfaceObservation class
        """

        _dict_common = _make_common_dict(self)

        _dict_unique = {'SnowDepth': self.SnowDepth,
                        'NewSnowDepth24': self.NewSnowDepth24,
                        'NewSnowLine': self.NewSnowLine,
                        'SnowDriftTID': self.SnowDriftTID,
                        'SnowDriftName': self.SnowDriftName,
                        'HeightLimitLayeredSnow': self.HeightLimitLayeredSnow,
                        'SnowLine': self.SnowLine,
                        'SnowSurfaceTID': self.SnowSurfaceTID,
                        'SnowSurfaceName': self.SnowSurfaceName,
                        'SurfaceWaterContentTID': self.SurfaceWaterContentTID,
                        'SurfaceWaterContentName': self.SurfaceWaterContentName,
                        'Comment': self.Comment
                        }

        _dict = {**_dict_common, **_dict_unique}

        return _dict


class ProfileColumnTest:
    def __init__(self, t):
        if t:
            self.CompressionTestID = t['CompressionTestID']
            self.CompressionTestTID = t['CompressionTestTID']
            self.CompressionTestName = t['CompressionTestName']
            self.TapsFracture = t['TapsFracture']
            self.TapsFullPropagation = t['TapsFullPropagation']
            self.PropagationTID = t['PropagationTID']
            self.PropagationName = t['PropagationName']
            self.FractureDepth = t['FractureDepth']
            self.StabilityEvalTID = t['StabilityEvalTID']
            self.StabilityEvalName = t['StabilityEvalName']
            self.ComprTestFractureTID = t['ComprTestFractureTID']
            self.IncludeInSnowProfile = t['IncludeInSnowProfile']
            self.ComprTestFractureName = t['ComprTestFractureName']
            self.Comment = t['Comment']
        else:
            self.CompressionTestID = None
            self.CompressionTestTID = None
            self.CompressionTestName = None
            self.TapsFracture = None
            self.TapsFullPropagation = None
            self.PropagationTID = None
            self.PropagationName = None
            self.FractureDepth = None
            self.StabilityEvalTID = None
            self.StabilityEvalName = None
            self.ComprTestFractureTID = None
            self.IncludeInSnowProfile = None
            self.ComprTestFractureName = None
            self.Comment = None


class ColumnTest(Registration, Location, Observer, Pictures, ProfileColumnTest):
    def __init__(self, d, i):
        Registration.__init__(self, d)
        Location.__init__(self, d)
        Observer.__init__(self, d)

        self.RegistrationTID = 25
        self.RegistrationName, self.Summary = _look_up_name_and_summary(self.RegistrationTID, d['Summaries'])

        Pictures.__init__(self, d, self.RegistrationTID)

        # Some tests are independent of the profile, but the ProfileColumnTest class contains the common values.
        if i > -1:
            ProfileColumnTest.__init__(self, d['CompressionTest'][i])
        else:
            ProfileColumnTest.__init__(self, None)

        self.LangKey = d['LangKey']

    def to_dict(self):
        """Convert the object to a dictionary.

        :return: dictionary representation of the ColumnTest class
        """

        _dict_common = _make_common_dict(self)

        _dict_unique = {'CompressionTestID': self.CompressionTestID,
                        'CompressionTestTID': self.CompressionTestTID,
                        'CompressionTestName': self.CompressionTestName,
                        'TapsFracture': self.TapsFracture,
                        'TapsFullPropagation': self.TapsFullPropagation,
                        'PropagationTID': self.PropagationTID,
                        'PropagationName': self.PropagationName,
                        'FractureDepth': self.FractureDepth,
                        'StabilityEvalTID': self.StabilityEvalTID,
                        'StabilityEvalName': self.StabilityEvalName,
                        'ComprTestFractureTID': self.ComprTestFractureTID,
                        'IncludeInSnowProfile': self.IncludeInSnowProfile,
                        'ComprTestFractureName': self.ComprTestFractureName,
                        'Comment': self.Comment
                        }

        _dict = {**_dict_common, **_dict_unique}

        return _dict


class AvalancheObs(Registration, Location, Observer, Pictures):
    def __init__(self, d):
        Registration.__init__(self, d)
        Location.__init__(self, d)
        Observer.__init__(self, d)

        self.RegistrationTID = 26
        self.RegistrationName, self.Summary = _look_up_name_and_summary(self.RegistrationTID, d['Summaries'])

        Pictures.__init__(self, d, self.RegistrationTID)

        if d['AvalancheObs']:
            self.AvalancheName = d['AvalancheObs']['AvalancheName']
            self.AvalancheTriggerName = d['AvalancheObs']['AvalancheTriggerName']
            self.Comment = d['AvalancheObs']['Comment']
            self.DestructiveSizeName = d['AvalancheObs']['DestructiveSizeName']
            self.DtAvalancheTime = _stringtime_2_datetime(d['AvalancheObs']['DtAvalancheTime'])
            self.HeightStartZone = d['AvalancheObs']['HeightStartZone']
            self.HeightStopZone = d['AvalancheObs']['HeightStopZone']
            self.SnowLine = d['AvalancheObs']['SnowLine']
            self.TerrainStartZoneName = d['AvalancheObs']['TerrainStartZoneName']
            self.UTMEastStop = d['AvalancheObs']['UTMEastStop']
            self.UTMNorthStop = d['AvalancheObs']['UTMNorthStop']
            self.UTMZoneStop = d['AvalancheObs']['UTMZoneStop']
        else:
            self.AvalancheName = None
            self.AvalancheTriggerName = None
            self.Comment = None
            self.DestructiveSizeName = None
            self.DtAvalancheTime = None
            self.HeightStartZone = None
            self.HeightStopZone = None
            self.SnowLine = None
            self.TerrainStartZoneName = None
            self.UTMEastStop = None
            self.UTMNorthStop = None
            self.UTMZoneStop = None

        self.LangKey = d['LangKey']

    def to_dict(self):
        """Convert the object to a dictionary.

        :return: dictionary representation of the AcalancheObs class
        """

        _dict_common = _make_common_dict(self)

        _dict_unique = {'AvalancheName': self.AvalancheName,
                        'AvalancheTriggerName': self.AvalancheTriggerName,
                        'Comment': self.Comment,
                        'DestructiveSizeName': self.DestructiveSizeName,
                        'DtAvalancheTime': self.DtAvalancheTime,
                        'HeightStartZone': self.HeightStartZone,
                        'HeightStopZone': self.HeightStopZone,
                        'SnowLine': self.SnowLine,
                        'TerrainStartZoneName': self.TerrainStartZoneName,
                        'UTMEastStop': self.UTMEastStop,
                        'UTMNorthStop': self.UTMNorthStop,
                        'UTMZoneStop': self.UTMZoneStop
                        }

        _dict = {**_dict_common, **_dict_unique}

        return _dict


class AvalancheActivityObs(Registration, Location, Observer, Pictures):
    def __init__(self, d, i):
        Registration.__init__(self, d)
        Location.__init__(self, d)
        Observer.__init__(self, d)

        self.RegistrationTID = 27
        self.RegistrationName, self.Summary = _look_up_name_and_summary(self.RegistrationTID, d['Summaries'])

        Pictures.__init__(self, d, self.RegistrationTID)

        if i > -1:
            self.EstimatedNumTID = d['AvalancheActivityObs'][i]['EstimatedNumTID']
            self.EstimatedNumName = d['AvalancheActivityObs'][i]['EstimatedNumName']
            self.DestructiveSizeName = d['AvalancheActivityObs'][i]['DestructiveSizeName']
            self.Aspect = d['AvalancheActivityObs'][i]['Aspect']
            self.HeightStartingZone = d['AvalancheActivityObs'][i]['HeigthStartZone']
            self.AvalancheName = d['AvalancheActivityObs'][i]['AvalancheName']
            self.AvalancheTriggerName = d['AvalancheActivityObs'][i]['AvalancheTriggerName']
            self.TerrainStartingZone = d['AvalancheActivityObs'][i]['TerrainStartZoneName']
            self.DtAvalancheTime = _stringtime_2_datetime(d['AvalancheActivityObs'][i]['DtAvalancheTime'])
            self.Snowline = d['AvalancheActivityObs'][i]['SnowLine']
            self.Comment = d['AvalancheActivityObs'][i]['Comment']
        else:
            self.EstimatedNumTID = None
            self.EstimatedNumName = None
            self.DestructiveSizeName = None
            self.Aspect = None
            self.HeightStartingZone = None
            self.AvalancheName = None
            self.AvalancheTriggerName = None
            self.TerrainStartingZone = None
            self.DtAvalancheTime = None
            self.Snowline = None
            self.Comment = None

        self.LangKey = d['LangKey']

    def to_dict(self):
        """Convert the object to a dictionary.

        :return: dictionary representation of the AvalancheActivityObs class
        """

        _dict_common = _make_common_dict(self)

        _dict_unique = {'EstimatedNumTID': self.EstimatedNumTID,
                        'EstimatedNumName': self.EstimatedNumName,
                        'DestructiveSizeName': self.DestructiveSizeName,
                        'Aspect': self.Aspect,
                        'HeigthStartZone': self.HeightStartingZone,
                        'AvalancheName': self.AvalancheName,
                        'AvalancheTriggerName': self.AvalancheTriggerName,
                        'TerrainStartZoneName': self.TerrainStartingZone,
                        'DtAvalancheTime': self.DtAvalancheTime,
                        'SnowLine': self.Snowline,
                        'Comment': self.Comment
                        }

        _dict = {**_dict_common, **_dict_unique}

        return _dict


class AvalancheActivityObs2(Registration, Location, Observer, Pictures):
    def __init__(self, d, i):

        Registration.__init__(self, d)
        Location.__init__(self, d)
        Observer.__init__(self, d)

        self.RegistrationTID = 33
        self.RegistrationName, self.Summary = _look_up_name_and_summary(self.RegistrationTID, d['Summaries'])

        Pictures.__init__(self, d, self.RegistrationTID)

        if i > -1:
            self.EstimatedNumTID = d['AvalancheActivityObs2'][i]['EstimatedNumTID']
            self.EstimatedNumName = d['AvalancheActivityObs2'][i]['EstimatedNumName']

            self.DtStart = _stringtime_2_datetime(d['AvalancheActivityObs2'][i]['DtStart'])
            self.DtEnd = _stringtime_2_datetime(d['AvalancheActivityObs2'][i]['DtEnd'])
            if self.DtStart is not None and self.DtEnd is not None:
                self.DtMiddleTime = self.DtStart + (self.DtEnd - self.DtStart) / 2  # Middle time of activity period
            else:
                self.DtMiddleTime = None

            # ValidExposition is int of eight char. First is N, second is NE etc.
            self.ValidExposition = d['AvalancheActivityObs2'][i]['ValidExposition']
            self.ExposedHeight1 = d['AvalancheActivityObs2'][i]['ExposedHeight1']  # upper height
            self.ExposedHeight2 = d['AvalancheActivityObs2'][i]['ExposedHeight2']  # lower height
            self.ExposedHeightComboTID = d['AvalancheActivityObs2'][i]['ExposedHeightComboTID']

            self.AvalancheExtName = d['AvalancheActivityObs2'][i]['AvalancheExtName']
            self.AvalCauseName = d['AvalancheActivityObs2'][i]['AvalCauseName']
            self.AvalTriggerSimpleName = d['AvalancheActivityObs2'][i]['AvalTriggerSimpleName']
            self.DestructiveSizeName = d['AvalancheActivityObs2'][i]['DestructiveSizeName']
            self.AvalPropagationName = d['AvalancheActivityObs2'][i]['AvalPropagationName']
            self.Comment = d['AvalancheActivityObs2'][i]['Comment']

        else:
            self.EstimatedNumTID = None
            self.EstimatedNumName = None
            self.DtStart = None
            self.DtEnd = None
            self.DtMiddleTime = None
            self.ValidExposition = None
            self.ExposedHeight1 = None
            self.ExposedHeight2 = None
            self.ExposedHeightComboTID = None
            self.AvalancheExtName = None
            self.AvalCauseName = None
            self.AvalTriggerSimpleName = None
            self.DestructiveSizeName = None
            self.AvalPropagationName = None
            self.Comment = None

        self.LangKey = d['LangKey']

    def to_dict(self):
        """Convert the object to a dictionary.

        :return: dictionary representation of the AvalancheActivityObs2 class
        """

        _dict_common = _make_common_dict(self)

        _dict_unique = {'EstimatedNumTID': self.EstimatedNumTID,
                        'EstimatedNumName': self.EstimatedNumName,
                        'DtStart': self.DtStart,
                        'DtEnd': self.DtEnd,
                        'DtMiddleTime': self.DtMiddleTime,
                        'ValidExposition': self.ValidExposition,
                        'ExposedHeight1': self.ExposedHeight1,
                        'ExposedHeight2': self.ExposedHeight2,
                        'ExposedHeightComboTID': self.ExposedHeightComboTID,
                        'AvalancheExtName': self.AvalancheExtName,
                        'AvalCauseName': self.AvalCauseName,
                        'AvalTriggerSimpleName': self.AvalTriggerSimpleName,
                        'DestructiveSizeName': self.DestructiveSizeName,
                        'AvalPropagationName': self.AvalPropagationName,
                        'Comment': self.Comment
                        }

        _dict = {**_dict_common, **_dict_unique}

        return _dict


class AvalancheEvalProblem0(Registration, Location, Observer):
    """The first avalanche problems used. At that time the problems were a list
    in the AvalancheEvaluation table. The avalanche problems where just text."""

    def __init__(self, d, ap_id, tid, name):
        Registration.__init__(self, d)
        Location.__init__(self, d)
        Observer.__init__(self, d)

        self.RegistrationTID = 28
        self.RegistrationName, self.Summary = _look_up_name_and_summary(self.RegistrationTID, d['Summaries'])

        self.AvalancheProblemID = ap_id
        self.AvalancheProblemTID = tid
        self.AvalancheProblemName = name

        self.LangKey = d['LangKey']


class AvalancheEvaluation(Registration, Location, Observer, Pictures):
    def __init__(self, d):

        Registration.__init__(self, d)
        Location.__init__(self, d)
        Observer.__init__(self, d)

        self.RegistrationTID = 28
        self.RegistrationName, self.Summary = _look_up_name_and_summary(self.RegistrationTID, d['Summaries'])

        Pictures.__init__(self, d, self.RegistrationTID)

        if d['AvalancheEvaluation']:
            self.AvalancheDangerTID = d['AvalancheEvaluation']['AvalancheDangerTID']
            self.AvalancheDangerName = d['AvalancheEvaluation']['AvalancheDangerName']
            self.AvalancheEvaluation = d['AvalancheEvaluation']['AvalancheEvaluation1']

            self.AvalancheProblems = []
            if d['AvalancheEvaluation']['AvalancheProblemTID1'] != 0:
                ap_id = 1
                tid = d['AvalancheEvaluation']['AvalancheProblemTID1']
                name = d['AvalancheEvaluation']['AvalancheProblemName1']
                self.AvalancheProblems.append(AvalancheEvalProblem0(d, ap_id, tid, name))
            if d['AvalancheEvaluation']['AvalancheProblemTID2'] != 0:
                ap_id = 2
                tid = d['AvalancheEvaluation']['AvalancheProblemTID2']
                name = d['AvalancheEvaluation']['AvalancheProblemName2']
                self.AvalancheProblems.append(AvalancheEvalProblem0(d, ap_id, tid, name))
            if d['AvalancheEvaluation']['AvalancheProblemTID3'] != 0:
                ap_id = 3
                tid = d['AvalancheEvaluation']['AvalancheProblemTID3']
                name = d['AvalancheEvaluation']['AvalancheProblemName3']
                self.AvalancheProblems.append(AvalancheEvalProblem0(d, ap_id, tid, name))

            self.ValidExposition = d['AvalancheEvaluation']['ValidExposition']
            self.ValidHeightFrom = d['AvalancheEvaluation']['ValidHeightFrom']
            self.ValidHeightRelative = d['AvalancheEvaluation']['ValidHeightRelative']
            self.ValidHeightTo = d['AvalancheEvaluation']['ValidHeigtTo']
            self.Comment = d['AvalancheEvaluation']['Comment']

        else:
            self.AvalancheDangerTID = None
            self.AvalancheDangerName = None
            self.AvalancheEvaluation = None
            self.AvalancheProblems = []
            self.ValidExposition = None
            self.ValidHeightFrom = None
            self.ValidHeightRelative = None
            self.ValidHeightTo = None
            self.Comment = None

        self.LangKey = d['LangKey']

    def to_dict(self):
        """Convert the object to a dictionary.

        :return: dictionary representation of the AvalancheEvaluation class
        """

        _dict_common = _make_common_dict(self)

        _dict_unique = {'AvalancheDangerTID': self.AvalancheDangerTID,
                        'AvalancheDangerName': self.AvalancheDangerName,
                        'AvalancheEvaluation': self.AvalancheEvaluation,
                        'ValidExposition': self.ValidExposition,
                        'ValidHeightFrom': self.ValidHeightFrom,
                        'ValidHeightRelative': self.ValidHeightRelative,
                        'ValidHeightTo': self.ValidHeightTo,
                        'Comment': self.Comment
                        }

        # generate dummy keys for three potential avalanche problems
        for n in range(1, 4):
            _ap_dict = {f'AvalancheProblemTID{n}': None,
                        f'AvalancheProblemName{n}': None
                        }
            _dict_unique.update(_ap_dict)

        # insert values for the issued avalanche problem(s)
        for p in self.AvalancheProblems:
            n = p.AvalancheProblemID
            _ap_dict = {f'AvalancheProblemTID{n}': p.AvalancheProblemTID,
                        f'AvalancheProblemName{n}': p.AvalancheProblemName
                        }
            _dict_unique.update(_ap_dict)

        _dict = {**_dict_common, **_dict_unique}

        return _dict


class AvalancheEvalProblem(Registration, Location, Observer):
    """List in AvalancheEvaluation2. Part of AvalancheEvaluation2 (RegistrationTID = 30)."""

    def __init__(self, d, p):
        Registration.__init__(self, d)
        Location.__init__(self, d)
        Observer.__init__(self, d)

        self.RegistrationTID = 30
        self.RegistrationName, self.Summary = _look_up_name_and_summary(self.RegistrationTID, d['Summaries'])

        self.AvalancheProblemID = p['AvalancheEvalProblemID']
        self.AvalCauseName = p['AvalCauseName']
        self.AvalCauseExtName = p['AvalCauseExtName']
        self.AvalancheProbabilityName = p['AvalProbabilityName']
        self.AvalReleaseHeightName = p['AvalReleaseHeightName']
        self.AvalTriggerSimpleName = p['AvalTriggerSimpleName']
        self.AvalancheExtName = p['AvalancheExtName']
        self.AvalancheProbabilityAutoText = p['AvalancheProbabilityAutoText']
        self.AvalancheProblemAutoText = p['AvalancheProblemAutoText']
        self.DestructiveSizeExtName = p['DestructiveSizeExtName']
        self.Comment = p['Comment']

        self.LangKey = d['LangKey']


class AvalancheEvaluation2(Registration, Location, Observer, Pictures):
    def __init__(self, d):
        Registration.__init__(self, d)
        Location.__init__(self, d)
        Observer.__init__(self, d)

        self.RegistrationTID = 30
        self.RegistrationName, self.Summary = _look_up_name_and_summary(self.RegistrationTID, d['Summaries'])

        Pictures.__init__(self, d, self.RegistrationTID)

        if d['AvalancheEvaluation2']:
            self.AvalancheEvaluation = d['AvalancheEvaluation2']['AvalancheEvaluation']
            self.AvalancheDevelopment = d['AvalancheEvaluation2']['AvalancheDevelopment']
            self.AvalancheDangerTID = d['AvalancheEvaluation2']['AvalancheDangerTID']
            self.AvalancheDangerName = d['AvalancheEvaluation2']['AvalancheDangerName']
            self.ExposedClimateTID = d['AvalancheEvaluation2']['ExposedClimateTID']
            self.ExposedClimateName = d['AvalancheEvaluation2']['ExposedClimateName']

            # int of eight char. First char is N, second is NE etc.
            self.ValidExposition = d['AvalancheEvaluation2']['ValidExposition']
            self.ExposedHeight1 = d['AvalancheEvaluation2']['ExposedHeight1']  # upper height
            self.ExposedHeight2 = d['AvalancheEvaluation2']['ExposedHeight2']  # lower height
            self.ExposedHeightComboTID = d['AvalancheEvaluation2']['ExposedHeightComboTID']
            self.Comment = d['AvalancheEvaluation2']['Comment']

            self.AvalancheProblems = []
            for p in d['AvalancheEvaluation2']['AvalancheEvalProblems']:
                if p['AvalCauseTID'] != 0 or p['AvalCauseExtTID'] != 0:
                    self.AvalancheProblems.append(AvalancheEvalProblem(d, p))

        else:
            self.AvalancheEvaluation = None
            self.AvalancheDevelopment = None
            self.AvalancheDangerTID = None
            self.AvalancheDangerName = None
            self.ExposedClimateTID = None
            self.ExposedClimateTName = None
            self.ValidExposition = None
            self.ExposedHeight1 = None
            self.ExposedHeight2 = None
            self.ExposedHeightComboTID = None
            self.Comment = None
            self.AvalancheProblems = []

        self.LangKey = d['LangKey']

    def to_dict(self):
        """Convert the object to a dictionary.

        :return: dictionary representation of the AvalancheEvaluation2 class
        """

        _dict_common = _make_common_dict(self)

        _dict_unique = {'AvalancheEvaluation': self.AvalancheEvaluation,
                        'AvalancheDevelopment': self.AvalancheDevelopment,
                        'AvalancheDangerTID': self.AvalancheDangerTID,
                        'AvalancheDangerName': self.AvalancheDangerName,
                        'ExposedClimateTID': self.ExposedClimateTID,
                        'ExposedClimateName': self.ExposedClimateName,
                        'ValidExposition': self.ValidExposition,
                        'ExposedHeight1': self.ExposedHeight1,
                        'ExposedHeight2': self.ExposedHeight2,
                        'ExposedHeightComboTID': self.ExposedHeightComboTID,
                        'Comment': self.Comment
                        }

        # generate dummy keys for three potential avalanche problems
        for n in range(1, 4):
            _ap_dict = {f'AvalCauseName{n}': None,
                        f'AvalCauseExtName{n}': None,
                        f'AvalProbabilityName{n}': None,
                        f'AvalReleaseHeightName{n}': None,
                        f'AvalTriggerSimpleName{n}': None,
                        f'AvalancheExtName{n}': None,
                        f'AvalancheProbabilityAutoText{n}': None,
                        f'AvalancheProblemAutoText{n}': None,
                        f'DestructiveSizeExtName{n}': None,
                        f'Comment{n}': None,
                        }
            _dict_unique.update(_ap_dict)

        # insert values for the issued avalanche problem(s)
        for p in self.AvalancheProblems:
            n = p.AvalancheProblemID
            _ap_dict = {f'AvalCauseName{n}': p.AvalCauseName,
                        f'AvalCauseExtName{n}': p.AvalCauseExtName,
                        f'AvalProbabilityName{n}': p.AvalancheProbabilityName,
                        f'AvalReleaseHeightName{n}': p.AvalReleaseHeightName,
                        f'AvalTriggerSimpleName{n}': p.AvalTriggerSimpleName,
                        f'AvalancheExtName{n}': p.AvalancheExtName,
                        f'AvalancheProbabilityAutoText{n}': p.AvalancheProbabilityAutoText,
                        f'AvalancheProblemAutoText{n}': p.AvalancheProblemAutoText,
                        f'DestructiveSizeExtName{n}': p.DestructiveSizeExtName,
                        f'Comment{n}': p.Comment
                        }
            _dict_unique.update(_ap_dict)

        _dict = {**_dict_common, **_dict_unique}

        return _dict


class AvalancheEvaluation3(Registration, Location, Observer, Pictures):
    def __init__(self, d):
        Registration.__init__(self, d)
        Location.__init__(self, d)
        Observer.__init__(self, d)

        self.RegistrationTID = 31
        self.RegistrationName, self.Summary = _look_up_name_and_summary(self.RegistrationTID, d['Summaries'])

        Pictures.__init__(self, d, self.RegistrationTID)

        if d['AvalancheEvaluation3']:
            self.AvalancheEvaluation = d['AvalancheEvaluation3']['AvalancheEvaluation']
            self.AvalancheDevelopment = d['AvalancheEvaluation3']['AvalancheDevelopment']
            self.AvalancheDangerTID = d['AvalancheEvaluation3']['AvalancheDangerTID']
            self.AvalancheDangerName = d['AvalancheEvaluation3']['AvalancheDangerName']
            self.ForecastCorrectTID = d['AvalancheEvaluation3']['ForecastCorrectTID']
            self.ForecastCorrectName = d['AvalancheEvaluation3']['ForecastCorrectName']
            self.ForecastComment = d['AvalancheEvaluation3']['ForecastComment']
        else:
            self.AvalancheEvaluation = None
            self.AvalancheDevelopment = None
            self.AvalancheDangerTID = None
            self.AvalancheDangerName = None
            self.ForecastCorrectTID = None
            self.ForecastCorrectName = None
            self.ForecastComment = None

        self.LangKey = d['LangKey']

    def to_dict(self):
        """Convert the object to a dictionary.

        :return: dictionary representation of the AvalancheEvaluation3 class
        """

        _dict_common = _make_common_dict(self)

        _dict_unique = {'AvalancheEvaluation': self.AvalancheEvaluation,
                        'AvalancheDevelopment': self.AvalancheDevelopment,
                        'AvalancheDangerTID': self.AvalancheDangerTID,
                        'AvalancheDangerName': self.AvalancheDangerName,
                        'ForecastCorrectTID': self.ForecastCorrectTID,
                        'ForecastCorrectName': self.ForecastCorrectName,
                        'ForecastComment': self.ForecastComment
                        }

        _dict = {**_dict_common, **_dict_unique}

        return _dict


class AvalancheEvalProblem2(Registration, Location, Observer, Pictures):
    def __init__(self, d, i):
        Registration.__init__(self, d)
        Location.__init__(self, d)
        Observer.__init__(self, d)

        self.RegistrationTID = 32
        self.RegistrationName, self.Summary = _look_up_name_and_summary(self.RegistrationTID, d['Summaries'])

        Pictures.__init__(self, d, self.RegistrationTID)

        if i > -1:
            self.AvalancheProblemID = d['AvalancheEvalProblem2'][i]['AvalancheEvalProblemID']

            self.AvalCauseAttributeCrystalTID = d['AvalancheEvalProblem2'][i]['AvalCauseAttributeCrystalTID']
            self.AvalCauseAttributeLightTID = d['AvalancheEvalProblem2'][i]['AvalCauseAttributeLightTID']
            self.AvalCauseAttributeSoftTID = d['AvalancheEvalProblem2'][i]['AvalCauseAttributeSoftTID']
            self.AvalCauseAttributeThinTID = d['AvalancheEvalProblem2'][i]['AvalCauseAttributeThinTID']

            self.AvalCauseAttributeCrystalName = d['AvalancheEvalProblem2'][i]['AvalCauseAttributeCrystalName']
            self.AvalCauseAttributeLightName = d['AvalancheEvalProblem2'][i]['AvalCauseAttributeLightName']
            self.AvalCauseAttributeSoftName = d['AvalancheEvalProblem2'][i]['AvalCauseAttributeSoftName']
            self.AvalCauseAttributeThinName = d['AvalancheEvalProblem2'][i]['AvalCauseAttributeThinName']

            self.AvalCauseDepthName = d['AvalancheEvalProblem2'][i]['AvalCauseDepthName']
            self.AvalCauseName = d['AvalancheEvalProblem2'][i]['AvalCauseName']
            self.AvalCauseTID = d['AvalancheEvalProblem2'][i]['AvalCauseTID']
            self.AvalTriggerSimpleName = d['AvalancheEvalProblem2'][i]['AvalTriggerSimpleName']
            self.AvalancheProbabilityName = d['AvalancheEvalProblem2'][i]['AvalProbabilityName']
            self.DestructiveSizeName = d['AvalancheEvalProblem2'][i]['DestructiveSizeName']
            self.AvalPropagationName = d['AvalancheEvalProblem2'][i]['AvalPropagationName']

            # int of eight char. First char is N, second is NE etc.
            self.ValidExposition = d['AvalancheEvalProblem2'][i]['ValidExposition']
            self.ExposedHeight1 = d['AvalancheEvalProblem2'][i]['ExposedHeight1']  # upper height
            self.ExposedHeight2 = d['AvalancheEvalProblem2'][i]['ExposedHeight2']  # lower height
            self.ExposedHeightComboTID = d['AvalancheEvalProblem2'][i]['ExposedHeightComboTID']

            self.AvalancheExtName = d['AvalancheEvalProblem2'][i]['AvalancheExtName']
            self.AvalancheExtTID = d['AvalancheEvalProblem2'][i]['AvalancheExtTID']
            self.Comment = d['AvalancheEvalProblem2'][i]['Comment']

        else:
            self.AvalancheProblemID = None
            self.AvalCauseAttributeCrystalTID = None
            self.AvalCauseAttributeLightTID = None
            self.AvalCauseAttributeSoftTID = None
            self.AvalCauseAttributeThinTID = None
            self.AvalCauseAttributeCrystalName = None
            self.AvalCauseAttributeLightName = None
            self.AvalCauseAttributeSoftName = None
            self.AvalCauseAttributeThinName = None
            self.AvalCauseDepthName = None
            self.AvalCauseName = None
            self.AvalCauseTID = None
            self.AvalTriggerSimpleName = None
            self.AvalancheProbabilityName = None
            self.DestructiveSizeName = None
            self.AvalPropagationName = None
            self.ValidExposition = None
            self.ExposedHeight1 = None
            self.ExposedHeight2 = None
            self.ExposedHeightComboTID = None
            self.AvalancheExtName = None
            self.AvalancheExtTID = None
            self.Comment = None

        self.LangKey = d['LangKey']

    def to_dict(self):
        """Convert the object to a dictionary.

        :return: dictionary representation of the AvalancheEvalProblem2 class
        """

        _dict_common = _make_common_dict(self)

        _dict_unique = {'AvalancheEvalProblemID': self.AvalancheProblemID,
                        'AvalCauseAttributeCrystalTID': self.AvalCauseAttributeCrystalTID,
                        'AvalCauseAttributeLightTID': self.AvalCauseAttributeLightTID,
                        'AvalCauseAttributeSoftTID': self.AvalCauseAttributeSoftTID,
                        'AvalCauseAttributeThinTID': self.AvalCauseAttributeThinTID,
                        'AvalCauseAttributeCrystalName': self.AvalCauseAttributeCrystalName,
                        'AvalCauseAttributeLightName': self.AvalCauseAttributeLightName,
                        'AvalCauseAttributeSoftName': self.AvalCauseAttributeSoftName,
                        'AvalCauseAttributeThinName': self.AvalCauseAttributeThinName,
                        'AvalCauseDepthName': self.AvalCauseDepthName,
                        'AvalCauseName': self.AvalCauseName,
                        'AvalCauseTID': self.AvalCauseTID,
                        'AvalTriggerSimpleName': self.AvalTriggerSimpleName,
                        'AvalProbabilityName': self.AvalancheProbabilityName,
                        'DestructiveSizeName': self.DestructiveSizeName,
                        'AvalPropagationName': self.AvalPropagationName,
                        'ValidExposition': self.ValidExposition,
                        'ExposedHeight1': self.ExposedHeight1,
                        'ExposedHeight2': self.ExposedHeight2,
                        'ExposedHeightComboTID': self.ExposedHeightComboTID,
                        'AvalancheExtName': self.AvalancheExtName,
                        'AvalancheExtTID': self.AvalancheExtTID,
                        'Comment': self.Comment
                        }

        _dict = {**_dict_common, **_dict_unique}

        return _dict


class SnowProfilePicture(Registration, Location, Observer, Pictures):
    def __init__(self, d):
        Registration.__init__(self, d)
        Location.__init__(self, d)
        Observer.__init__(self, d)

        self.RegistrationTID = 23
        self.RegistrationName, self.Summary = _look_up_name_and_summary(self.RegistrationTID, d['Summaries'])

        Pictures.__init__(self, d, self.RegistrationTID)

        self.PictureID = d['FullObject']['PictureID']
        self.Photographer = d['FullObject']['Photographer']
        self.Copyright = d['FullObject']['Copyright']
        self.RegistrationTID = d['FullObject']['RegistrationTID']
        self.RegistrationName = d['FullObject']['RegistrationTName']
        # self.PictureComment = d['FullObject']['PictureComment']
        self.Comment = d['FullObject']['Comment']
        self.LangKey = d['LangKey']


class SnowTempLayer:
    def __init__(self, l):
        self.Depth = l['Depth']
        self.SnowTemp = l['SnowTemp']


class StratProfileLayer:
    def __init__(self, l):
        self.DepthTop = l['DepthTop']
        self.Thickness = l['Thickness']
        self.GrainFormPrimaryTID = l['GrainFormPrimaryTID']
        self.GrainFormPrimaryName = l['GrainFormPrimaryTName']
        self.GrainFormSecondaryTID = l['GrainFormSecondaryTID']
        self.GrainFormSecondaryName = l['GrainFormSecondaryTName']

        if l['GrainSizeAvg']:
            self.GrainSizeAvg = l['GrainSizeAvg'] / 10  # error in api
        else:
            self.GrainSizeAvg = None

        if l['GrainSizeAvgMax']:
            self.GrainSizeAvgMax = l['GrainSizeAvgMax'] / 10  # error in api
        else:
            self.GrainSizeAvgMax = None

        self.HardnessTID = l['HardnessTID']
        self.HardnessName = l['HardnessTName']
        self.HardnessBottomTID = l['HardnessBottomTID']
        self.HardnessBottomName = l['HardnessBottomTName']
        self.WetnessTID = l['WetnessTID']
        self.WetnessName = l['WetnessTName']
        self.CriticalLayerTID = l['CriticalLayerTID']
        self.CriticalLayerName = l['CriticalLayerTName']
        self.Comment = l['Comment']
        self.SortOrder = l['SortOrder']


class SnowDensity:
    def __init__(self, d):
        self.CylinderDiameter = d['CylinderDiameter']
        self.TareWeight = d['TareWeight']
        self.Comment = d['Comment']

        self.Layers = []
        for l in d['Layers']:
            layer = SnowDensityLayer(l)
            self.Layers.append(layer)


class SnowDensityLayer:
    def __init__(self, l):
        self.DensityProfileLayerID = l['DensityProfileLayerID']
        self.Depth = l['Depth']
        self.Thickness = l['Thickness']
        self.Density = l['Density']
        self.Comment = l['Comment']
        self.Weight = l['Weight']
        # self.WaterEquivalent = self.Density * self.Thickness
        self.WaterEquivalent = l['WaterEquivalent']


class SnowProfile(Registration, Location, Observer, Pictures):
    def __init__(self, d):

        Registration.__init__(self, d)
        Location.__init__(self, d)
        Observer.__init__(self, d)

        self.RegistrationTID = 36
        self.RegistrationName, self.Summary = _look_up_name_and_summary(self.RegistrationTID, d['Summaries'])

        Pictures.__init__(self, d, self.RegistrationTID)

        if d['SnowProfile2']:
            self.TotalDepth = d['SnowProfile2']['TotalDepth']
            self.AttachmentID = d['SnowProfile2']['AttachmentID']
            self.Comment = d['SnowProfile2']['Comment']

            self.StratProfile = []
            if d['SnowProfile2']['StratProfile']:
                for sp in d['SnowProfile2']['StratProfile']['Layers']:
                    layer = StratProfileLayer(sp)
                    self.StratProfile.append(layer)

            self.SnowTemp = []
            if d['SnowProfile2']['SnowTemp']:
                for st in d['SnowProfile2']['SnowTemp']['Layers']:
                    layer = SnowTempLayer(st)
                    self.SnowTemp.append(layer)

            self.SnowDensities = []
            for sd in d['SnowProfile2']['SnowDensity']:
                snow_density = SnowDensity(sd)
                self.SnowDensities.append(snow_density)

            self.ColumnTests = []
            for ct in d['SnowProfile2']['CompressionTest']:
                column_test = ProfileColumnTest(ct)
                self.ColumnTests.append(column_test)

            # Before this form was added in des 2018, profiles were added as images with RegistrationTID = 23
            self.PictureOfTID23 = 0
            for p in self.Pictures:
                if p.RegistrationTID == 23:
                    self.PictureOfTID23 += 1

        else:
            self.TotalDepth = None
            self.AttachmentID = None
            self.Comment = None
            self.StratProfile = []
            self.SnowTemp = []
            self.SnowDensities = []
            self.ColumnTests = []
            self.PictureOfTID23 = None

        self.LangKey = d['LangKey']

    def to_dict(self):
        """Convert the object to a dictionary.

        :return: dictionary representation of the SnowProfile class
        """

        _dict_common = _make_common_dict(self)

        _dict_unique = {'TotalDepth': self.TotalDepth,
                        'AttachmentID': self.AttachmentID,
                        'Comment': self.Comment,
                        'StratProfile': len(self.StratProfile),
                        'SnowTemp': len(self.SnowTemp),
                        'SnowDensities': len(self.SnowDensities),
                        'ColumnTests': len(self.ColumnTests),
                        'ProfilePicturesOfTID23': self.PictureOfTID23
                        }

        _dict = {**_dict_common, **_dict_unique}

        return _dict


class IceThicknessLayer:
    def __init__(self, l):
        self.IceLayerID = l['IceLayerID']
        self.IceLayerTID = l['IceLayerTID']
        self.IceLayerName = l['IceLayerName']
        self.IceLayerThickness = l['IceLayerThickness']


class IceThickness(Registration, Location, Observer, Pictures):
    def __init__(self, d):
        Registration.__init__(self, d)
        Location.__init__(self, d)
        Observer.__init__(self, d)

        self.RegistrationTID = 50
        self.RegistrationName, self.Summary = _look_up_name_and_summary(self.RegistrationTID, d['Summaries'])

        Pictures.__init__(self, d, self.RegistrationTID)

        if d['IceThickness']:
            self.SnowDepth = d['IceThickness']['SnowDepth']
            self.SlushSnow = d['IceThickness']['SlushSnow']
            self.SlushSnow = d['IceThickness']['IceThicknessSum']
            self.IceHeightBefore = d['IceThickness']['IceHeightBefore']
            self.IceHeightAfter = d['IceThickness']['IceHeightAfter']
            self.Comment = d['IceThickness']['Comment']

            self.IceThicknessLayers = []
            for l in d['IceThickness']['IceThicknessLayers']:
                layer = IceThicknessLayer(l)
                self.IceThicknessLayers.append(layer)
        else:
            self.SnowDepth = None
            self.SlushSnow = None
            self.SlushSnow = None
            self.IceHeightBefore = None
            self.IceHeightAfter = None
            self.Comment = None

            self.IceThicknessLayers = []
            for l in d['IceThickness']['IceThicknessLayers']:
                layer = IceThicknessLayer(l)
                self.IceThicknessLayers.append(layer)

        self.LangKey = d['LangKey']

    def to_dict(self):
        """Convert the object to a dictionary.

        :return: dictionary representation of the IceThickness class
        """

        _dict_common = _make_common_dict(self)

        _dict_unique = {'SnowDepth': self.SnowDepth,
                        'SlushSnow': self.SlushSnow,
                        'IceThicknessSum': self.SlushSnow,
                        'IceHeightBefore': self.IceHeightBefore,
                        'IceHeightAfter': self.IceHeightAfter,
                        'Comment': self.Comment,
                        'Layers': len(self.IceThicknessLayers)
                        }

        _dict = {**_dict_common, **_dict_unique}

        return _dict


class IceCover(Registration, Location, Observer, Pictures):

    def __init__(self, d):
        Registration.__init__(self, d)
        Location.__init__(self, d)
        Observer.__init__(self, d)

        self.RegistrationTID = 51
        self.RegistrationName, self.Summary = _look_up_name_and_summary(self.RegistrationTID, d['Summaries'])

        Pictures.__init__(self, d, self.RegistrationTID)

        if d['IceCoverObs']:
            self.IceCoverBeforeTID = d['IceCoverObs']['IceCoverBeforeTID']
            self.IceCoverBeforeName = d['IceCoverObs']['IceCoverBeforeName']
            self.IceCoverTID = d['IceCoverObs']['IceCoverTID']
            self.IceCoverName = d['IceCoverObs']['IceCoverName']
            self.IceCoverAfterTID = d['IceCoverObs']['IceCoverAfterTID']
            self.IceCoverAfterName = d['IceCoverObs']['IceCoverAfterName']
            self.IceSkateabilityTID = d['IceCoverObs']['IceSkateabilityTID']
            self.IceSkateabilityName = d['IceCoverObs']['IceSkateabilityName']
            self.IceCapacityTID = d['IceCoverObs']['IceCapacityTID']
            self.IceCapacityName = d['IceCoverObs']['IceCapacityName']
            self.Comment = d['IceCoverObs']['Comment']
        else:
            self.IceCoverBeforeTID = None
            self.IceCoverBeforeName = None
            self.IceCoverTID = None
            self.IceCoverName = None
            self.IceCoverAfterTID = None
            self.IceCoverAfterName = None
            self.IceSkateabilityTID = None
            self.IceSkateabilityName = None
            self.IceCapacityTID = None
            self.IceCapacityName = None
            self.Comment = None
        self.LangKey = d['LangKey']

    def to_dict(self):
        """Convert the object to a dictionary.

        :return: dictionary representation of the IceCover class
        """

        _dict_common = _make_common_dict(self)

        _dict_unique = {'IceCoverBeforeTID': self.IceCoverBeforeTID,
                        'IceCoverBeforeName': self.IceCoverBeforeName,
                        'IceCoverTID': self.IceCoverTID,
                        'IceCoverName': self.IceCoverName,
                        'IceCoverAfterTID': self.IceCoverAfterTID,
                        'IceCoverAfterName': self.IceCoverAfterName,
                        'IceSkateabilityTID': self.IceSkateabilityTID,
                        'IceSkateabilityName': self.IceSkateabilityName,
                        'IceCapacityTID': self.IceCapacityTID,
                        'IceCapacityName': self.IceCapacityName,
                        'Comment': self.Comment
                        }

        _dict = {**_dict_common, **_dict_unique}

        return _dict


class WaterLevel(Registration, Location, Observer, Pictures):
    def __init__(self, d):
        Registration.__init__(self, d)
        Location.__init__(self, d)
        Observer.__init__(self, d)

        self.RegistrationTID = 61
        self.RegistrationName, self.Summary = _look_up_name_and_summary(self.RegistrationTID, d['Summaries'])

        Pictures.__init__(self, d, self.RegistrationTID)

        if d['WaterLevel']:
            self.WaterLevelDescribed = d['WaterLevel']['WaterLevelDescribed']
            self.WaterLevelValue = d['WaterLevel']['WaterLevelValue']
            self.WaterLevelRefTID = d['WaterLevel']['WaterLevelRefTID']
            self.WaterLevelRefName = d['WaterLevel']['WaterLevelRefName']
            self.Comment = d['WaterLevel']['Comment']
            self.MeasuredDischarge = d['WaterLevel']['MeasuredDischarge']
        else:
            self.WaterLevelDescribed = None
            self.WaterLevelValue = None
            self.WaterLevelRefTID = None
            self.WaterLevelRefName = None
            self.Comment = None
            self.MeasuredDischarge = None

        self.LangKey = d['LangKey']

    def to_dict(self):
        """Convert the object to a dictionary.

        :return: dictionary representation of the WaterLevel class
        """

        _dict_common = _make_common_dict(self)

        _dict_unique = {'WaterLevelDescribed': self.WaterLevelDescribed,
                        'WaterLevelValue': self.WaterLevelValue,
                        'WaterLevelRefTID': self.WaterLevelRefTID,
                        'WaterLevelRefName': self.WaterLevelRefName,
                        'Comment': self.Comment,
                        'MeasuredDischarge': self.MeasuredDischarge,
                        }

        _dict = {**_dict_common, **_dict_unique}

        return _dict


class WaterLevelMeasurement:
    def __init__(self, m):
        self.WaterLevelMeasurementId = m['WaterLevelMeasurementId']
        self.WaterLevelValue = m['WaterLevelValue']
        self.DtMeasurementTime = m['DtMeasurementTime']
        self.Comment = m['Comment']
        self.Pictures = m['Attachments']


class WaterLevel2(Registration, Location, Observer):
    def __init__(self, d):
        Registration.__init__(self, d)
        Location.__init__(self, d)
        Observer.__init__(self, d)

        self.RegistrationTID = 62
        self.RegistrationName, self.Summary = _look_up_name_and_summary(self.RegistrationTID, d['Summaries'])

        if d['WaterLevel2']:
            self.WaterLevelStateTID = d['WaterLevel2']['WaterLevelStateTID']
            self.WaterLevelStateName = d['WaterLevel2']['WaterLevelStateName']
            self.WaterAstrayTID = d['WaterLevel2']['WaterAstrayTID']
            self.WaterAstrayName = d['WaterLevel2']['WaterAstrayName']
            self.ObservationTimingTID = d['WaterLevel2']['ObservationTimingTID']
            self.ObservationTimingName = d['WaterLevel2']['ObservationTimingName']
            self.MeasurementReferenceTID = d['WaterLevel2']['MeasurementReferenceTID']
            self.MeasurementReferenceName = d['WaterLevel2']['MeasurementReferenceName']
            self.MeasurementTypeTID = d['WaterLevel2']['MeasurementTypeTID']
            self.MeasurementTypeName = d['WaterLevel2']['MeasurementTypeName']
            self.WaterLevelMethodTID = d['WaterLevel2']['WaterLevelMethodTID']
            self.WaterLevelMethodName = d['WaterLevel2']['WaterLevelMethodName']
            self.MarkingReferenceTID = d['WaterLevel2']['MarkingReferenceTID']
            self.MarkingReferenceName = d['WaterLevel2']['MarkingReferenceName']
            self.MarkingTypeTID = d['WaterLevel2']['MarkingTypeTID']
            self.MarkingTypeName = d['WaterLevel2']['MarkingTypeName']
            self.MeasuringToolDescription = d['WaterLevel2']['MeasuringToolDescription']

            self.WaterLevelMeasurements = []
            for m in d['WaterLevel2']['WaterLevelMeasurement']:
                self.WaterLevelMeasurements.append(WaterLevelMeasurement(m))

        else:
            self.WaterLevelStateTID = None
            self.WaterLevelStateName = None
            self.WaterAstrayTID = None
            self.WaterAstrayName = None
            self.ObservationTimingTID = None
            self.ObservationTimingName = None
            self.MeasurementReferenceTID = None
            self.MeasurementReferenceName = None
            self.MeasurementTypeTID = None
            self.MeasurementTypeName = None
            self.WaterLevelMethodTID = None
            self.WaterLevelMethodName = None
            self.MarkingReferenceTID = None
            self.MarkingReferenceName = None
            self.MarkingTypeTID = None
            self.MarkingTypeName = None
            self.MeasuringToolDescription = None
            self.WaterLevelMeasurements = []

        self.LangKey = d['LangKey']

    def to_dict(self):
        """Convert the object to a dictionary.

        :return: dictionary representation of the WaterLevel2 class
        """

        _dict_common = _make_common_dict(self)

        _dict_unique = {'WaterLevelStateTID': self.WaterLevelStateTID,
                        'WaterLevelStateName': self.WaterLevelStateName,
                        'WaterAstrayTID': self.WaterAstrayTID,
                        'WaterAstrayName': self.WaterAstrayName,
                        'ObservationTimingTID': self.ObservationTimingTID,
                        'ObservationTimingName': self.ObservationTimingName,
                        'MeasurementReferenceTID': self.MeasurementReferenceTID,
                        'MeasurementReferenceName': self.MeasurementReferenceName,
                        'MeasurementTypeTID': self.MeasurementTypeTID,
                        'MeasurementTypeName': self.MeasurementTypeName,
                        'WaterLevelMethodTID': self.WaterLevelMethodTID,
                        'WaterLevelMethodName': self.WaterLevelMethodName,
                        'MarkingReferenceTID': self.MarkingReferenceTID,
                        'MarkingReferenceName': self.MarkingReferenceName,
                        'MarkingTypeTID': self.MarkingTypeTID,
                        'MarkingTypeName': self.MarkingTypeName,
                        'MeasuringToolDescription': self.MeasuringToolDescription,
                        'WaterLevelMeasurements': len(self.WaterLevelMeasurements)
                        }

        _dict = {**_dict_common, **_dict_unique}

        return _dict


class LandSlideObs(Registration, Location, Observer, Pictures):
    def __init__(self, d):
        Registration.__init__(self, d)
        Location.__init__(self, d)
        Observer.__init__(self, d)

        self.RegistrationTID = 71
        self.RegistrationName, self.Summary = _look_up_name_and_summary(self.RegistrationTID, d['Summaries'])

        Pictures.__init__(self, d, self.RegistrationTID)

        if d['LandSlideObs']:
            self.DtLandSlideTime = _stringtime_2_datetime(d['LandSlideObs']['DtLandSlideTime'])
            self.DtLandSlideTimeEnd = _stringtime_2_datetime(d['LandSlideObs']['DtLandSlideTimeEnd'])
            self.UTMNorthStop = d['LandSlideObs']['UTMNorthStop']
            self.UTMEastStop = d['LandSlideObs']['UTMEastStop']
            self.UTMZoneStop = d['LandSlideObs']['UTMZoneStop']
            self.LandSlideTID = d['LandSlideObs']['LandSlideTID']
            self.LandSlideName = d['LandSlideObs']['LandSlideName']
            self.LandSlideTriggerTID = d['LandSlideObs']['LandSlideTriggerTID']
            self.LandSlideTriggerName = d['LandSlideObs']['LandSlideTriggerName']
            self.LandSlideSizeTID = d['LandSlideObs']['LandSlideSizeTID']
            self.LandSlideSizeName = d['LandSlideObs']['LandSlideSizeName']
            self.ActivityInfluencedTID = d['LandSlideObs']['ActivityInfluencedTID']
            self.ActivityInfluencedName = d['LandSlideObs']['ActivityInfluencedName']
            self.ForecastAccurateTID = d['LandSlideObs']['ForecastAccurateTID']
            self.ForecastAccurateName = d['LandSlideObs']['ForecastAccurateName']
            self.DamageExtentTID = d['LandSlideObs']['DamageExtentTID']
            self.DamageExtentName = d['LandSlideObs']['DamageExtentName']
            self.UTMZoneStart = d['LandSlideObs']['UTMZoneStart']
            self.UTMNorthStart = d['LandSlideObs']['UTMNorthStart']
            self.UTMEastStart = d['LandSlideObs']['UTMEastStart']
            self.Comment = d['LandSlideObs']['Comment']

            self.URLs = []
            for u in d['LandSlideObs']['Urls']:
                self.URLs.append({'URLLine': u['UrlLine'], 'URLDescription': u['UrlDescription']})

        else:
            self.DtLandSlideTime = None
            self.DtLandSlideTimeEnd = None
            self.UTMNorthStop = None
            self.UTMEastStop = None
            self.UTMZoneStop = None
            self.LandSlideTID = None
            self.LandSlideName = None
            self.LandSlideTriggerTID = None
            self.LandSlideTriggerName = None
            self.LandSlideSizeTID = None
            self.LandSlideSizeName = None
            self.ActivityInfluencedTID = None
            self.ActivityInfluencedName = None
            self.ForecastAccurateTID = None
            self.ForecastAccurateName = None
            self.DamageExtentTID = None
            self.DamageExtentName = None
            self.UTMZoneStart = None
            self.UTMNorthStart = None
            self.UTMEastStart = None
            self.Comment = None
            self.URLs = []

        self.LangKey = d['LangKey']

    def to_dict(self):
        """Convert the object to a dictionary.

        :return: dictionary representation of the LandSlideObs class
        """

        _dict_common = _make_common_dict(self)

        _dict_unique = {'DtLandSlideTime': self.DtLandSlideTime,
                        'DtLandSlideTimeEnd': self.DtLandSlideTimeEnd,
                        'UTMNorthStop': self.UTMNorthStop,
                        'UTMEastStop': self.UTMEastStop,
                        'UTMZoneStop': self.UTMZoneStop,
                        'LandSlideTID': self.LandSlideTID,
                        'LandSlideName': self.LandSlideName,
                        'LandSlideTriggerTID': self.LandSlideTriggerTID,
                        'LandSlideTriggerName': self.LandSlideTriggerName,
                        'LandSlideSizeTID': self.LandSlideSizeTID,
                        'LandSlideSizeName': self.LandSlideSizeName,
                        'ActivityInfluencedTID': self.ActivityInfluencedTID,
                        'ActivityInfluencedName': self.ActivityInfluencedName,
                        'ForecastAccurateTID': self.ForecastAccurateTID,
                        'ForecastAccurateName': self.ForecastAccurateName,
                        'DamageExtentTID': self.DamageExtentTID,
                        'DamageExtentName': self.DamageExtentName,
                        'UTMZoneStart': self.UTMZoneStart,
                        'UTMNorthStart': self.UTMNorthStart,
                        'UTMEastStart': self.UTMEastStart,
                        'Comment': self.Comment,
                        'URLs': f'{len(self.URLs)} on observation'
                        }

        _dict = {**_dict_common, **_dict_unique}

        return _dict


class PictureObservation(Registration, Location, Observer, Picture):

    def __init__(self, d):
        Registration.__init__(self, d)
        Location.__init__(self, d)
        Observer.__init__(self, d)
        Picture.__init__(self, d)

        self.LangKey = d['LangKey']


def _get_general(registration_type, from_date, to_date, region_ids=None, location_id=None,
                 countries=None, time_zone=None, observer_ids=None, observer_nick=None, observer_competence=None,
                 group_id=None, output='List', geohazard_tids=None, lang_key=1):
    """Gets observations of one requested type and maps them to one requested class.

    :param registration_type:   [int] RegistrationTID for the requested observation type
    :param from_date:           [date] A query returns [from_date, to_date]
    :param to_date:             [date] A query returns [from_date, to_date]
    :param region_ids:          [int or list of ints] If region_ids = None, all regions are selected
    :param observer_ids:        [int or list of ints] If observer_ids = None, all observers are selected
    :param observer_nick:       [int or list of ints] Default None gives all.
    :param observer_competence: [string] Part of a observer nick name
    :param group_id:            [int]
    :param output:              [string] Options: 'List', 'DataFrame' and 'Count'. Default 'List'.
    :param geohazard_tids       [int or list of ints] 10 is snow, 20,30,40 are dirt, 60 is water and 70 is ice
    :param lang_key             [int] 1 is norwegian, 2 is english

    :return:
    """

    obs_list = None
    if output not in ['List', 'DataFrame', 'Count']:
        lg.warning("getobservations.py -> _get_general: Illegal output option.")
        return obs_list

    if output == 'Count':
        total_matches = get_count(from_date=from_date, to_date=to_date, region_ids=region_ids,
                                  observer_ids=observer_ids, observer_nick=observer_nick,
                                  observer_competence=observer_competence, group_id=group_id, location_id=location_id,
                                  countries=countries, time_zone=time_zone, lang_key=lang_key,
                                  registration_types=registration_type, geohazard_tids=geohazard_tids)
        return total_matches

    else:
        data = get_data(from_date=from_date, to_date=to_date, region_ids=region_ids, observer_ids=observer_ids,
                        observer_nick=observer_nick, observer_competence=observer_competence, group_id=group_id,
                        location_id=location_id, countries=countries, time_zone=time_zone, lang_key=lang_key,
                        registration_types=registration_type, geohazard_tids=geohazard_tids)

        if output == 'List' or output == 'DataFrame':
            obs_list = []
            for d in data:
                obs_list += _get_object(registration_type, d)
            obs_list = sorted(obs_list, key=lambda registration_class_type: registration_class_type.DtObsTime)

        if output == 'List':
            return obs_list

        if output == 'DataFrame':
            list_of_dict = [d.to_dict() for d in obs_list]
            return pd.DataFrame(list_of_dict)


def get_general_observation(from_date, to_date, region_ids=None, location_id=None, countries=None, time_zone=None,
                            group_id=None, observer_ids=None, observer_nick=None, observer_competence=None,
                            output='List', geohazard_tids=None, lang_key=1):
    """Gets observations like given in GeneralObs table with RegistrationTID = 10.
    View is shared by all the geo hazards so the filter includes geohazard_tid if only some geohazards are needed.

    :param from_date:           [date] A query returns [from_date, to_date]
    :param to_date:             [date] A query returns [from_date, to_date]
    :param region_ids:          [int or list of ints] If region_ids = None, all regions are selected
    :param location_id:         [int] LocationID as given in the ObsLocation table in regObs.
    :param countries:           [int or list of ints] If countries = None, all regions are selected.
    :param time_zone:           [string] Desired timezone representation in summaries. None returns server local time.
    :param group_id:            [int] ObserverGroupID as given in the ObserverGroup table in regObs.
    :param observer_ids:        [int or list of ints] If observer_ids = None, all observers are selected
    :param observer_nick:       [int or list of ints] Default None gives all.
    :param observer_competence: [string] Part of a observer nick name
    :param output:              [string] Options: 'List', 'DataFrame' and 'Count'. Default 'List'.
    :param geohazard_tids:      [int or list of ints] Default None gives all.
    :param lang_key             [int] 1 is norwegian, 2 is english

    :return:
    """

    return _get_general(10, from_date=from_date, to_date=to_date,
                        region_ids=region_ids, location_id=location_id, countries=countries, time_zone=time_zone,
                        group_id=group_id, observer_ids=observer_ids, observer_nick=observer_nick,
                        observer_competence=observer_competence, output=output, geohazard_tids=geohazard_tids,
                        lang_key=lang_key)


def get_incident(from_date, to_date, region_ids=None, location_id=None, countries=None, time_zone=None, group_id=None,
                 observer_ids=None, observer_nick=None, observer_competence=None, output='List', geohazard_tids=None,
                 lang_key=1):
    """Gets observations like given the Incident table with RegistrationTID = 11.
    Table is shared by all the geohazards so the filter includes geohazard_tid if only some geohazards are needed.

    :param from_date:           [date] A query returns [from_date, to_date]
    :param to_date:             [date] A query returns [from_date, to_date]
    :param region_ids:          [int or list of ints] If region_ids = None, all regions are selected
    :param location_id:         [int] LocationID as given in the ObsLocation table in regObs.
    :param countries:           [int or list of ints] If countries = None, all regions are selected.
    :param time_zone:           [string] Desired timezone representation in summaries. None returns server local time.
    :param group_id:            [int] ObserverGroupID as given in the ObserverGroup table in regObs.
    :param observer_ids:        [int or list of ints] If observer_ids = None, all observers are selected
    :param observer_nick:       [int or list of ints] Default None gives all.
    :param observer_competence: [string] Part of a observer nick name
    :param output:              [string] Options: 'List', 'DataFrame' and 'Count'. Default 'List'.
    :param geohazard_tids:      [int or list of ints] Default None gives all.
    :param lang_key             [int] 1 is norwegian, 2 is english

    :return:
    """

    return _get_general(11, from_date=from_date, to_date=to_date,
                        region_ids=region_ids, location_id=location_id, countries=countries, time_zone=time_zone,
                        group_id=group_id, observer_ids=observer_ids, observer_nick=observer_nick,
                        observer_competence=observer_competence, output=output, geohazard_tids=geohazard_tids,
                        lang_key=lang_key)


def get_danger_sign(from_date, to_date, region_ids=None, location_id=None, countries=None, time_zone=None,
                    group_id=None, observer_ids=None, observer_nick=None, observer_competence=None,
                    output='List', geohazard_tids=None, lang_key=1):
    """Gets observations like given in DangerObsV table with RegistrationTID = 13.
    View is shared by all the geohazards so the filter includes geohazard_tid if only some geohazards are needed.

    :param from_date:           [date] A query returns [from_date, to_date]
    :param to_date:             [date] A query returns [from_date, to_date]
    :param region_ids:          [int or list of ints] If region_ids = None, all regions are selected
    :param location_id:         [int] LocationID as given in the ObsLocation table in regObs.
    :param countries:           [int or list of ints] If countries = None, all regions are selected.
    :param time_zone:           [string] Desired timezone representation in summaries. None returns server local time.
    :param group_id:            [int] ObserverGroupID as given in the ObserverGroup table in regObs.
    :param observer_ids:        [int or list of ints] If observer_ids = None, all observers are selected
    :param observer_nick:       [int or list of ints] Default None gives all.
    :param observer_competence: [string] Part of a observer nick name
    :param output:              [string] Options: 'List', 'DataFrame' and 'Count'. Default 'List'.
    :param geohazard_tids:      [int or list of ints] Default None gives all.
    :param lang_key             [int] 1 is norwegian, 2 is english

    :return:
    """

    return _get_general(13, from_date=from_date, to_date=to_date,
                        region_ids=region_ids, location_id=location_id, countries=countries, time_zone=time_zone,
                        group_id=group_id, observer_ids=observer_ids, observer_nick=observer_nick,
                        observer_competence=observer_competence, output=output, geohazard_tids=geohazard_tids,
                        lang_key=lang_key)


def get_damage_observation(from_date, to_date, region_ids=None, location_id=None, countries=None, time_zone=None,
                           group_id=None, observer_ids=None, observer_nick=None, observer_competence=None,
                           output='List', geohazard_tids=None, lang_key=1):
    """Gets observations like given in SnowSurfaceObservation table with RegistrationTID = 22.
    View is shared by all the geohazards so the filter includes geohazard_tid if only some geohazards are needed.

    :param from_date:           [date] A query returns [from_date, to_date]
    :param to_date:             [date] A query returns [from_date, to_date]
    :param region_ids:          [int or list of ints] If region_ids = None, all regions are selected
    :param location_id:         [int] LocationID as given in the ObsLocation table in regObs.
    :param countries:           [int or list of ints] If countries = None, all regions are selected.
    :param time_zone:           [string] Desired timezone representation in summaries. None returns server local time.
    :param group_id:            [int] ObserverGroupID as given in the ObserverGroup table in regObs.
    :param observer_ids:        [int or list of ints] If observer_ids = None, all observers are selected
    :param observer_nick:       [int or list of ints] Default None gives all.
    :param observer_competence: [string] Part of a observer nick name
    :param output:              [string] Options: 'List', 'DataFrame' and 'Count'. Default 'List'.
    :param geohazard_tids:      [int or list of ints] Default None gives all.
    :param lang_key             [int] 1 is norwegian, 2 is english

    :return:
    """

    return _get_general(14, from_date=from_date, to_date=to_date, region_ids=region_ids, location_id=location_id,
                        countries=countries, time_zone=time_zone, group_id=group_id, observer_ids=observer_ids,
                        observer_nick=observer_nick, observer_competence=observer_competence, output=output,
                        geohazard_tids=geohazard_tids, lang_key=lang_key)


def get_weather_observation(from_date, to_date, region_ids=None, location_id=None, countries=None, time_zone=None,
                            group_id=None, observer_ids=None, observer_nick=None, observer_competence=None,
                            output='List', lang_key=1):
    """Gets observations like given in WeatherObservation table with RegistrationTID = 21.
    View is used by GeoHazard = 10 (snow).

    :param from_date:           [date] A query returns [from_date, to_date]
    :param to_date:             [date] A query returns [from_date, to_date]
    :param region_ids:          [int or list of ints] If region_ids = None, all regions are selected
    :param location_id:         [int] LocationID as given in the ObsLocation table in regObs.
    :param countries:           [int or list of ints] If countries = None, all regions are selected.
    :param time_zone:           [string] Desired timezone representation in summaries. None returns server local time.
    :param group_id:            [int] ObserverGroupID as given in the ObserverGroup table in regObs.
    :param observer_ids:        [int or list of ints] If observer_ids = None, all observers are selected
    :param observer_nick:       [int or list of ints] Default None gives all.
    :param observer_competence: [string] Part of a observer nick name
    :param output:              [string] Options: 'List', 'DataFrame' and 'Count'. Default 'List'.
    :param lang_key             [int] 1 is norwegian, 2 is english

    :return:
    """

    return _get_general(21, from_date=from_date, to_date=to_date, region_ids=region_ids, location_id=location_id,
                        countries=countries, time_zone=time_zone, group_id=group_id, observer_ids=observer_ids,
                        observer_nick=observer_nick, observer_competence=observer_competence, output=output,
                        geohazard_tids=10, lang_key=lang_key)


def get_snow_surface_observation(from_date, to_date, region_ids=None, location_id=None, countries=None, time_zone=None,
                                 group_id=None, observer_ids=None, observer_nick=None, observer_competence=None,
                                 output='List', lang_key=1):
    """Gets observations like given in SnowSurfaceObservation table with RegistrationTID = 22.
    View is used by GeoHazard = 10 (snow).

    :param from_date:           [date] A query returns [from_date, to_date]
    :param to_date:             [date] A query returns [from_date, to_date]
    :param region_ids:          [int or list of ints] If region_ids = None, all regions are selected
    :param location_id:         [int] LocationID as given in the ObsLocation table in regObs.
    :param countries:           [int or list of ints] If countries = None, all regions are selected.
    :param time_zone:           [string] Desired timezone representation in summaries. None returns server local time.
    :param group_id:            [int] ObserverGroupID as given in the ObserverGroup table in regObs.
    :param observer_ids:        [int or list of ints] If observer_ids = None, all observers are selected
    :param observer_nick:       [int or list of ints] Default None gives all.
    :param observer_competence: [string] Part of a observer nick name
    :param output:              [string] Options: 'List', 'DataFrame' and 'Count'. Default 'List'.
    :param lang_key             [int] 1 is norwegian, 2 is english

    :return:
    """

    return _get_general(22, from_date=from_date, to_date=to_date, region_ids=region_ids, location_id=location_id,
                        countries=countries, time_zone=time_zone, group_id=group_id, observer_ids=observer_ids,
                        observer_nick=observer_nick, observer_competence=observer_competence, output=output,
                        geohazard_tids=10, lang_key=lang_key)


def get_tests(from_date, to_date, region_ids=None, location_id=None, countries=None, time_zone=None,
              group_id=None, observer_ids=None, observer_nick=None, observer_competence=None,
              output='List', lang_key=1):
    """Gets observations of tests done in a snow pit.

    :param from_date:           [date] A query returns [from_date, to_date]
    :param to_date:             [date] A query returns [from_date, to_date]
    :param region_ids:          [int or list of ints] If region_ids = None, all regions are selected
    :param location_id:         [int] LocationID as given in the ObsLocation table in regObs.
    :param countries:           [int or list of ints] If countries = None, all regions are selected.
    :param time_zone:           [string] Desired timezone representation in summaries. None returns server local time.
    :param group_id:            [int] ObserverGroupID as given in the ObserverGroup table in regObs.
    :param observer_ids:        [int or list of ints] If observer_ids = None, all observers are selected
    :param observer_nick:       [int or list of ints] Default None gives all.
    :param observer_competence: [string] Part of a observer nick name
    :param output:              [string] Options: 'List', 'DataFrame' and 'Count'. Default 'List'.
    :param lang_key             [int] 1 is norwegian, 2 is english

    :return:
    """

    return _get_general(25, from_date=from_date, to_date=to_date, region_ids=region_ids, location_id=location_id,
                        countries=countries, time_zone=time_zone, group_id=group_id, observer_ids=observer_ids,
                        observer_nick=observer_nick, observer_competence=observer_competence, output=output,
                        lang_key=lang_key)


def get_avalanche(from_date, to_date, region_ids=None, location_id=None, countries=None, time_zone=None,
                  group_id=None, observer_ids=None, observer_nick=None, observer_competence=None,
                  output='List', lang_key=1):
    """Gets observations as given in the AvalancheObs table with RegistrationTID = 26.
    These are observations of single avalanches, often related to incidents. It is specific for snow observations.

    :param from_date:           [date] A query returns [from_date, to_date]
    :param to_date:             [date] A query returns [from_date, to_date]
    :param region_ids:          [int or list of ints] If region_ids = None, all regions are selected
    :param location_id:         [int] LocationID as given in the ObsLocation table in regObs.
    :param countries:           [int or list of ints] If countries = None, all regions are selected.
    :param time_zone:           [string] Desired timezone representation in summaries. None returns server local time.
    :param group_id:            [int] ObserverGroupID as given in the ObserverGroup table in regObs.
    :param observer_ids:        [int or list of ints] If observer_ids = None, all observers are selected
    :param observer_nick:       [int or list of ints] Default None gives all.
    :param observer_competence: [string] Part of a observer nick name
    :param output:              [string] Options: 'List', 'DataFrame' and 'Count'. Default 'List'.
    :param lang_key             [int] 1 is norwegian, 2 is english

    :return:
    """

    return _get_general(26, from_date=from_date, to_date=to_date, region_ids=region_ids, location_id=location_id,
                        countries=countries, time_zone=time_zone, group_id=group_id, observer_ids=observer_ids,
                        observer_nick=observer_nick, observer_competence=observer_competence,
                        output=output, lang_key=lang_key)


def get_avalanche_activity(from_date, to_date, region_ids=None, location_id=None, countries=None, time_zone=None,
                           group_id=None, observer_ids=None, observer_nick=None, observer_competence=None,
                           output='List', lang_key=1):
    """Gets observations as given in AvalancheActivityObs table with RegistrationTID = 27.
    It is specific for snow observations. The table was introduced at the beginning an phased out in in january 2016.

    :param from_date:           [date] A query returns [from_date, to_date]
    :param to_date:             [date] A query returns [from_date, to_date]
    :param region_ids:          [int or list of ints] If region_ids = None, all regions are selected
    :param location_id:         [int] LocationID as given in the ObsLocation table in regObs.
    :param countries:           [int or list of ints] If countries = None, all regions are selected.
    :param time_zone:           [string] Desired timezone representation in summaries. None returns server local time.
    :param group_id:            [int] ObserverGroupID as given in the ObserverGroup table in regObs.
    :param observer_ids:        [int or list of ints] If observer_ids = None, all observers are selected
    :param observer_nick:       [int or list of ints] Default None gives all.
    :param observer_competence: [string] Part of a observer nick name
    :param output:              [string] Options: 'List', 'DataFrame' and 'Count'. Default 'List'.
    :param lang_key             [int] 1 is norwegian, 2 is english

    :return:
    """

    return _get_general(27, from_date=from_date, to_date=to_date, region_ids=region_ids, location_id=location_id,
                        countries=countries, time_zone=time_zone, group_id=group_id, observer_ids=observer_ids,
                        observer_nick=observer_nick, observer_competence=observer_competence,
                        output=output, lang_key=lang_key)


def get_avalanche_activity_2(from_date, to_date, region_ids=None, location_id=None, countries=None, time_zone=None,
                             group_id=None, observer_ids=None, observer_nick=None, observer_competence=None,
                             output='List', lang_key=1):
    """Gets observations like given in AvalancheActivityObs2 table with RegistrationTID = 33.
    It is specific for snow observations. The table was introduced in january 2016.

    :param from_date:           [date] A query returns [from_date, to_date]
    :param to_date:             [date] A query returns [from_date, to_date]
    :param region_ids:          [int or list of ints] If region_ids = None, all regions are selected
    :param location_id:         [int] LocationID as given in the ObsLocation table in regObs.
    :param countries:           [int or list of ints] If countries = None, all regions are selected.
    :param time_zone:           [string] Desired timezone representation in summaries. None returns server local time.
    :param group_id:            [int] ObserverGroupID as given in the ObserverGroup table in regObs.
    :param observer_ids:        [int or list of ints] If observer_ids = None, all observers are selected
    :param observer_nick:       [int or list of ints] Default None gives all.
    :param observer_competence: [string] Part of a observer nick name
    :param output:              [string] Options: 'List', 'DataFrame' and 'Count'. Default 'List'.
    :param lang_key             [int] 1 is norwegian, 2 is english

    :return:
    """

    return _get_general(33, from_date=from_date, to_date=to_date, region_ids=region_ids, location_id=location_id,
                        countries=countries, time_zone=time_zone, group_id=group_id, observer_ids=observer_ids,
                        observer_nick=observer_nick, observer_competence=observer_competence, output=output,
                        lang_key=lang_key)


def get_avalanche_evaluation(from_date, to_date, region_ids=None, location_id=None, countries=None, time_zone=None,
                             group_id=None, observer_ids=None, observer_nick=None, observer_competence=None,
                             output='List', lang_key=1):
    """Gets observations like given in AvalancheEvaluation table with RegistrationTID = 28.
    It contains avalanche problems. It is specific for snow observations.
    The table was used winter and spring 2012. Last observatins jan/beb 2013 by drift@svv..

    :param from_date:           [date] A query returns [from_date, to_date]
    :param to_date:             [date] A query returns [from_date, to_date]
    :param region_ids:          [int or list of ints] If region_ids = None, all regions are selected
    :param location_id:         [int] LocationID as given in the ObsLocation table in regObs.
    :param countries:           [int or list of ints] If countries = None, all regions are selected.
    :param time_zone:           [string] Desired timezone representation in summaries. None returns server local time.
    :param group_id:            [int] ObserverGroupID as given in the ObserverGroup table in regObs.
    :param observer_ids:        [int or list of ints] If observer_ids = None, all observers are selected
    :param observer_nick:       [int or list of ints] Default None gives all.
    :param observer_competence: [string] Part of a observer nick name
    :param output:              [string] Options: 'List', 'DataFrame' and 'Count'. Default 'List'.
    :param lang_key             [int] 1 is norwegian, 2 is english

    :return:
    """

    return _get_general(28, from_date=from_date, to_date=to_date, region_ids=region_ids, location_id=location_id,
                        countries=countries, time_zone=time_zone, group_id=group_id, observer_ids=observer_ids,
                        observer_nick=observer_nick, observer_competence=observer_competence, output=output,
                        lang_key=lang_key)


def get_avalanche_evaluation_2(from_date, to_date, region_ids=None, location_id=None, countries=None, time_zone=None,
                               group_id=None, observer_ids=None, observer_nick=None, observer_competence=None,
                               output='List', lang_key=1):
    """Gets observations like given in AvalancheEvaluation2 table with RegistrationTID = 30.
    It contains the avalanche problems used at the time. It is specific for snow observations.
    The table was introduced December 2012 and phased out winter 2014. It was last used May 2014.

    :param from_date:           [date] A query returns [from_date, to_date]
    :param to_date:             [date] A query returns [from_date, to_date]
    :param region_ids:          [int or list of ints] If region_ids = None, all regions are selected
    :param location_id:         [int] LocationID as given in the ObsLocation table in regObs.
    :param countries:           [int or list of ints] If countries = None, all regions are selected.
    :param time_zone:           [string] Desired timezone representation in summaries. None returns server local time.
    :param group_id:            [int] ObserverGroupID as given in the ObserverGroup table in regObs.
    :param observer_ids:        [int or list of ints] If observer_ids = None, all observers are selected
    :param observer_nick:       [int or list of ints] Default None gives all.
    :param observer_competence: [string] Part of a observer nick name
    :param output:              [string] Options: 'List', 'DataFrame' and 'Count'. Default 'List'.
    :param lang_key             [int] 1 is norwegian, 2 is english

    :return:
    """

    return _get_general(30, from_date=from_date, to_date=to_date, region_ids=region_ids, location_id=location_id,
                        countries=countries, time_zone=time_zone, group_id=group_id, observer_ids=observer_ids,
                        observer_nick=observer_nick, observer_competence=observer_competence, output=output,
                        lang_key=lang_key)


def get_avalanche_evaluation_3(from_date, to_date, region_ids=None, location_id=None, countries=None, time_zone=None,
                               group_id=None, observer_ids=None, observer_nick=None, observer_competence=None,
                               output='List', lang_key=1):
    """Gets observations like given in AvalancheEvaluation3 table with RegistrationTID = 31.
    It is specific for snow observations. The table was introduced in february 2014.

    :param from_date:           [date] A query returns [from_date, to_date]
    :param to_date:             [date] A query returns [from_date, to_date]
    :param region_ids:          [int or list of ints] If region_ids = None, all regions are selected
    :param location_id:         [int] LocationID as given in the ObsLocation table in regObs.
    :param countries:           [int or list of ints] If countries = None, all regions are selected.
    :param time_zone:           [string] Desired timezone representation in summaries. None returns server local time.
    :param group_id:            [int] ObserverGroupID as given in the ObserverGroup table in regObs.
    :param observer_ids:        [int or list of ints] If observer_ids = None, all observers are selected
    :param observer_nick:       [int or list of ints] Default None gives all.
    :param observer_competence: [string] Part of a observer nick name
    :param output:              [string] Options: 'List', 'DataFrame' and 'Count'. Default 'List'.
    :param lang_key             [int] 1 is norwegian, 2 is english

    :return:
    """

    return _get_general(31, from_date=from_date, to_date=to_date, region_ids=region_ids, location_id=location_id,
                        countries=countries, time_zone=time_zone, group_id=group_id, observer_ids=observer_ids,
                        observer_nick=observer_nick, observer_competence=observer_competence, output=output,
                        lang_key=lang_key)


def get_avalanche_problem_2(from_date, to_date, region_ids=None, location_id=None, countries=None, time_zone=None,
                            group_id=None, observer_ids=None, observer_nick=None, observer_competence=None,
                            output='List', lang_key=1):
    """Gets observations given in AvalancheEvalProblem2 table with RegistrationTID = 31.
    It is specific for snow observations. The table was introduced winter 2014 with the
    first observation was February 2014. It is currently in use (Oct 2017).

    :param from_date:           [date] A query returns [from_date, to_date]
    :param to_date:             [date] A query returns [from_date, to_date]
    :param region_ids:          [int or list of ints] If region_ids = None, all regions are selected
    :param location_id:         [int] LocationID as given in the ObsLocation table in regObs.
    :param countries:           [int or list of ints] If countries = None, all regions are selected.
    :param time_zone:           [string] Desired timezone representation in summaries. None returns server local time.
    :param group_id:            [int] ObserverGroupID as given in the ObserverGroup table in regObs.
    :param observer_ids:        [int or list of ints] If observer_ids = None, all observers are selected
    :param observer_nick:       [int or list of ints] Default None gives all.
    :param observer_competence: [string] Part of a observer nick name
    :param output:              [string] Options: 'List', 'DataFrame' and 'Count'. Default 'List'.
    :param lang_key             [int] 1 is norwegian, 2 is english

    :return:
    """

    return _get_general(32, from_date=from_date, to_date=to_date, region_ids=region_ids, location_id=location_id,
                        countries=countries, time_zone=time_zone, group_id=group_id, observer_ids=observer_ids,
                        observer_nick=observer_nick, observer_competence=observer_competence, output=output,
                        lang_key=lang_key)


def get_snow_profile(from_date, to_date, region_ids=None, location_id=None, countries=None, time_zone=None,
                     group_id=None, observer_ids=None, observer_nick=None, observer_competence=None,
                     output='List', lang_key=1):
    """Gets observations of snow profiles. Before dec 2018 these were provided as pictures.

    :param from_date:           [date] A query returns [from_date, to_date]
    :param to_date:             [date] A query returns [from_date, to_date]
    :param region_ids:          [int or list of ints] If region_ids = None, all regions are selected
    :param location_id:         [int] LocationID as given in the ObsLocation table in regObs.
    :param countries:           [int or list of ints] If countries = None, all regions are selected.
    :param time_zone:           [string] Desired timezone representation in summaries. None returns server local time.
    :param group_id:            [int] ObserverGroupID as given in the ObserverGroup table in regObs.
    :param observer_ids:        [int or list of ints] If observer_ids = None, all observers are selected
    :param observer_nick:       [int or list of ints] Default None gives all.
    :param observer_competence: [string] Part of a observer nick name
    :param output:              [string] Options: 'List', 'DataFrame' and 'Count'. Default 'List'.
    :param lang_key             [int] 1 is norwegian, 2 is english

    :return:
    """

    return _get_general(36, from_date=from_date, to_date=to_date, region_ids=region_ids, location_id=location_id,
                        countries=countries, time_zone=time_zone, group_id=group_id, observer_ids=observer_ids,
                        observer_nick=observer_nick, observer_competence=observer_competence, output=output,
                        lang_key=lang_key)


def get_ice_thickness(from_date, to_date, region_ids=None, location_id=None, countries=None, time_zone=None,
                      group_id=None, observer_ids=None, observer_nick=None, observer_competence=None,
                      output='List', lang_key=1):
    """Gets observations of ice thickness from the IceThicknessObs table.

    :param from_date:           [date] A query returns [from_date, to_date]
    :param to_date:             [date] A query returns [from_date, to_date]
    :param region_ids:          [int or list of ints] If region_ids = None, all regions are selected
    :param location_id:         [int] LocationID as given in the ObsLocation table in regObs.
    :param countries:           [int or list of ints] If countries = None, all regions are selected.
    :param time_zone:           [string] Desired timezone representation in summaries. None returns server local time.
    :param group_id:            [int] ObserverGroupID as given in the ObserverGroup table in regObs.
    :param observer_ids:        [int or list of ints] If observer_ids = None, all observers are selected
    :param observer_nick:       [int or list of ints] Default None gives all.
    :param observer_competence: [string] Part of a observer nick name
    :param output:              [string] Options: 'List', 'DataFrame' and 'Count'. Default 'List'.
    :param lang_key             [int] 1 is norwegian, 2 is english

    :return:
    """

    return _get_general(50, from_date=from_date, to_date=to_date, region_ids=region_ids, location_id=location_id,
                        countries=countries, time_zone=time_zone, group_id=group_id, observer_ids=observer_ids,
                        observer_nick=observer_nick, observer_competence=observer_competence, output=output,
                        lang_key=lang_key)


def get_ice_cover(from_date, to_date, region_ids=None, location_id=None, countries=None, time_zone=None,
                  group_id=None, observer_ids=None, observer_nick=None, observer_competence=None,
                  output='List', lang_key=1):
    """Gets observations of ice cover from the IceCoverObs table.

    :param from_date:           [date] A query returns [from_date, to_date]
    :param to_date:             [date] A query returns [from_date, to_date]
    :param region_ids:          [int or list of ints] If region_ids = None, all regions are selected
    :param location_id:         [int] LocationID as given in the ObsLocation table in regObs.
    :param countries:           [int or list of ints] If countries = None, all regions are selected.
    :param time_zone:           [string] Desired timezone representation in summaries. None returns server local time.
    :param group_id:            [int] ObserverGroupID as given in the ObserverGroup table in regObs.
    :param observer_ids:        [int or list of ints] If observer_ids = None, all observers are selected
    :param observer_nick:       [int or list of ints] Default None gives all.
    :param observer_competence: [string] Part of a observer nick name
    :param output:              [string] Options: 'List', 'DataFrame' and 'Count'. Default 'List'.
    :param lang_key             [int] 1 is norwegian, 2 is english

    :return:
    """

    return _get_general(51, from_date=from_date, to_date=to_date, region_ids=region_ids, location_id=location_id,
                        countries=countries, time_zone=time_zone, group_id=group_id, observer_ids=observer_ids,
                        observer_nick=observer_nick, observer_competence=observer_competence, output=output,
                        lang_key=lang_key)


def get_water_level(from_date, to_date, region_ids=None, location_id=None, countries=None, time_zone=None,
                    group_id=None, observer_ids=None, observer_nick=None, observer_competence=None,
                    output='List', lang_key=1):
    """Gets observations of water level from the WaterLevel table. Ths was the first modelling of this form and
    was phased out in 2017.

    :param from_date:           [date] A query returns [from_date, to_date]
    :param to_date:             [date] A query returns [from_date, to_date]
    :param region_ids:          [int or list of ints] If region_ids = None, all regions are selected
    :param location_id:         [int] LocationID as given in the ObsLocation table in regObs.
    :param countries:           [int or list of ints] If countries = None, all regions are selected.
    :param time_zone:           [string] Desired timezone representation in summaries. None returns server local time.
    :param group_id:            [int] ObserverGroupID as given in the ObserverGroup table in regObs.
    :param observer_ids:        [int or list of ints] If observer_ids = None, all observers are selected
    :param observer_nick:       [int or list of ints] Default None gives all.
    :param observer_competence: [string] Part of a observer nick name
    :param output:              [string] Options: 'List', 'DataFrame' and 'Count'. Default 'List'.
    :param lang_key             [int] 1 is norwegian, 2 is english

    :return:
    """

    return _get_general(61, from_date=from_date, to_date=to_date, region_ids=region_ids, location_id=location_id,
                        countries=countries, time_zone=time_zone, group_id=group_id, observer_ids=observer_ids,
                        observer_nick=observer_nick, observer_competence=observer_competence, output=output,
                        lang_key=lang_key)


def get_water_level_2(from_date, to_date, region_ids=None, location_id=None, countries=None, time_zone=None,
                      group_id=None, observer_ids=None, observer_nick=None, observer_competence=None,
                      output='List', lang_key=1):
    """
    Gets observations of water level from the WaterLevel2 table which was put to use in 2017.

    :param from_date:           [date] A query returns [from_date, to_date]
    :param to_date:             [date] A query returns [from_date, to_date]
    :param region_ids:          [int or list of ints] If region_ids = None, all regions are selected
    :param location_id:         [int] LocationID as given in the ObsLocation table in regObs.
    :param countries:           [int or list of ints] If countries = None, all regions are selected.
    :param time_zone:           [string] Desired timezone representation in summaries. None returns server local time.
    :param group_id:            [int] ObserverGroupID as given in the ObserverGroup table in regObs.
    :param observer_ids:        [int or list of ints] If observer_ids = None, all observers are selected
    :param observer_nick:       [int or list of ints] Default None gives all.
    :param observer_competence: [string] Part of a observer nick name
    :param output:              [string] Options: 'List', 'DataFrame' and 'Count'. Default 'List'.
    :param lang_key             [int] 1 is norwegian, 2 is english

    :return:
    """

    return _get_general(62, from_date=from_date, to_date=to_date, region_ids=region_ids, location_id=location_id,
                        countries=countries, time_zone=time_zone, group_id=group_id, observer_ids=observer_ids,
                        observer_nick=observer_nick, observer_competence=observer_competence, output=output,
                        lang_key=lang_key)


def get_land_slide_obs(from_date, to_date, region_ids=None, location_id=None, countries=None, time_zone=None,
                       group_id=None, observer_ids=None, observer_nick=None, observer_competence=None,
                       output='List', lang_key=1):
    """
    Gets observations of land slide observations in the LandSlideObs table in regObs.

    :param from_date:           [date] A query returns [from_date, to_date]
    :param to_date:             [date] A query returns [from_date, to_date]
    :param region_ids:          [int or list of ints] If region_ids = None, all regions are selected
    :param location_id:         [int] LocationID as given in the ObsLocation table in regObs.
    :param countries:           [int or list of ints] If countries = None, all regions are selected.
    :param time_zone:           [string] Desired timezone representation in summaries. None returns server local time.
    :param group_id:            [int] ObserverGroupID as given in the ObserverGroup table in regObs.
    :param observer_ids:        [int or list of ints] If observer_ids = None, all observers are selected
    :param observer_nick:       [int or list of ints] Default None gives all.
    :param observer_competence: [string] Part of a observer nick name
    :param output:              [string] Options: 'List', 'DataFrame' and 'Count'. Default 'List'.
    :param lang_key             [int] 1 is norwegian, 2 is english

    :return:
    """

    return _get_general(71, from_date=from_date, to_date=to_date, region_ids=region_ids, location_id=location_id,
                        countries=countries, time_zone=time_zone, group_id=group_id, observer_ids=observer_ids,
                        observer_nick=observer_nick, observer_competence=observer_competence, output=output,
                        geohazard_tids=20, lang_key=lang_key)


def get_all_observations(from_date=None, to_date=None, registration_types=None, reg_ids=None, region_ids=None,
                         location_id=None, countries=None, time_zone=None,
                         observer_ids=None, observer_nick=None, observer_competence=None, group_id=None,
                         output='List', geohazard_tids=None, lang_key=1):
    """
    Uses the get_data method and maps all data to their respective class. Returns data as list or nest.

    :param from_date:           [string] 'yyyy-mm-dd'. Result includes from date.
    :param to_date:             [string] 'yyyy-mm-dd'. Result includes to date.
    :param registration_types:  [string or list of strings] Default None gives all.
    :param reg_ids:             [int or list of ints] Default None gives all.
    :param region_ids:          [int or list of ints]
    :param location_id:         [int]
    :param countries:           [int or list of ints] If countries = None, all regions are selected.
    :param time_zone:           [string] Desired timezone representation in summaries. None returns server local time.
    :param observer_ids:        [int or list of ints] Default None gives all.
    :param observer_nick        [string] Part of a observer nick name
    :param observer_competence  [int or list of int] as given in CompetenceLevelKDV
    :param group_id:            [int]
    :param output:              [string] 'List' collects all forms on one observation (default for webapi).
                                         'FlatList' is a flat structure with one entry pr form (observation type).
                                         'Count' returns the number of matching observations to the given query.
    :param geohazard_tids:      [int or list of ints] Default None gives all.
    :param lang_key:            [int] Default 1 gives Norwegian.

    :return:                    [list or int] Depending on output requested.
    """

    if output == 'Count':
        total_matches = get_count(from_date=from_date, to_date=to_date, region_ids=region_ids,
                                  observer_ids=observer_ids, observer_nick=observer_nick,
                                  observer_competence=observer_competence, group_id=group_id, location_id=location_id,
                                  countries=countries, time_zone=time_zone, lang_key=lang_key,
                                  registration_types=registration_types, geohazard_tids=geohazard_tids)
        return total_matches

    elif output in ['List', 'FlatList']:
        data = get_data(from_date=from_date, to_date=to_date, registration_types=registration_types, reg_ids=reg_ids,
                        region_ids=region_ids, location_id=location_id, countries=countries, time_zone=time_zone,
                        observer_ids=observer_ids, observer_nick=observer_nick, observer_competence=observer_competence,
                        group_id=group_id, geohazard_tids=geohazard_tids, lang_key=lang_key)

        data_in_classes = []

        for d in data:
            data_in_classes.append(Observation(d))

        if output == 'List':
            return data_in_classes

        elif output == 'FlatList':
            list_of_classes = [o for d in data_in_classes for o in d.Observations]
            return list_of_classes

    else:
        lg.warning("getobservations.py -> get_data_in_classes: Illegal output option.")


def _request_testing():
    """
    Method for testing requests to Regobs web-api directly.
    """

    data = []  # data from one query
    records_requested = 100

    # query object posted in the request
    rssquery = {'LangKey': 0,
                # 'RegId': 176528,
                # 'ObserverGuid': None,               # '4d11f3cc-07c5-4f43-837a-6597d318143c',
                # 'SelectedRegistrationTypes': [{'Id': 82, 'SubTypes': [36]}],
                # _reg_types_dict([10, 11, 12, 13]),    # list dict with type and sub type
                # 'SelectedRegions': None,
                'SelectedGeoHazards': [70],         # list int
                # 'ObserverNickName': None,           # "jostein",
                # 'ObserverId': None,
                # 'ObserverCompetence': None,         # list int
                # 'GroupId': None,
                # 'LocationId': None,
                # 'TimeZone': None,  # string
                # 'Countries': None,  # list int
                'FromDate': '2018-12-30',
                'ToDate': '2019-01-01',
                # 'NumberOfRecords': records_requested,  # int
                'Offset': 0
                }

    url = 'https://api.regobs.no/v4/Search'
    # url = 'https://demo-api.regobs.no/v4/Search'
    # url = 'https://test-api.regobs.no/v4/Search'

    total_count = requests.post(url + '/Count', json=rssquery).json()['TotalMatches']

    # get data from regObs api. It returns 100 items at a time. If more, continue requesting with an offset. Paging.
    while len(data) < total_count:

        r = requests.post(url, json=rssquery)
        responds = r.json()
        data += responds

        if len(responds) == 0:
            lg.info("getobservations.py -> _request_testing: No data")
        else:
            lg.info("getobservations.py -> _request_testing: {0:.2f}%".format(len(data) / total_count * 100))

        if len(data) < total_count:
            rssquery['Offset'] += records_requested
            # else:
            #     more_available = False

    total_count_actual = len(data)

    return data


def _the_simplest_webapi_request():
    """
    Example for demonstrating how simple an request to regObs web-api can be.
    """

    import requests as rq

    query = {'LangKey': 2,
             'FromDate': '2018-03-01',
             'ToDate': '2018-03-04',
             'NumberOfRecords': 500}

    query = {'LangKey': 1,
             'SelectedGeoHazards': [70],
             # 'SelectedRegistrationTypes': {'Id': 51, 'SubTypes': []},
             'FromDate': '2019-03-01',
             'ToDate': '2019-06-04',
             'NumberOfRecords': 1500}

    url = 'https://api.regobs.no/v4/Search/' # AtAGlance'

    data = rq.post(url, json=query)
    time = data.elapsed
    size = len(data.content)
    observations = data.json()

    pass


def _test_diff_in_reg_type_query():
    """
    Test the difference between two requests.
    """
    data1 = get_data(from_date='2017-03-01', to_date='2017-04-01', registration_types=[{'Id': 81, 'SubTypes': [13]}],
                     geohazard_tids=10)
    data2 = get_data(from_date='2017-03-01', to_date='2017-04-01', registration_types=[{'SubTypes': [13]}],
                     geohazard_tids=10)
    diff = []
    # data1.pop(0)
    previous_time = ''
    for d2 in data2:
        common_list_element = False
        if d2['DtRegTime'] == previous_time:
            print(previous_time)
        for d1 in data1:
            if d2['DtRegTime'] == d1['DtRegTime']:
                common_list_element = True

        if common_list_element is False:
            diff.append(d2)
        previous_time = d2['DtRegTime']


if __name__ == "__main__":
    ### Covers calls for single forms
    # general_obs = get_general_observation('2018-01-20', '2018-02-01')
    # incident = get_incident('2012-03-01', '2012-03-10')
    # danger_signs = get_danger_sign('2017-12-13', '2017-12-16', geohazard_tids=10)
    # damages = get_damage_observation('2017-01-01', '2018-02-01', output='DataFrame')
    # weather = get_weather_observation('2018-01-28', '2018-02-01')
    # snow_surface = get_snow_surface_observation('2018-01-29', '2018-02-01')
    # tests = get_tests('2018-01-20', '2018-02-10')
    # avalanche_obs = get_avalanche('2015-03-01', '2015-03-10')
    # avalanche_activity = get_avalanche_activity('2015-03-01', '2015-03-10')
    # avalanche_activity_2 = get_avalanche_activity_2('2017-03-01', '2017-03-10')
    # avalanche_evaluations = get_avalanche_evaluation('2012-03-01', '2012-03-10')
    # avalanche_evaluations_2 = get_avalanche_evaluation_2('2013-03-01', '2013-03-10')
    # avalanche_evaluations_3 = get_avalanche_evaluation_3('2017-03-01', '2017-03-10')
    # problems = get_avalanche_problem_2('2017-03-01', '2017-03-10')
    # snow_profiles = get_snow_profile('2019-05-01', '2019-05-03')
    # snow_profiles_df = get_snow_profile('2018-12-13', '2018-12-16', output='DataFrame')
    # ice_thicks = get_ice_thickness('2018-01-20', '2018-02-10')
    # ice_cover = get_ice_cover('2018-01-20', '2018-02-10')
    # new_water_levels = get_water_level_2('2017-06-01', '2018-02-01')
    # water_levels = get_water_level('2015-01-01', '2016-01-01')
    # land_slides = get_land_slide_obs('2018-01-01', '2018-02-01')

    ##### One generic call, mapped to the individual classes
    # observations_listed = get_all_observations(from_date='2019-05-01', to_date='2019-05-05')
    # list_flatened = get_all_observations(from_date='2019-05-01', to_date='2019-05-05', output='FlatList')

    ###### Do some counting
    # count_all_season_regs = get_all_observations('2016-08-01', '2017-08-01', output='Count')
    # count_ice = get_all_observations('2016-10-01', '2016-11-01', output='Count')
    # count_damages = get_damage_observation('2017-01-01', '2018-02-01', output='Count')

    # todo: test one or more geohazards

    # danger_signs_data = get_data('2017-03-01', '2017-04-01', geohazard_tids=10, output='Count nest', registration_types=13)
    # registrations_ice = get_all_observations(from_date='2016-10-01', to_date='2016-11-01', geohazard_tids=70)
    # my_observations = get_all_observations(from_date=dt.date(2015, 6, 1), to_date=dt.date(2016, 7, 1), geohazard_tids=10, observer_ids=[6, 7, 236], output='List', region_ids=[3011, 3014, 3015])
    # count_registrations_snow_10 = get_all_observations(dt.date(2017, 6, 1), dt.date.today(), geohazard_tids=10, output='Count', observer_nick='obskorps')
    # one_obs = get_data(reg_ids=130548)
    # two_obs = get_data(reg_ids=[130548, 130328])
    # two_obs_count = get_data(reg_ids=[130548, 130328],  output='Count nest')
    # two_observers = get_data(from_date='2016-12-30', to_date='2017-04-01', observer_ids=[6,10])
    # one_observer_count_list = get_data(from_date='2016-12-30', to_date='2017-04-01', observer_ids=6, output='Count list')
    # one_observer_count_nest = get_data(from_date='2012-01-01', to_date='2018-01-01', observer_ids=6, output='Count nest')
    # ice_data = get_data(from_date='2016-10-01', to_date='2016-11-01', geohazard_tids=70)

    # data = _make_one_request(from_date='2019-02-01', to_date='2019-03-01')
    # data = _request_testing()
    # _the_simplest_webapi_request()

    pass
