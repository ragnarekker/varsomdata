# -*- coding: utf-8 -*-
"""Contains classes and methods for accessing all on the regObs webapi."""

import datetime as dt
import requests as requests
import pandas as pd
import sys as sys
from utilities import makelogs as ml
from dateutil.parser import parse as parse
import setenvironment as env

__author__ = 'raek'


def _stringtime_2_datetime(stringtime):
    """Takes in a date as string, both given as unix datetime or normal local time, as string.
    Method returns a normal datetime object.

    :param stringtime:
    :return:           The date and time as datetime object
    """

    if stringtime is None:
        return None

    elif '/Date(' in stringtime:      # oData gives unix time. Unix date time in milliseconds from 1.1.1970
        unix_date_time = int(stringtime[6:-2])
        unix_datetime_in_seconds = unix_date_time/1000 # For some reason they are given in miliseconds
        date = dt.datetime.fromtimestamp(int(unix_datetime_in_seconds))

    else:
        # if '.' in stringtime:       # though sometimes with seconds given with decimal places
        #     non_decimal_stringtime = stringtime[0:stringtime.index('.')]
        #     stringtime = non_decimal_stringtime
        #
        # date = dt.datetime.strptime(stringtime, '%Y-%m-%dT%H:%M:%S')
        date = parse(stringtime)

    return date


def _make_data_frame(list_of_data):
    """Takes a list of objects and makes a Pandas data frame.

    :param list_of_data: [list of objects]
    :return:     [data frame]
    """

    if len(list_of_data) == 0:
        data_frame = pd.DataFrame()
    else:
        observation_fields = list(list_of_data[0].__dict__.keys())
        data_frame = pd.DataFrame(columns=observation_fields)

        i = 0
        for l in list_of_data:
            observation_values = list(l.__dict__.values())
            data_frame.loc[i] = observation_values
            #data_frame.append(observation_values, ignore_index=True)  # does not work
            i += 1

    return data_frame


def _reg_types_dict(registration_tids=None):
    """Method maps single RegistrationTID values to the query dictionary used in regObs webapi

    :param registration_tids:       [int or list of int] Definition given below
    :return:


    Registration IDs and names
    10	Notater, var Fritekst inntil april 2018         # TODO Remove Fritekst reference
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
    36  Toppnoed snøprofil (fra dec 2018)
    40	Snøskredvarsel
    50	Istykkelse
    51	Isdekningsgrad
    61	Vannstand (2017)
    62	Vannstand
    71	Skredhendelse
    80	Hendelser   Grupperings type - Hendelser
    81	Skred og faretegn   Grupperings type - Skred og faretegn
    82	Snødekke og vær Grupperings type - Snødekke og vær
    83	Vurderinger og problemer    Grupperings type - Vurderinger og problemer

    """

    # If input isn't a list, make it so
    if not isinstance(registration_tids, list):
        registration_tids = [registration_tids]

    registration_dicts = []
    for registration_tid in registration_tids:
        if registration_tid is None:
            return None
        elif registration_tid == 10:  # Notater (var Fritekst inntil april 2018)  # TODO Remove Fritekst reference
            registration_dicts.append({'Id': 10, 'SubTypes': []})
        elif registration_tid == 11:  # Ulykke/hendelse
            registration_dicts.append({'Id': 80, 'SubTypes': [11]})
        elif registration_tid == 12:  # Bilder
            return None               # Images cover all observation types
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
            ml.log_and_print("[warning] getobservations.py -> _reg_types_dict: RegistrationTID {0} not supported (yet).".format(registration_tid))

    return registration_dicts


def _make_one_request(from_date=None, to_date=None, reg_id=None, registration_types=None,
        region_ids=None, location_id=None, observer_id=None, observer_nick=None, observer_competence=None,
        group_id=None, output='List', geohazard_tids=None, lang_key=1, recursive_count=5):
    """Part of get_data method. Parameters the same except observer_id and reg_id can not be lists."""

    # Dates in the web-api request are strings
    if isinstance(from_date, dt.date):
        from_date = dt.date.strftime(from_date, '%Y-%m-%d')
    elif isinstance(from_date, dt.datetime):
        from_date = dt.datetime.strftime(from_date, '%Y-%m-%d')

    if isinstance(to_date, dt.date):
        to_date = dt.date.strftime(to_date, '%Y-%m-%d')
    elif isinstance(to_date, dt.datetime):
        to_date = dt.datetime.strftime(to_date, '%Y-%m-%d')

    data = []  # data from one query

    # query object posted in the request
    rssquery = {'LangKey': lang_key,
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
                'FromDate': from_date,
                'ToDate': to_date,
                'NumberOfRecords': None,  # int
                'Offset': 0}

    url = 'https://api.nve.no/hydrology/regobs/webapi_{0}/Search/All'.format(env.web_api_version)
    # url = 'http://tst-h-web03.nve.no/regobswebapi/Search/Rss?geoHazard=0'
    # url = 'https://api.nve.no/hydrology/demo/regobs/webapi_v3.2/Search/Rss?geoHazard=0'

    more_available = True

    # get data from regObs api. It returns 100 items at a time. If more, continue requesting with an offset. Paging.
    while more_available:

        # try or if there is an exception, try again.
        try:
            r = requests.post(url, json=rssquery)
            responds = r.json()
            data += responds['Results']

            if output == 'Count nest':
                ml.log_and_print("[info] getobservations.py -> _make_one_request: total matches {0}".format(responds['TotalMatches']))
                return [responds['TotalMatches']]

            # log request status
            if r.status_code <= 299:

                if responds['TotalMatches'] == 0:
                    ml.log_and_print("[info] getobservations.py -> _make_one_request: no data")
                else:
                    ml.log_and_print("[info] getobservations.py -> _make_one_request: {0:.2f}%".format(
                        len(data) / responds['TotalMatches'] * 100))

                # if more get more by adding to the offset
                if len(data) < responds['TotalMatches']:
                    rssquery['Offset'] += 100
                else:
                    more_available = False

            else:
                ml.log_and_print("[error] getobservations.py -> _make_one_request: http {0} {1}".format(r.status_code, r.reason))

        except Exception:
            error_msg = sys.exc_info()[0]
            ml.log_and_print("[error] getobservations.py -> _make_one_request: EXCEPTION. RECURSIVE COUNT {0} {1}".format(recursive_count, error_msg))

            # When exception occurred, start requesting again. All that has happened in this scope is not important.
            # Call this method again and make sure the received data goes direct to return at the bottom.

            if recursive_count > 1:
                recursive_count -= 1  # count down
                data = _make_one_request(from_date=from_date,
                                         to_date=to_date,
                                         reg_id=reg_id,
                                         registration_types=registration_types,
                                         region_ids=region_ids,
                                         location_id=location_id,
                                         observer_id=observer_id,
                                         observer_nick=observer_nick,
                                         observer_competence=observer_competence,
                                         group_id=group_id,
                                         output=output,
                                         geohazard_tids=geohazard_tids,
                                         lang_key=lang_key,
                                         recursive_count=recursive_count)

            more_available = False

    return data


def get_data(from_date=None, to_date=None, registration_types=None, reg_ids=None, region_ids=None, location_id=None,
        observer_ids=None, observer_nick=None, observer_competence=None, group_id=None,
        output='List', geohazard_tids=None, lang_key=1):
    """Gets data from regObs webapi. Each observation returned as a dictionary in a list.

    :param from_date:           [string] 'yyyy-mm-dd'. Result includes from date.
    :param to_date:             [string] 'yyyy-mm-dd'. Result includes to date.
    :param registration_types:  [string or list of strings] Default None gives all.
    :param reg_ids:             [int or list of ints] Default None gives all.
    :param region_ids:          [int or list of ints]
    :param location_id:         [int]
    :param observer_ids:        [int or list of ints] Default None gives all.
    :param observer_nick        [string] Part of a observer nick name
    :param observer_competence  [int or list of int] as given in CompetenceLevelKDV
    :param group_id:            [int]
    :param output:              [string] 'Nest' collects all observations in one regid in one entry (defult for webapi).
                                         'List' is a flatt structure with one entry pr observation type.
                                         'Count nest' makes one request and picks out info on total matches
                                         'Count list' counts every from in every observation.
    :param geohazard_tids:      [int or list of ints] Default None gives all.
    :param lang_key:            [int] Default 1 gives Norwegian.

    :return:                    [list or int] Depending on output requested.
    """

    # If input isn't a list, make it so
    if not isinstance(registration_types, list):
        registration_types = [registration_types]

    if not isinstance(region_ids, list):
        region_ids = [region_ids]

    if not isinstance(geohazard_tids, list):
        geohazard_tids = [geohazard_tids]

    # regObs weabapi does not support multiple ObserverIDs and RegIDs. Making it so.
    if not isinstance(observer_ids, list):
        observer_ids = [observer_ids]

    if not isinstance(reg_ids, list):
            reg_ids = [reg_ids]

    # if output requested is 'Count' a number is expected, else a list og observations
    all_data = []

    for reg_id in reg_ids:
        for observer_id in observer_ids:

            data = _make_one_request(
                from_date=from_date, to_date=to_date, lang_key=lang_key, reg_id=reg_id,
                registration_types=registration_types, region_ids=region_ids, geohazard_tids=geohazard_tids,
                observer_id=observer_id, observer_nick=observer_nick, observer_competence=observer_competence, group_id=group_id, location_id=location_id, output=output)

            all_data += data

    # Output 'Nest' is the structure returned from webapi. All observations on the same reg_id are grouped to one list item.
    # Output 'List' all observation elements are made a separate item on list.
    # Sums of each are available as 'Count list. and 'Count nest'.
    if output == 'Count nest':
        return sum(all_data)

    # data sorted with ascending observation time
    all_data = sorted(all_data, key=lambda d: d['DtObsTime'])
    if output == 'Nest':
        return all_data

    elif output == 'List' or output == 'Count list':
        listed_data = []

        for d in all_data:
            for o in d['Registrations']:
                listed_data.append({**d, **o})
            for p in d['Pictures']:
                p['RegistrationName'] = 'Bilde'
                listed_data.append({**d, **p})

        if output == 'List':
            return listed_data
        if output == 'Count list':
            return len(listed_data)

    else:
        ml.log_and_print('[warning] getobservations.py -> get_data: Unsupported output type.')
        return None


def get_data_as_class(from_date=None, to_date=None, registration_types=None, reg_ids=None, region_ids=None, location_id=None,
        observer_ids=None, observer_nick=None, observer_competence=None, group_id=None,
        output='Nest', geohazard_tids=None, lang_key=1):
    """Uses the get_data method and maps all data to their respective class. Returns data as list or nest.

    :param from_date:           [string] 'yyyy-mm-dd'. Result includes from date.
    :param to_date:             [string] 'yyyy-mm-dd'. Result includes to date.
    :param registration_types:  [string or list of strings] Default None gives all.
    :param reg_ids:             [int or list of ints] Default None gives all.
    :param region_ids:          [int or list of ints]
    :param location_id:         [int]
    :param observer_ids:        [int or list of ints] Default None gives all.
    :param observer_nick        [string] Part of a observer nick name
    :param observer_competence  [int or list of int] as given in CompetenceLevelKDV
    :param group_id:            [int]
    :param output:              [string] 'Nest' collects all observations in one regid in one entry (defult for webapi).
                                         'List' is a flatt structure with one entry pr observation type.
    :param geohazard_tids:      [int or list of ints] Default None gives all.
    :param lang_key:            [int] Default 1 gives Norwegian.

    :return:                    [list or int] Depending on output requested.
    """

    data = get_data(from_date=from_date, to_date=to_date, registration_types=registration_types, reg_ids=reg_ids,
                    region_ids=region_ids, location_id=location_id, observer_ids=observer_ids,
                    observer_nick=observer_nick, observer_competence=observer_competence, group_id=group_id,
                    output=output, geohazard_tids=geohazard_tids, lang_key=lang_key)

    data_in_classes = []

    for d in data:
        data_in_classes.append(Observation(d))

    return data_in_classes


class Registration:

    def __init__(self, d):

        self.RegID = int(d['RegId'])
        self.DtObsTime = _stringtime_2_datetime(d['DtObsTime'])
        self.DtRegTime = _stringtime_2_datetime(d['DtRegTime'])

        # DtChangeTime only given when registration has been changed.
        # If DtChangeTime ends up like None, the field is missing from the view
        if 'DtChangeTime' in d:
            if d['DtChangeTime'] is not None:
                self.DtChangeTime = _stringtime_2_datetime(d['DtChangeTime'])
            else:
                self.DtChangeTime = self.DtRegTime
        else:
            self.DtChangeTime = None

        self.GeoHazardTID = d['GeoHazardTid']
        self.GeoHazardName = d['GeoHazardName']

        self.OriginalData = d


class Location:

    def __init__(self, d):

        self.LocationName = d['LocationName']
        self.LocationID = d['LocationId']

        self.UTMZone = int(d['UtmZone'])
        self.UTMEast = int(d['UtmEast'])
        self.UTMNorth = int(d['UtmNorth'])

        self.Latitude = d['Latitude']
        self.Longitude = d['Longitude']

        self.ForecastRegionName = d['ForecastRegionName']
        self.ForecastRegionTID = d['ForecastRegionTid']
        self.MunicipalName = d['MunicipalName']


class Observer:

    def __init__(self, d):

        self.NickName = d['NickName']
        self.ObserverId = int(d['ObserverId'])
        self.CompetenceLevelName = d['CompetenceLevelName']


class Pictures:
    """A parent class for listing of picture related to the form in question."""

    def __init__(self, d, RegistrationTID):

        self.Pictures = []
        for p in d['Pictures']:
            picture = Picture(p)
            if picture.RegistrationTID == RegistrationTID:
                self.Pictures.append(picture)


class Picture:

    def __init__(self, d):

        self.FullObject = d['FullObject']

        self.PictureID = d['FullObject']['PictureID']
        self.URLoriginal = env.image_basestring_original + '{}'.format(self.PictureID)
        self.URLlarge = env.image_basestring_large + '{}'.format(self.PictureID)
        self.Photographer = d['FullObject']['Photographer']
        self.Copyright = d['FullObject']['Copyright']
        self.Aspect = d['FullObject']['Aspect']
        # self.GeoHazardTID = d['FullObject']['GeoHazardTID']
        # self.GeoHazardName = d['FullObject']['GeoHazardTName']
        self.RegistrationTID = d['FullObject']['RegistrationTID']
        self.RegistrationName = d['FullObject']['RegistrationTName']
        # self.PictureComment = d['FullObject']['PictureComment']
        self.Comment = d['FullObject']['Comment']


class Observation(Registration, Location, Observer):

    def __init__(self, d):

        Registration.__init__(self, d)
        Location.__init__(self, d)
        Observer.__init__(self, d)

        self.Observations = []
        for r in d['Registrations']:
            if r['RegistrationTid'] == 10:
                observation = GeneralObservation({**d, **r})
            elif r['RegistrationTid'] == 11:
                observation = Incident({**d, **r})
            elif r['RegistrationTid'] == 12:
                observation = PictureObservation({**d, **r})
            elif r['RegistrationTid'] == 13:
                observation = DangerSign({**d, **r})
            elif r['RegistrationTid'] == 14:
                observation = DamageObs({**d, **r})
            elif r['RegistrationTid'] == 21:
                observation = WeatherObservation({**d, **r})
            elif r['RegistrationTid'] == 22:
                observation = SnowSurfaceObservation({**d, **r})
            # Snow profile has a new form and TID pr dec 2018
            elif r['RegistrationTid'] == 23:
                observation = SnowProfilePicture({**d, **r})
            elif r['RegistrationTid'] == 25:
                observation = ColumnTest({**d, **r})
            elif r['RegistrationTid'] == 26:
                observation = AvalancheObs({**d, **r})
            elif r['RegistrationTid'] == 27:
                observation = AvalancheActivityObs({**d, **r})
            elif r['RegistrationTid'] == 28:
                observation = AvalancheEvaluation({**d, **r})
            elif r['RegistrationTid'] == 30:
                observation = AvalancheEvaluation2({**d, **r})
            elif r['RegistrationTid'] == 31:
                observation = AvalancheEvaluation3({**d, **r})
            elif r['RegistrationTid'] == 32:
                observation = AvalancheEvalProblem2({**d, **r})
            elif r['RegistrationTid'] == 33:
                observation = AvalancheActivityObs2({**d, **r})
            elif r['RegistrationTid'] == 36:
                observation = SnowProfile({**d, **r})
            elif r['RegistrationTid'] == 50:
                observation = IceThickness({**d, **r})
            elif r['RegistrationTid'] == 51:
                observation = IceCover({**d, **r})
            elif r['RegistrationTid'] == 61:
                observation = WaterLevel({**d, **r})
            elif r['RegistrationTid'] == 62:
                observation = WaterLevel2({**d, **r})
            elif r['RegistrationTid'] == 71:
                observation = LandSlideObs({**d, **r})
            else:
                observation = None
                ml.log_and_print("[warning] Unrecognized RegistrationTID given {0}".format(r['RegistrationTid']))

            if observation:
                self.Observations.append(observation)

        self.Pictures = []
        for p in d['Pictures']:
            self.Pictures.append(PictureObservation({**d, **p}))

        self.LangKey = int(d['LangKey'])


class AllRegistrations(Registration, Location, Observer):

    def __init__(self, d):

        Registration.__init__(self, d)
        Location.__init__(self, d)
        Observer.__init__(self, d)

        self.FullObject = d['FullObject']
        self.RegistrationTID = int(d['RegistrationTid'])
        self.RegistrationName = d['RegistrationName']

        self.TypicalValue1 = d['TypicalValue1']
        self.TypicalValue2 = d['TypicalValue2']

        self.LangKey = int(d['LangKey'])


class AvalancheActivityObs(Registration, Location, Observer, Pictures):

    def __init__(self, d):

        Registration.__init__(self, d)
        Location.__init__(self, d)
        Observer.__init__(self, d)

        self.FullObject = d['FullObject']
        self.RegistrationTID = int(d['RegistrationTid'])
        self.RegistrationName = d['RegistrationName']

        Pictures.__init__(self, d, self.RegistrationTID)

        self.EstimatedNumTID = d['FullObject']['EstimatedNumTID']
        self.EstimatedNumName = d['FullObject']['EstimatedNumTName']

        self.DestructiveSizeName = d['FullObject']['DestructiveSizeTName']
        self.Aspect = d['FullObject']['Aspect']
        self.HeightStartingZone = d['FullObject']['HeigthStartZone']
        self.AvalancheName = d['FullObject']['AvalancheTName']
        self.AvalancheTriggerName = d['FullObject']['AvalancheTriggerTName']
        self.TerrainStartingZone = d['FullObject']['TerrainStartZoneTName']
        self.DtAvalancheTime = _stringtime_2_datetime(d['FullObject']['DtAvalancheTime'])
        self.Snowline = d['FullObject']['SnowLine']
        self.Comment = d['FullObject']['Comment']
        self.LangKey = d['LangKey']


class AvalancheActivityObs2(Registration, Location, Observer, Pictures):

    def __init__(self, d):

        Registration.__init__(self, d)
        Location.__init__(self, d)
        Observer.__init__(self, d)

        self.FullObject = d['FullObject']
        self.RegistrationTID = int(d['RegistrationTid'])
        self.RegistrationName = d['RegistrationName']

        Pictures.__init__(self, d, self.RegistrationTID)

        self.EstimatedNumTID = d['FullObject']['EstimatedNumTID']
        self.EstimatedNumName = d['FullObject']['EstimatedNumTName']

        self.DtStart = _stringtime_2_datetime(d['FullObject']['DtStart'])
        self.DtEnd = _stringtime_2_datetime(d['FullObject']['DtEnd'])
        if self.DtStart is not None and self.DtEnd is not None:
            self.DtMiddleTime = self.DtStart + (self.DtEnd - self.DtStart) / 2      # Middle time of activity period
        else:
            self.DtMiddleTime = None

        self.ValidExposition = d['FullObject']['ValidExposition']    # int of eight char. First char is N, second is NE etc.
        self.ExposedHeight1 = d['FullObject']['ExposedHeight1']      # upper height
        self.ExposedHeight2 = d['FullObject']['ExposedHeight2']      # lower height
        self.ExposedHeightComboTID = d['FullObject']['ExposedHeightComboTID']

        self.AvalancheExtName = d['FullObject']['AvalancheExtTName']
        self.AvalCauseName = d['FullObject']['AvalCauseTName']
        self.AvalTriggerSimpleName = d['FullObject']['AvalTriggerSimpleTName']
        self.DestructiveSizeName = d['FullObject']['DestructiveSizeTName']
        self.AvalPropagationName = d['FullObject']['AvalPropagationTName']
        self.Comment = d['FullObject']['Comment']

        self.LangKey = d['LangKey']


class AvalancheEvalProblem0(Registration, Location, Observer):
    """ The avalanche problems fist used. At that time the problems were a list
    List in AvalancheEvaluation. The avalanche problems where just text."""

    def __init__(self, d, id, tid, name):

        Registration.__init__(self, d)
        Location.__init__(self, d)
        Observer.__init__(self, d)

        self.RegistrationTID = int(d['RegistrationTid'])
        self.RegistrationName = d['RegistrationName']

        self.AvalancheProblemID = id
        self.AvalancheProblemTID = tid
        self.AvalancheProblemName = name

        self.LangKey = d['LangKey']


class AvalancheEvalProblem(Registration, Location, Observer):
    """List in AvalancheEvaluation2"""

    def __init__(self, d, p):

        Registration.__init__(self, d)
        Location.__init__(self, d)
        Observer.__init__(self, d)

        self.FullObject = p
        self.RegistrationTID = int(d['RegistrationTid'])
        self.RegistrationName = d['RegistrationName']

        self.AvalancheProblemID = p['AvalancheEvalProblemID']
        self.AvalCauseName = p['AvalCauseTName']
        self.AvalCauseExtName = p['AvalCauseExtTName']
        self.AvalancheProbabilityName = p['AvalProbabilityTName']
        self.AvalReleaseHeightName = p['AvalReleaseHeightTName']
        self.AvalTriggerSimpleName = p['AvalTriggerSimpleTName']
        self.AvalancheExtName = p['AvalancheExtTName']
        self.AvalancheProbabilityAutoText = p['AvalancheProbabilityAutoText']
        self.AvalancheProblemAutoText = p['AvalancheProblemAutoText']
        self.DestructiveSizeExtName = p['DestructiveSizeExtTName']
        self.Comment = p['Comment']

        self.LangKey = d['LangKey']


class AvalancheEvalProblem2(Registration, Location, Observer, Pictures):

    def __init__(self, d):

        Registration.__init__(self, d)
        Location.__init__(self, d)
        Observer.__init__(self, d)

        self.FullObject = d['FullObject']
        self.RegistrationTID = int(d['RegistrationTid'])
        self.RegistrationName = d['RegistrationName']

        Pictures.__init__(self, d, self.RegistrationTID)

        self.AvalancheProblemID = d['FullObject']['AvalancheEvalProblemID']

        self.AvalCauseAttributeCrystalTID = d['FullObject']['AvalCauseAttributeCrystalTID']
        self.AvalCauseAttributeLightTID = d['FullObject']['AvalCauseAttributeLightTID']
        self.AvalCauseAttributeSoftTID = d['FullObject']['AvalCauseAttributeSoftTID']
        self.AvalCauseAttributeThinTID = d['FullObject']['AvalCauseAttributeThinTID']

        self.AvalCauseAttributeCrystalName = d['FullObject']['AvalCauseAttributeCrystalTName']
        self.AvalCauseAttributeLightName = d['FullObject']['AvalCauseAttributeLightTName']
        self.AvalCauseAttributeSoftName = d['FullObject']['AvalCauseAttributeSoftTName']
        self.AvalCauseAttributeThinName = d['FullObject']['AvalCauseAttributeThinTName']

        self.AvalCauseDepthName = d['FullObject']['AvalCauseDepthTName']
        self.AvalCauseName = d['FullObject']['AvalCauseTName']
        self.AvalCauseTID = d['FullObject']['AvalCauseTID']
        self.AvalTriggerSimpleName = d['FullObject']['AvalTriggerSimpleTName']
        self.AvalancheProbabilityName = d['FullObject']['AvalProbabilityTName']
        self.DestructiveSizeName = d['FullObject']['DestructiveSizeTName']
        self.AvalPropagationName = d['FullObject']['AvalPropagationTName']

        self.ValidExposition = d['FullObject']['ValidExposition']  # int of eight char. First char is N, second is NE etc.
        self.ExposedHeight1 = d['FullObject']['ExposedHeight1']      # upper height
        self.ExposedHeight2 = d['FullObject']['ExposedHeight2']      # lower height
        self.ExposedHeightComboTID = d['FullObject']['ExposedHeightComboTID']

        self.AvalancheExtName = d['FullObject']['AvalancheExtTName']
        self.AvalancheExtTID = d['FullObject']['AvalancheExtTID']
        self.Comment = d['FullObject']['Comment']
        self.LangKey = d['LangKey']


class AvalancheObs(Registration, Location, Observer, Pictures):

    def __init__(self, d):

        Registration.__init__(self, d)
        Location.__init__(self, d)
        Observer.__init__(self, d)

        self.FullObject = d['FullObject']
        self.RegistrationTID = int(d['RegistrationTid'])
        self.RegistrationName = d['RegistrationName']

        Pictures.__init__(self, d, self.RegistrationTID)

        self.AvalancheName = d['FullObject']['AvalancheTName']
        self.AvalancheTriggerName = d['FullObject']['AvalancheTriggerTName']
        self.Comment = d['FullObject']['Comment']
        self.DestructiveSizeName = d['FullObject']['DestructiveSizeTName']
        self.DtAvalancheTime = _stringtime_2_datetime(d['FullObject']['DtAvalancheTime'])
        self.HeightStartZone = d['FullObject']['HeigthStartZone']
        self.HeightStopZone = d['FullObject']['HeigthStopZone']
        self.SnowLine = d['FullObject']['SnowLine']
        self.TerrainStartZoneName = d['FullObject']['TerrainStartZoneTName']
        self.UTMEastStop = d['FullObject']['UTMEastStop']
        self.UTMNorthStop = d['FullObject']['UTMNorthStop']
        self.UTMZoneStop = d['FullObject']['UTMZoneStop']

        self.LangKey = d['LangKey']


class DangerSign(Registration, Location, Observer, Pictures):

    def __init__(self, d):

        Registration.__init__(self, d)
        Location.__init__(self, d)
        Observer.__init__(self, d)

        self.FullObject = d['FullObject']
        self.RegistrationTID = int(d['RegistrationTid'])
        self.RegistrationName = d['RegistrationName']

        Pictures.__init__(self, d, self.RegistrationTID)

        self.Comment = d['FullObject']['Comment']
        self.DangerSignName = d['FullObject']['DangerSignTName']
        self.DangerSignTID = d['FullObject']['DangerSignTID']

        self.LangKey = d['LangKey']


class Incident(Registration, Location, Observer, Pictures):

    def __init__(self, d):

        Registration.__init__(self, d)
        Location.__init__(self, d)
        Observer.__init__(self, d)

        self.FullObject = d['FullObject']
        self.RegistrationTID = int(d['RegistrationTid'])
        self.RegistrationName = d['RegistrationName']

        Pictures.__init__(self, d, self.RegistrationTID)

        self.ActivityInfluencedTID = d['FullObject']['ActivityInfluencedTID']
        self.ActivityInfluencedName = d['FullObject']['ActivityInfluencedTName']
        self.DamageExtentTID = d['FullObject']['DamageExtentTID']
        self.DamageExtentName = d['FullObject']['DamageExtentTName']
        self.IncidentHeader = d['FullObject']['IncidentHeader']
        self.IncidentIngress = d['FullObject']['IncidentIngress']
        self.IncidentText = d['FullObject']['IncidentText']

        self.URLs = []
        for u in d['FullObject']['Urls']:
            self.URLs.append({'URLLine': u['UrlLine'], 'URLDescription': u['UrlDescription']})

        self.GeoHazardName = d['GeoHazardName']
        self.GeoHazardTID = d['GeoHazardTid']
        self.LangKey = d['LangKey']


class AvalancheEvaluation3(Registration, Location, Observer, Pictures):

    def __init__(self, d):

        Registration.__init__(self, d)
        Location.__init__(self, d)
        Observer.__init__(self, d)

        self.FullObject = d['FullObject']
        self.RegistrationTID = int(d['RegistrationTid'])
        self.RegistrationName = d['RegistrationName']

        Pictures.__init__(self, d, self.RegistrationTID)

        self.AvalancheEvaluation = d['FullObject']['AvalancheEvaluation']
        self.AvalancheDevelopment = d['FullObject']['AvalancheDevelopment']
        self.AvalancheDangerTID = d['FullObject']['AvalancheDangerTID']
        self.AvalancheDangerName = d['FullObject']['AvalancheDangerTName']
        self.ForecastCorrectTID = d['FullObject']['ForecastCorrectTID']
        self.ForecastCorrectName = d['FullObject']['ForecastCorrectTName']
        self.ForecastComment = d['FullObject']['ForecastComment']
        self.LangKey = d['LangKey']


class AvalancheEvaluation2(Registration, Location, Observer, Pictures):

    def __init__(self, d):

        Registration.__init__(self, d)
        Location.__init__(self, d)
        Observer.__init__(self, d)

        self.FullObject = d['FullObject']
        self.RegistrationTID = int(d['RegistrationTid'])
        self.RegistrationName = d['RegistrationName']

        Pictures.__init__(self, d, self.RegistrationTID)

        self.AvalancheEvaluation = d['FullObject']['AvalancheEvaluation']
        self.AvalancheDevelopment = d['FullObject']['AvalancheDevelopment']
        self.AvalancheDangerTID = d['FullObject']['AvalancheDangerTID']
        self.AvalancheDangerName = d['FullObject']['AvalancheDangerTName']

        self.ExposedClimateTID = d['FullObject']['ExposedClimateTID']
        self.ExposedClimateTName = d['FullObject']['ExposedClimateTName']

        self.ValidExposition = d['FullObject']['ValidExposition']  # int of eight char. First char is N, second is NE etc.
        self.ExposedHeight1 = d['FullObject']['ExposedHeight1']      # upper height
        self.ExposedHeight2 = d['FullObject']['ExposedHeight2']      # lower height
        self.ExposedHeightComboTID = d['FullObject']['ExposedHeightComboTID']
        self.Comment = d['FullObject']['Comment']

        self.AvalancheProblems = []
        for p in d['FullObject']['AvalancheEvalProblems']:
            if p['AvalCauseTID'] != 0 or p['AvalCauseExtTID'] != 0:
                self.AvalancheProblems.append(AvalancheEvalProblem(d, p))

        self.LangKey = d['LangKey']


class AvalancheEvaluation(Registration, Location, Observer, Pictures):

    def __init__(self, d):

        Registration.__init__(self, d)
        Location.__init__(self, d)
        Observer.__init__(self, d)

        self.FullObject = d['FullObject']
        self.RegistrationTID = int(d['RegistrationTid'])
        self.RegistrationName = d['RegistrationName']

        Pictures.__init__(self, d, self.RegistrationTID)

        self.AvalancheDangerTID = d['FullObject']['AvalancheDangerTID']
        self.AvalancheDangerName = d['FullObject']['AvalancheDangerTName']
        self.AvalancheEvaluation = d['FullObject']['AvalancheEvaluation1']

        self.AvalancheProblems = []
        if d['FullObject']['AvalancheProblemTID1'] != 0:
            self.AvalancheProblems.append(AvalancheEvalProblem0(d, 1, d['FullObject']['AvalancheProblemTID1'], d['FullObject']['AvalancheProblemTName1']))
        if d['FullObject']['AvalancheProblemTID2'] != 0:
            self.AvalancheProblems.append(AvalancheEvalProblem0(d, 2, d['FullObject']['AvalancheProblemTID2'], d['FullObject']['AvalancheProblemTName2']))
        if d['FullObject']['AvalancheProblemTID3'] != 0:
            self.AvalancheProblems.append(AvalancheEvalProblem0(d, 3, d['FullObject']['AvalancheProblemTID3'], d['FullObject']['AvalancheProblemTName3']))

        self.ValidExposition = d['FullObject']['ValidExposition']
        self.ValidHeightFrom = d['FullObject']['ValidHeightFrom']
        self.ValidHeightRelative = d['FullObject']['ValidHeightRelative']
        self.ValidHeigtTo = d['FullObject']['ValidHeigtTo']

        self.Comment = d['FullObject']['Comment']
        self.LangKey = d['LangKey']


class GeneralObservation(Registration, Location, Observer, Pictures):

    def __init__(self, d):

        Registration.__init__(self, d)
        Location.__init__(self, d)
        Observer.__init__(self, d)

        self.FullObject = d['FullObject']
        self.RegistrationTID = int(d['RegistrationTid'])
        self.RegistrationName = d['RegistrationName']

        Pictures.__init__(self, d, self.RegistrationTID)

        self.ObsHeader = d['FullObject']['ObsHeader']
        self.ObsComment = d['FullObject']['ObsComment']
        self.Comment = d['FullObject']['Comment']

        self.URLs = []
        for u in d['FullObject']['Urls']:
            self.URLs.append({'URLLine': u['UrlLine'], 'URLDescription': u['UrlDescription']})

        self.LangKey = d['LangKey']


class PictureObservation(Registration, Location, Observer, Picture):

    def __init__(self, d):

        Registration.__init__(self, d)
        Location.__init__(self, d)
        Observer.__init__(self, d)
        Picture.__init__(self, d)

        self.LangKey = d['LangKey']


class WeatherObservation(Registration, Location, Observer, Pictures):

    def __init__(self, d):

        Registration.__init__(self, d)
        Location.__init__(self, d)
        Observer.__init__(self, d)

        self.FullObject = d['FullObject']
        self.RegistrationTID = int(d['RegistrationTid'])
        self.RegistrationName = d['RegistrationName']

        Pictures.__init__(self, d, self.RegistrationTID)

        self.PrecipitationTID = d['FullObject']['PrecipitationTID']
        self.PrecipitationName = d['FullObject']['PrecipitationName']
        self.AirTemperature = d['FullObject']['AirTemperature']
        self.CloudCover = d['FullObject']['CloudCover']
        self.WindDirection = d['FullObject']['WindDirection']
        self.WindDirectionName = d['FullObject']['WindDirectionName']
        self.WindSpeed = d['FullObject']['WindSpeed']
        self.Comment = d['FullObject']['Comment']

        self.LangKey = d['LangKey']


class SnowSurfaceObservation(Registration, Location, Observer, Pictures):

    def __init__(self, d):

        Registration.__init__(self, d)
        Location.__init__(self, d)
        Observer.__init__(self, d)

        self.FullObject = d['FullObject']
        self.RegistrationTID = int(d['RegistrationTid'])
        self.RegistrationName = d['RegistrationName']

        Pictures.__init__(self, d, self.RegistrationTID)

        self.SnowDepth = d['FullObject']['SnowDepth']
        self.NewSnowDepth24 = d['FullObject']['NewSnowDepth24']
        self.NewSnowLine = d['FullObject']['NewSnowLine']
        self.SnowDriftTID = d['FullObject']['SnowDriftTID']
        self.SnowDriftName = d['FullObject']['SnowDriftTName']
        self.HeightLimitLayeredSnow = d['FullObject']['HeightLimitLayeredSnow']
        self.SnowLine = d['FullObject']['Snowline']
        self.SnowSurfaceTID = d['FullObject']['SnowSurfaceTID']
        self.SnowSurfaceName = d['FullObject']['SnowSurfaceTName']
        self.SurfaceWaterContentTID = d['FullObject']['SurfaceWaterContentTID']
        self.SurfaceWaterContentName = d['FullObject']['SurfaceWaterContentTName']
        self.Comment = d['FullObject']['Comment']

        self.LangKey = d['LangKey']


class DamageObs(Registration, Location, Observer, Pictures):

    def __init__(self, d):

        Registration.__init__(self, d)
        Location.__init__(self, d)
        Observer.__init__(self, d)

        self.FullObject = d['FullObject']
        self.RegistrationTID = int(d['RegistrationTid'])
        self.RegistrationName = d['RegistrationName']

        Pictures.__init__(self, d, self.RegistrationTID)

        self.DamageTypeTID = d['FullObject']['DamageTypeTID']
        self.DamageTypeName = d['FullObject']['DamageTypeTName']
        self.DamagePosition = d['FullObject']['DamagePosition']
        self.Comment = d['FullObject']['Comment']

        self.Pictures = []
        for p in d['Pictures']:
            self.Pictures.append({'PictureID': p['TypicalValue2'], 'PictureComment': p['TypicalValue1'], 'FullObject': p['FullObject']})

        self.LangKey = d['LangKey']


class SnowProfilePicture(Registration, Location, Observer, Pictures):

    def __init__(self, d):

        Registration.__init__(self, d)
        Location.__init__(self, d)
        Observer.__init__(self, d)

        self.FullObject = d['FullObject']
        self.RegistrationTID = int(d['RegistrationTid'])
        self.RegistrationName = d['RegistrationName']

        Pictures.__init__(self, d, self.RegistrationTID)

        self.PictureID = d['FullObject']['PictureID']
        self.Photographer = d['FullObject']['Photographer']
        self.Copyright = d['FullObject']['Copyright']
        self.RegistrationTID = d['FullObject']['RegistrationTID']
        self.RegistrationName = d['FullObject']['RegistrationTName']
        # self.PictureComment = d['FullObject']['PictureComment']
        self.Comment = d['FullObject']['Comment']
        self.LangKey = d['LangKey']


class StratProfileLayer:

    def __init__(self, l):

        self.DepthTop = l['DepthTop']
        self.Thickness = l['Thickness']
        self.GrainFormPrimaryTID = l['GrainFormPrimaryTID']
        self.GrainFormPrimaryName = l['GrainFormPrimaryTName']
        self.GrainFormSecondaryTID = l['GrainFormSecondaryTID']
        self.GrainFormSecondaryName = l['GrainFormSecondaryTName']
        self.GrainSizeAvg = l['GrainSizeAvg']/10            # error in api
        self.GrainSizeAvgMax = l['GrainSizeAvgMax']/10      # error in api
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


class SnowTempLayer:

    def __init__(self, l):

        self.Depth = l['Depth']
        self.SnowTemp = l['SnowTemp']


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
        self.WaterEquivalent = self.Density * self.Thickness
        # wrong on api
        # self.WaterEquivalent = l['WaterEquivalent']


class ProfileColumnTest:

    def __init__(self, t):
        self.CompressionTestID = t['CompressionTestID']
        self.CompressionTestTID = t['CompressionTestTID']
        self.CompressionTestName = t['CompressionTestTName']
        self.TapsFracture = t['TapsFracture']
        self.TapsFullPropagation = t['TapsFullPropagation']
        self.PropagationTID = t['PropagationTID']
        self.PropagationName = t['PropagationTName']
        self.FractureDepth = t['FractureDepth']
        self.StabilityEvalTID = t['StabilityEvalTID']
        self.StabilityEvalName = t['StabilityEvalTName']
        self.ComprTestFractureTID = t['ComprTestFractureTID']
        self.IncludeInSnowProfile = t['IncludeInSnowProfile']
        self.ComprTestFractureName = t['ComprTestFractureTName']
        self.Comment = t['Comment']


class ColumnTest(Registration, Location, Observer, Pictures, ProfileColumnTest):

    def __init__(self, d):
        Registration.__init__(self, d)
        Location.__init__(self, d)
        Observer.__init__(self, d)

        self.FullObject = d['FullObject']
        self.RegistrationTID = int(d['RegistrationTid'])
        self.RegistrationName = d['RegistrationName']
        self.LangKey = d['LangKey']

        Pictures.__init__(self, d, self.RegistrationTID)

        # Not all column tests are in the profile, but the ProfileColumnTest class contains the common values.
        ProfileColumnTest.__init__(self, d['FullObject'])


class SnowProfile(Registration, Location, Observer, Pictures):

    def __init__(self, d):

        Registration.__init__(self, d)
        Location.__init__(self, d)
        Observer.__init__(self, d)

        self.FullObject = d['FullObject']
        self.RegistrationTID = int(d['RegistrationTid'])
        self.RegistrationName = d['RegistrationName']

        Pictures.__init__(self, d, self.RegistrationTID)

        self.TotalDepth = d['FullObject']['TotalDepth']
        self.AttachmentID = d['FullObject']['AttachmentID']
        self.Comment = d['FullObject']['Comment']

        self.StratProfile = []
        for sp in d['FullObject']['StratProfile']['Layers']:
            layer = StratProfileLayer(sp)
            self.StratProfile.append(layer)

        self.SnowTemp = []
        for st in d['FullObject']['SnowTemp']['Layers']:
            layer = SnowTempLayer(st)
            self.SnowTemp.append(layer)

        self.SnowDensities = []
        for sd in d['FullObject']['SnowDensity']:
            snow_density = SnowDensity(sd)
            self.SnowDensities.append(snow_density)

        self.ColumnTests = []
        for ct in d['FullObject']['CompressionTest']:
            column_test = ProfileColumnTest(ct)
            self.ColumnTests.append(column_test)

        self.LangKey = d['LangKey']


class IceThicknessLayer:

    def __init__(self, l):

        self.IceLayerID = l['IceLayerID']
        self.IceLayerTID = l['IceLayerTID']
        self.IceLayerName = l['IceLayerTName']
        self.IceLayerThickness = l['IceLayerThickness']


class IceThickness(Registration, Location, Observer, Pictures):

    def __init__(self, d):

        Registration.__init__(self, d)
        Location.__init__(self, d)
        Observer.__init__(self, d)

        self.FullObject = d['FullObject']
        self.RegistrationTID = int(d['RegistrationTid'])
        self.RegistrationName = d['RegistrationName']

        Pictures.__init__(self, d, self.RegistrationTID)

        self.SnowDepth = d['FullObject']['SnowDepth']
        self.SlushSnow = d['FullObject']['SlushSnow']
        self.SlushSnow = d['FullObject']['IceThicknessSum']
        self.IceHeightBefore = d['FullObject']['IceHeightBefore']
        self.IceHeightAfter = d['FullObject']['IceHeightAfter']
        self.Comment = d['FullObject']['Comment']

        self.IceThicknessLayers = []
        for l in d['FullObject']['IceThicknessLayers']:
            layer = IceThicknessLayer(l)
            self.IceThicknessLayers.append(layer)

        self.LangKey = d['LangKey']


class IceCover(Registration, Location, Observer, Pictures):

    def __init__(self, d):

        Registration.__init__(self, d)
        Location.__init__(self, d)
        Observer.__init__(self, d)

        self.FullObject = d['FullObject']
        self.RegistrationTID = int(d['RegistrationTid'])
        self.RegistrationName = d['RegistrationName']

        Pictures.__init__(self, d, self.RegistrationTID)

        self.IceCoverBeforeTID = d['FullObject']['IceCoverBeforeTID']
        self.IceCoverBeforeName = d['FullObject']['IceCoverBeforeTName']
        self.IceCoverTID = d['FullObject']['IceCoverTID']
        self.IceCoverName = d['FullObject']['IceCoverTName']
        self.IceCoverAfterTID = d['FullObject']['IceCoverAfterTID']
        self.IceCoverAfterName = d['FullObject']['IceCoverAfterTName']
        self.IceSkateabilityTID = d['FullObject']['IceSkateabilityTID']
        self.IceSkateabilityName = d['FullObject']['IceSkateabilityTName']
        self.IceCapacityTID = d['FullObject']['IceCapacityTID']
        self.IceCapacityName = d['FullObject']['IceCapacityTName']
        self.Comment = d['FullObject']['Comment']
        self.LangKey = d['LangKey']


class WaterLevel(Registration, Location, Observer, Pictures):

    def __init__(self, d):
        Registration.__init__(self, d)
        Location.__init__(self, d)
        Observer.__init__(self, d)

        self.FullObject = d['FullObject']
        self.RegistrationTID = int(d['RegistrationTid'])
        self.RegistrationName = d['RegistrationName']

        Pictures.__init__(self, d, self.RegistrationTID)

        self.WaterLevelDescribed = d['FullObject']['WaterLevelDescribed']
        self.WaterLevelValue = d['FullObject']['WaterLevelValue']
        self.WaterLevelRefTID = d['FullObject']['WaterLevelRefTID']
        self.WaterLevelRefName = d['FullObject']['WaterLevelRefTName']
        self.Comment = d['FullObject']['Comment']
        self.MeasuredDischarge = d['FullObject']['MeasuredDischarge']
        self.LangKey = d['LangKey']


class WaterLevelMeasurement:

    def __init__(self, m):

        self.WaterLevelMeasurementId = m['WaterLevelMeasurementId']
        self.WaterLevelValue = m['WaterLevelValue']
        self.DtMeasurementTime = m['DtMeasurementTime']
        self.Comment = m['Comment']
        self.Pictures = m['Pictures']


class WaterLevel2(Registration, Location, Observer):

    def __init__(self, d):
        Registration.__init__(self, d)
        Location.__init__(self, d)
        Observer.__init__(self, d)

        self.FullObject = d['FullObject']
        self.RegistrationTID = int(d['RegistrationTid'])
        self.RegistrationName = d['RegistrationName']

        self.WaterLevelStateTID = d['FullObject']['WaterLevelStateTID']
        self.WaterLevelStateName = d['FullObject']['WaterLevelStateTName']
        self.WaterAstrayTID = d['FullObject']['WaterAstrayTID']
        self.WaterAstrayName = d['FullObject']['WaterAstrayTName']
        self.ObservationTimingTID = d['FullObject']['ObservationTimingTID']
        self.ObservationTimingName = d['FullObject']['ObservationTimingTName']
        self.MeasurementReferenceTID = d['FullObject']['MeasurementReferenceTID']
        self.MeasurementReferenceName = d['FullObject']['MeasurementReferenceTName']
        self.MeasurementTypeTID = d['FullObject']['MeasurementTypeTID']
        self.MeasurementTypeName = d['FullObject']['MeasurementTypeTName']
        self.WaterLevelMethodTID = d['FullObject']['WaterLevelMethodTID']
        self.WaterLevelMethodName = d['FullObject']['WaterLevelMethodTName']
        self.MarkingReferenceTID = d['FullObject']['MarkingReferenceTID']
        self.MarkingReferenceName = d['FullObject']['MarkingReferenceTName']
        self.MarkingTypeTID = d['FullObject']['MarkingTypeTID']
        self.MarkingTypeName = d['FullObject']['MarkingTypeTName']
        self.MeasuringToolDescription = d['FullObject']['MeasuringToolDescription']

        self.WaterLevelMeasurements = []
        for m in d['FullObject']['WaterLevelMeasurement']:
            self.WaterLevelMeasurements.append(WaterLevelMeasurement(m))

        self.LangKey = d['LangKey']


class LandSlideObs(Registration, Location, Observer, Pictures):

    def __init__(self, d):

        Registration.__init__(self, d)
        Location.__init__(self, d)
        Observer.__init__(self, d)

        self.FullObject = d['FullObject']
        self.RegistrationTID = int(d['RegistrationTid'])
        self.RegistrationName = d['RegistrationName']

        Pictures.__init__(self, d, self.RegistrationTID)

        self.DtLandSlideTime = _stringtime_2_datetime(d['FullObject']['DtLandSlideTime'])
        self.DtLandSlideTimeEnd = _stringtime_2_datetime(d['FullObject']['DtLandSlideTimeEnd'])
        self.UTMNorthStop = d['FullObject']['UTMNorthStop']
        self.UTMEastStop = d['FullObject']['UTMEastStop']
        self.UTMZoneStop = d['FullObject']['UTMZoneStop']
        self.LandSlideTID = d['FullObject']['LandSlideTID']
        self.LandSlideName = d['FullObject']['LandSlideTName']
        self.LandSlideTriggerTID = d['FullObject']['LandSlideTriggerTID']
        self.LandSlideTriggerName = d['FullObject']['LandSlideTriggerTName']
        self.LandSlideSizeTID = d['FullObject']['LandSlideSizeTID']
        self.LandSlideSizeName = d['FullObject']['LandSlideSizeTName']
        # self.GeoHazardTID = d['FullObject']['GeoHazardTID']
        # self.GeoHazardName = d['FullObject']['GeoHazardTName']
        self.ActivityInfluencedTID = d['FullObject']['ActivityInfluencedTID']
        self.ActivityInfluencedName = d['FullObject']['ActivityInfluencedTName']
        self.ForecastAccurateTID = d['FullObject']['ForecastAccurateTID']
        self.ForecastAccurateName = d['FullObject']['ForecastAccurateTName']
        self.DamageExtentTID = d['FullObject']['DamageExtentTID']
        self.DamageExtentName = d['FullObject']['DamageExtentTName']
        self.UTMZoneStart = d['FullObject']['UTMZoneStart']
        self.UTMNorthStart = d['FullObject']['UTMNorthStart']
        self.UTMEastStart = d['FullObject']['UTMEastStart']
        self.Comment = d['FullObject']['Comment']

        self.URLs = []
        for u in d['FullObject']['Urls']:
            self.URLs.append({'URLLine': u['UrlLine'], 'URLDescription': u['UrlDescription']})

        self.LangKey = d['LangKey']


def _get_general(registration_class_type, registration_types, from_date, to_date, region_ids=None, location_id=None,
        observer_ids=None, observer_nick=None, observer_competence=None, group_id=None,
        output='List', geohazard_tids=None, lang_key=1):
    """Gets observations of a requested type and maps them to one requested class.

    :param registration_class_type: [class for the requested observations]
    :param registration_types:  [int] RegistrationTID for the requested observation type
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

    list = None
    if output not in ['List', 'DataFrame', 'Count']:
        ml.log_and_print('getobservations.py -> _get_general: Illegal output option.')
        return list

    # In these methods "Count" is obviously to count the list of forms, where as in the more general get_data
    # counting a list and counting a nested list of full observations are two different things.
    output_for_get_data = output
    if output == 'Count':
        output_for_get_data = 'Count list'

    # Data frames are based on the lists
    if output == 'DataFrame':
        output_for_get_data = 'List'

    data_with_more = get_data(from_date=from_date, to_date=to_date, region_ids=region_ids, observer_ids=observer_ids,
                              observer_nick=observer_nick, observer_competence=observer_competence,
                              group_id=group_id, location_id=location_id, lang_key=lang_key,
                              output=output_for_get_data, registration_types=registration_types, geohazard_tids=geohazard_tids)

    # wash out all other observation types
    data = []
    if registration_types:
        for d in data_with_more:
            if d['RegistrationTid'] == registration_types:
                data.append(d)
    else:  # registration_types is None is for all registrations and no single type is picked out.
        data = data_with_more

    if output == 'List' or output == 'DataFrame':
        list = [registration_class_type(d) for d in data]
        list = sorted(list, key=lambda registration_class_type: registration_class_type.DtObsTime)

    if output == 'List':
        return list

    if output == 'DataFrame':
        return _make_data_frame(list)

    if output == 'Count':
        return data


def get_land_slide_obs(from_date, to_date, region_ids=None, location_id=None, group_id=None,
        observer_ids=None, observer_nick=None, observer_competence=None, output='List', lang_key=1):
    """Gets observations of land slide observations in the LandSlideObs table in regObs.

    :param from_date:           [date] A query returns [from_date, to_date]
    :param to_date:             [date] A query returns [from_date, to_date]
    :param region_ids:          [int or list of ints] If region_ids = None, all regions are selected
    :param location_id:         [int] LocationID as given in the ObsLocation table in regObs.
    :param group_id:            [int] ObserverGroupID as given in the ObserverGroup table in regObs.
    :param observer_ids:        [int or list of ints] If observer_ids = None, all observers are selected
    :param observer_nick:       [int or list of ints] Default None gives all.
    :param observer_competence: [string] Part of a observer nick name
    :param output:              [string] Options: 'List', 'DataFrame' and 'Count'. Default 'List'.
    :param lang_key             [int] 1 is norwegian, 2 is english

    :return:
    """

    return _get_general(LandSlideObs, 71, from_date=from_date, to_date=to_date,
                        region_ids=region_ids, location_id=location_id, group_id=group_id,
                        observer_ids=observer_ids, observer_nick=observer_nick, observer_competence=observer_competence,
                        output=output, geohazard_tids=20, lang_key=lang_key)


def get_water_level_2(from_date, to_date, region_ids=None, location_id=None, group_id=None,
        observer_ids=None, observer_nick=None, observer_competence=None, output='List', lang_key=1):
    """Gets observations of water level from the WaterLevel2 table which was put to use in 2017.

    :param from_date:           [date] A query returns [from_date, to_date]
    :param to_date:             [date] A query returns [from_date, to_date]
    :param region_ids:          [int or list of ints] If region_ids = None, all regions are selected
    :param location_id:         [int] LocationID as given in the ObsLocation table in regObs.
    :param group_id:            [int] ObserverGroupID as given in the ObserverGroup table in regObs.
    :param observer_ids:        [int or list of ints] If observer_ids = None, all observers are selected
    :param observer_nick:       [int or list of ints] Default None gives all.
    :param observer_competence: [string] Part of a observer nick name
    :param output:              [string] Options: 'List', 'DataFrame' and 'Count'. Default 'List'.
    :param lang_key             [int] 1 is norwegian, 2 is english

    :return:
    """

    return _get_general(WaterLevel2, 62, from_date=from_date, to_date=to_date,
                        region_ids=region_ids, location_id=location_id, group_id=group_id,
                        observer_ids=observer_ids, observer_nick=observer_nick, observer_competence=observer_competence,
                        output=output, lang_key=lang_key)


def get_water_level(from_date, to_date, region_ids=None, location_id=None, group_id=None,
        observer_ids=None, observer_nick=None, observer_competence=None, output='List', lang_key=1):
    """Gets observations of water level from the WaterLevel table. Ths was the first modelling of this form and
    was phased out in 2017.

    :param from_date:           [date] A query returns [from_date, to_date]
    :param to_date:             [date] A query returns [from_date, to_date]
    :param region_ids:          [int or list of ints] If region_ids = None, all regions are selected
    :param location_id:         [int] LocationID as given in the ObsLocation table in regObs.
    :param group_id:            [int] ObserverGroupID as given in the ObserverGroup table in regObs.
    :param observer_ids:        [int or list of ints] If observer_ids = None, all observers are selected
    :param observer_nick:       [int or list of ints] Default None gives all.
    :param observer_competence: [string] Part of a observer nick name
    :param output:              [string] Options: 'List', 'DataFrame' and 'Count'. Default 'List'.
    :param lang_key             [int] 1 is norwegian, 2 is english

    :return:
    """

    return _get_general(WaterLevel, 61, from_date=from_date, to_date=to_date,
                        region_ids=region_ids, location_id=location_id, group_id=group_id,
                        observer_ids=observer_ids, observer_nick=observer_nick, observer_competence=observer_competence,
                        output=output, lang_key=lang_key)


def get_ice_cover(from_date, to_date, region_ids=None, location_id=None, group_id=None,
        observer_ids=None, observer_nick=None, observer_competence=None, output='List', lang_key=1):
    """Gets observations of ice cover from the IceCoverObs table.

    :param from_date:           [date] A query returns [from_date, to_date]
    :param to_date:             [date] A query returns [from_date, to_date]
    :param region_ids:          [int or list of ints] If region_ids = None, all regions are selected
    :param location_id:         [int] LocationID as given in the ObsLocation table in regObs.
    :param group_id:            [int] ObserverGroupID as given in the ObserverGroup table in regObs.
    :param observer_ids:        [int or list of ints] If observer_ids = None, all observers are selected
    :param observer_nick:       [int or list of ints] Default None gives all.
    :param observer_competence: [string] Part of a observer nick name
    :param output:              [string] Options: 'List', 'DataFrame' and 'Count'. Default 'List'.
    :param lang_key             [int] 1 is norwegian, 2 is english

    :return:
    """

    return _get_general(IceCover, 51, from_date=from_date, to_date=to_date,
                        region_ids=region_ids, location_id=location_id, group_id=group_id,
                        observer_ids=observer_ids, observer_nick=observer_nick, observer_competence=observer_competence,
                        output=output, lang_key=lang_key)


def get_ice_thickness(from_date, to_date, region_ids=None, location_id=None, group_id=None,
        observer_ids=None, observer_nick=None, observer_competence=None, output='List', lang_key=1):
    """Gets observations of ice thickness from the IceThicknessObs table.

    :param from_date:           [date] A query returns [from_date, to_date]
    :param to_date:             [date] A query returns [from_date, to_date]
    :param region_ids:          [int or list of ints] If region_ids = None, all regions are selected
    :param location_id:         [int] LocationID as given in the ObsLocation table in regObs.
    :param group_id:            [int] ObserverGroupID as given in the ObserverGroup table in regObs.
    :param observer_ids:        [int or list of ints] If observer_ids = None, all observers are selected
    :param observer_nick:       [int or list of ints] Default None gives all.
    :param observer_competence: [string] Part of a observer nick name
    :param output:              [string] Options: 'List', 'DataFrame' and 'Count'. Default 'List'.
    :param lang_key             [int] 1 is norwegian, 2 is english

    :return:
    """

    return _get_general(IceThickness, 50, from_date=from_date, to_date=to_date,
                        region_ids=region_ids, location_id=location_id, group_id=group_id,
                        observer_ids=observer_ids, observer_nick=observer_nick, observer_competence=observer_competence,
                        output=output, lang_key=lang_key)


def get_column_test(from_date, to_date, region_ids=None, location_id=None, group_id=None,
        observer_ids=None, observer_nick=None, observer_competence=None, output='List', lang_key=1):
    """Gets observations of snow profiles. Pr now these are provided as pictures.

    :param from_date:           [date] A query returns [from_date, to_date]
    :param to_date:             [date] A query returns [from_date, to_date]
    :param region_ids:          [int or list of ints] If region_ids = None, all regions are selected
    :param location_id:         [int] LocationID as given in the ObsLocation table in regObs.
    :param group_id:            [int] ObserverGroupID as given in the ObserverGroup table in regObs.
    :param observer_ids:        [int or list of ints] If observer_ids = None, all observers are selected
    :param observer_nick:       [int or list of ints] Default None gives all.
    :param observer_competence: [string] Part of a observer nick name
    :param output:              [string] Options: 'List', 'DataFrame' and 'Count'. Default 'List'.
    :param lang_key             [int] 1 is norwegian, 2 is english

    :return:
    """

    return _get_general(ColumnTest, 25, from_date=from_date, to_date=to_date,
                        region_ids=region_ids, location_id=location_id, group_id=group_id,
                        observer_ids=observer_ids, observer_nick=observer_nick, observer_competence=observer_competence,
                        output=output, lang_key=lang_key)


def get_snow_profile_picture(from_date, to_date, region_ids=None, location_id=None, group_id=None,
        observer_ids=None, observer_nick=None, observer_competence=None, output='List', lang_key=1):
    """Gets observations of snow profiles. Before dec 2018 these were provided as pictures.

    :param from_date:           [date] A query returns [from_date, to_date]
    :param to_date:             [date] A query returns [from_date, to_date]
    :param region_ids:          [int or list of ints] If region_ids = None, all regions are selected
    :param location_id:         [int] LocationID as given in the ObsLocation table in regObs.
    :param group_id:            [int] ObserverGroupID as given in the ObserverGroup table in regObs.
    :param observer_ids:        [int or list of ints] If observer_ids = None, all observers are selected
    :param observer_nick:       [int or list of ints] Default None gives all.
    :param observer_competence: [string] Part of a observer nick name
    :param output:              [string] Options: 'List', 'DataFrame' and 'Count'. Default 'List'.
    :param lang_key             [int] 1 is norwegian, 2 is english

    :return:
    """

    return _get_general(SnowProfilePicture, 23, from_date=from_date, to_date=to_date,
                        region_ids=region_ids, location_id=location_id, group_id=group_id,
                        observer_ids=observer_ids, observer_nick=observer_nick, observer_competence=observer_competence,
                        output=output, lang_key=lang_key)


def get_snow_profile(from_date, to_date, region_ids=None, location_id=None, group_id=None,
        observer_ids=None, observer_nick=None, observer_competence=None, output='List', lang_key=1):
    """Gets observations of snow profiles. Before dec 2018 these were provided as pictures.

    :param from_date:           [date] A query returns [from_date, to_date]
    :param to_date:             [date] A query returns [from_date, to_date]
    :param region_ids:          [int or list of ints] If region_ids = None, all regions are selected
    :param location_id:         [int] LocationID as given in the ObsLocation table in regObs.
    :param group_id:            [int] ObserverGroupID as given in the ObserverGroup table in regObs.
    :param observer_ids:        [int or list of ints] If observer_ids = None, all observers are selected
    :param observer_nick:       [int or list of ints] Default None gives all.
    :param observer_competence: [string] Part of a observer nick name
    :param output:              [string] Options: 'List', 'DataFrame' and 'Count'. Default 'List'.
    :param lang_key             [int] 1 is norwegian, 2 is english

    :return:
    """

    return _get_general(SnowProfile, 36, from_date=from_date, to_date=to_date,
                        region_ids=region_ids, location_id=location_id, group_id=group_id,
                        observer_ids=observer_ids, observer_nick=observer_nick, observer_competence=observer_competence,
                        output=output, lang_key=lang_key)


def get_damage_observation(from_date, to_date, region_ids=None, location_id=None, group_id=None,
        observer_ids=None, observer_nick=None, observer_competence=None, output='List', geohazard_tids=None, lang_key=1):
    """Gets observations like given in SnowSurfaceObservation table with RegistrationTID = 22.
    View is shared by all the geohazards so the filter includes geohazard_tid if only some geohazards are needed.

    :param from_date:           [date] A query returns [from_date, to_date]
    :param to_date:             [date] A query returns [from_date, to_date]
    :param region_ids:          [int or list of ints] If region_ids = None, all regions are selected
    :param location_id:         [int] LocationID as given in the ObsLocation table in regObs.
    :param group_id:            [int] ObserverGroupID as given in the ObserverGroup table in regObs.
    :param observer_ids:        [int or list of ints] If observer_ids = None, all observers are selected
    :param observer_nick:       [int or list of ints] Default None gives all.
    :param observer_competence: [string] Part of a observer nick name
    :param output:              [string] Options: 'List', 'DataFrame' and 'Count'. Default 'List'.
    :param geohazard_tids:      [int or list of ints] Default None gives all.
    :param lang_key             [int] 1 is norwegian, 2 is english

    :return:
    """

    return _get_general(DamageObs, 14, from_date=from_date, to_date=to_date,
                        region_ids=region_ids, location_id=location_id, group_id=group_id,
                        observer_ids=observer_ids, observer_nick=observer_nick, observer_competence=observer_competence,
                        output=output, geohazard_tids=geohazard_tids, lang_key=lang_key)


def get_snow_surface_observation(from_date, to_date, region_ids=None, location_id=None, group_id=None,
        observer_ids=None, observer_nick=None, observer_competence=None, output='List', lang_key=1):
    """Gets observations like given in SnowSurfaceObservation table with RegistrationTID = 22.
    View is used by GeoHazard = 10 (snow).

    :param from_date:           [date] A query returns [from_date, to_date]
    :param to_date:             [date] A query returns [from_date, to_date]
    :param region_ids:          [int or list of ints] If region_ids = None, all regions are selected
    :param location_id:         [int] LocationID as given in the ObsLocation table in regObs.
    :param group_id:            [int] ObserverGroupID as given in the ObserverGroup table in regObs.
    :param observer_ids:        [int or list of ints] If observer_ids = None, all observers are selected
    :param observer_nick:       [int or list of ints] Default None gives all.
    :param observer_competence: [string] Part of a observer nick name
    :param output:              [string] Options: 'List', 'DataFrame' and 'Count'. Default 'List'.
    :param lang_key             [int] 1 is norwegian, 2 is english

    :return:
    """

    return _get_general(SnowSurfaceObservation, 22, from_date=from_date, to_date=to_date,
                        region_ids=region_ids, location_id=location_id, group_id=group_id,
                        observer_ids=observer_ids, observer_nick=observer_nick, observer_competence=observer_competence,
                        output=output, geohazard_tids=10, lang_key=lang_key)


def get_weather_observation(from_date, to_date, region_ids=None, location_id=None, group_id=None,
        observer_ids=None, observer_nick=None, observer_competence=None, output='List', lang_key=1):
    """Gets observations like given in WeatherObservation table with RegistrationTID = 21.
    View is used by GeoHazard = 10 (snow).

    :param from_date:           [date] A query returns [from_date, to_date]
    :param to_date:             [date] A query returns [from_date, to_date]
    :param region_ids:          [int or list of ints] If region_ids = None, all regions are selected
    :param location_id:         [int] LocationID as given in the ObsLocation table in regObs.
    :param group_id:            [int] ObserverGroupID as given in the ObserverGroup table in regObs.
    :param observer_ids:        [int or list of ints] If observer_ids = None, all observers are selected
    :param observer_nick:       [int or list of ints] Default None gives all.
    :param observer_competence: [string] Part of a observer nick name
    :param output:              [string] Options: 'List', 'DataFrame' and 'Count'. Default 'List'.
    :param lang_key             [int] 1 is norwegian, 2 is english

    :return:
    """

    return _get_general(WeatherObservation, 21, from_date=from_date, to_date=to_date,
                        region_ids=region_ids, location_id=location_id, group_id=group_id,
                        observer_ids=observer_ids, observer_nick=observer_nick, observer_competence=observer_competence,
                        output=output, geohazard_tids=10, lang_key=lang_key)


def get_picture(from_date, to_date, region_ids=None, location_id=None, group_id=None,
        observer_ids=None, observer_nick=None, observer_competence=None, output='List', geohazard_tids=None, lang_key=1):
    """Gets observations like given in Picture table with RegistrationTID = 12.
    View is shared by all the geohazards so the filter includes geohazard_tid if only some geohazards are needed.

    :param from_date:           [date] A query returns [from_date, to_date]
    :param to_date:             [date] A query returns [from_date, to_date]
    :param region_ids:          [int or list of ints] If region_ids = None, all regions are selected
    :param location_id:         [int] LocationID as given in the ObsLocation table in regObs.
    :param group_id:            [int] ObserverGroupID as given in the ObserverGroup table in regObs.
    :param observer_ids:        [int or list of ints] If observer_ids = None, all observers are selected
    :param observer_nick:       [int or list of ints] Default None gives all.
    :param observer_competence: [string] Part of a observer nick name
    :param output:              [string] Options: 'List', 'DataFrame' and 'Count'. Default 'List'.
    :param geohazard_tids:      [int or list of ints] Default None gives all.
    :param lang_key             [int] 1 is norwegian, 2 is english

    :return:
    """

    return _get_general(PictureObservation, 12, from_date=from_date, to_date=to_date,
                        region_ids=region_ids, location_id=location_id, group_id=group_id,
                        observer_ids=observer_ids, observer_nick=observer_nick, observer_competence=observer_competence,
                        output=output, geohazard_tids=geohazard_tids, lang_key=lang_key)


def get_general_observation(from_date, to_date, region_ids=None, location_id=None, group_id=None,
        observer_ids=None, observer_nick=None, observer_competence=None, output='List', geohazard_tids=None, lang_key=1):
    """Gets observations like given in GeneralObs table with RegistrationTID = 10.
    View is shared by all the geo hazards so the filter includes geohazard_tid if only some geohazards are needed.

    :param from_date:           [date] A query returns [from_date, to_date]
    :param to_date:             [date] A query returns [from_date, to_date]
    :param region_ids:          [int or list of ints] If region_ids = None, all regions are selected
    :param location_id:         [int] LocationID as given in the ObsLocation table in regObs.
    :param group_id:            [int] ObserverGroupID as given in the ObserverGroup table in regObs.
    :param observer_ids:        [int or list of ints] If observer_ids = None, all observers are selected
    :param observer_nick:       [int or list of ints] Default None gives all.
    :param observer_competence: [string] Part of a observer nick name
    :param output:              [string] Options: 'List', 'DataFrame' and 'Count'. Default 'List'.
    :param geohazard_tids:      [int or list of ints] Default None gives all.
    :param lang_key             [int] 1 is norwegian, 2 is english

    :return:
    """

    return _get_general(GeneralObservation, 10, from_date=from_date, to_date=to_date,
                        region_ids=region_ids, location_id=location_id, group_id=group_id,
                        observer_ids=observer_ids, observer_nick=observer_nick, observer_competence=observer_competence,
                        output=output, geohazard_tids=geohazard_tids, lang_key=lang_key)


def get_all_registrations(from_date, to_date, region_ids=None, location_id=None, group_id=None,
        observer_ids=None, observer_nick=None, observer_competence=None, output='List', geohazard_tids=None, lang_key=1):
    """Gets observations like given in AllRegistrationsV. View is shared by all the geohazards so the filter
    includes geohazard_tid if only some geohazards are needed.

    :param from_date:           [date] A query returns [from_date, to_date]
    :param to_date:             [date] A query returns [from_date, to_date]
    :param region_ids:          [int or list of ints] If region_ids = None, all regions are selected
    :param location_id:         [int] LocationID as given in the ObsLocation table in regObs.
    :param group_id:            [int] ObserverGroupID as given in the ObserverGroup table in regObs.
    :param observer_ids:        [int or list of ints] If observer_ids = None, all observers are selected
    :param observer_nick:       [int or list of ints] Default None gives all.
    :param observer_competence: [string] Part of a observer nick name
    :param output:              [string] Options: 'List', 'DataFrame' and 'Count'. Default 'List'.
    :param geohazard_tids:      [int or list of ints] Default None gives all.
    :param lang_key             [int] 1 is norwegian, 2 is english

    :return:
    """

    return _get_general(AllRegistrations, None, from_date=from_date, to_date=to_date,
                        region_ids=region_ids, location_id=location_id, group_id=group_id,
                        observer_ids=observer_ids, observer_nick=observer_nick, observer_competence=observer_competence,
                        output=output, geohazard_tids=geohazard_tids, lang_key=lang_key)


def get_danger_sign(from_date, to_date, region_ids=None, location_id=None, group_id=None,
        observer_ids=None, observer_nick=None, observer_competence=None, output='List', geohazard_tids=None, lang_key=1):
    """Gets observations like given in DangerObsV table with RegistrationTID = 13.
    View is shared by all the geohazards so the filter includes geohazard_tid if only some geohazards are needed.

    :param from_date:           [date] A query returns [from_date, to_date]
    :param to_date:             [date] A query returns [from_date, to_date]
    :param region_ids:          [int or list of ints] If region_ids = None, all regions are selected
    :param location_id:         [int] LocationID as given in the ObsLocation table in regObs.
    :param group_id:            [int] ObserverGroupID as given in the ObserverGroup table in regObs.
    :param observer_ids:        [int or list of ints] If observer_ids = None, all observers are selected
    :param observer_nick:       [int or list of ints] Default None gives all.
    :param observer_competence: [string] Part of a observer nick name
    :param output:              [string] Options: 'List', 'DataFrame' and 'Count'. Default 'List'.
    :param geohazard_tids:         [int or list of ints] Default None gives all.
    :param lang_key             [int] 1 is norwegian, 2 is english

    :return:
    """

    return _get_general(DangerSign, 13, from_date=from_date, to_date=to_date,
                        region_ids=region_ids, location_id=location_id, group_id=group_id,
                        observer_ids=observer_ids, observer_nick=observer_nick, observer_competence=observer_competence,
                        output=output, geohazard_tids=geohazard_tids, lang_key=lang_key)


def get_incident(from_date, to_date, region_ids=None, location_id=None, group_id=None,
        observer_ids=None, observer_nick=None, observer_competence=None, output='List', geohazard_tids=None, lang_key=1):
    """Gets observations like given the Incident table with RegistrationTID = 11.
    Table is shared by all the geohazards so the filter includes geohazard_tid if only some geohazards are needed.

    :param from_date:           [date] A query returns [from_date, to_date]
    :param to_date:             [date] A query returns [from_date, to_date]
    :param region_ids:          [int or list of ints] If region_ids = None, all regions are selected
    :param location_id:         [int] LocationID as given in the ObsLocation table in regObs.
    :param group_id:            [int] ObserverGroupID as given in the ObserverGroup table in regObs.
    :param observer_ids:        [int or list of ints] If observer_ids = None, all observers are selected
    :param observer_nick:       [int or list of ints] Default None gives all.
    :param observer_competence: [string] Part of a observer nick name
    :param output:              [string] Options: 'List', 'DataFrame' and 'Count'. Default 'List'.
    :param geohazard_tids:      [int or list of ints] Default None gives all.
    :param lang_key             [int] 1 is norwegian, 2 is english

    :return:
    """

    return _get_general(Incident, 11, from_date=from_date, to_date=to_date,
                        region_ids=region_ids, location_id=location_id, group_id=group_id,
                        observer_ids=observer_ids, observer_nick=observer_nick, observer_competence=observer_competence,
                        output=output, geohazard_tids=geohazard_tids, lang_key=lang_key)


def get_avalanche(from_date, to_date, region_ids=None, location_id=None, group_id=None,
        observer_ids=None, observer_nick=None, observer_competence=None, output='List', lang_key=1):
    """Gets observations as given in the AvalancheObs table with RegistrationTID = 26.
    These are observations of single avalanches, often related to incidents. It is specific for snow observations.

    :param from_date:           [date] A query returns [from_date, to_date]
    :param to_date:             [date] A query returns [from_date, to_date]
    :param region_ids:          [int or list of ints] If region_ids = None, all regions are selected
    :param location_id:         [int] LocationID as given in the ObsLocation table in regObs.
    :param group_id:            [int] ObserverGroupID as given in the ObserverGroup table in regObs.
    :param observer_ids:        [int or list of ints] If observer_ids = None, all observers are selected
    :param observer_nick:       [int or list of ints] Default None gives all.
    :param observer_competence: [string] Part of a observer nick name
    :param output:              [string] Options: 'List', 'DataFrame' and 'Count'. Default 'List'.
    :param lang_key             [int] 1 is norwegian, 2 is english

    :return:
    """

    return _get_general(AvalancheObs, 26, from_date=from_date, to_date=to_date,
                        region_ids=region_ids, location_id=location_id, group_id=group_id,
                        observer_ids=observer_ids, observer_nick=observer_nick, observer_competence=observer_competence,
                        output=output, lang_key=lang_key)


def get_avalanche_activity(from_date, to_date, region_ids=None, location_id=None, group_id=None,
        observer_ids=None, observer_nick=None, observer_competence=None, output='List', lang_key=1):
    """Gets observations as given in AvalancheActivityObs table with RegistrationTID = 27.
    It is specific for snow observations. The table was introduced at the beginning an phased out in in january 2016.

    :param from_date:           [date] A query returns [from_date, to_date]
    :param to_date:             [date] A query returns [from_date, to_date]
    :param region_ids:          [int or list of ints] If region_ids = None, all regions are selected
    :param location_id:         [int] LocationID as given in the ObsLocation table in regObs.
    :param group_id:            [int] ObserverGroupID as given in the ObserverGroup table in regObs.
    :param observer_ids:        [int or list of ints] If observer_ids = None, all observers are selected
    :param observer_nick:       [int or list of ints] Default None gives all.
    :param observer_competence: [string] Part of a observer nick name
    :param output:              [string] Options: 'List', 'DataFrame' and 'Count'. Default 'List'.
    :param lang_key             [int] 1 is norwegian, 2 is english

    :return:
    """

    return _get_general(AvalancheActivityObs, 27, from_date=from_date, to_date=to_date,
                        region_ids=region_ids, location_id=location_id, group_id=group_id,
                        observer_ids=observer_ids, observer_nick=observer_nick, observer_competence=observer_competence,
                        output=output, lang_key=lang_key)


def get_avalanche_activity_2(from_date, to_date, region_ids=None, location_id=None, group_id=None,
        observer_ids=None, observer_nick=None, observer_competence=None, output='List', lang_key=1):
    """Gets observations like given in AvalancheActivityObs2 table with RegistrationTID = 33.
    It is specific for snow observations. The table was introduced in january 2016.

    :param from_date:           [date] A query returns [from_date, to_date]
    :param to_date:             [date] A query returns [from_date, to_date]
    :param region_ids:          [int or list of ints] If region_ids = None, all regions are selected
    :param location_id:         [int] LocationID as given in the ObsLocation table in regObs.
    :param group_id:            [int] ObserverGroupID as given in the ObserverGroup table in regObs.
    :param observer_ids:        [int or list of ints] If observer_ids = None, all observers are selected
    :param observer_nick:       [int or list of ints] Default None gives all.
    :param observer_competence: [string] Part of a observer nick name
    :param output:              [string] Options: 'List', 'DataFrame' and 'Count'. Default 'List'.
    :param lang_key             [int] 1 is norwegian, 2 is english

    :return:
    """

    return _get_general(AvalancheActivityObs2, 33, from_date=from_date, to_date=to_date,
                        region_ids=region_ids, location_id=location_id, group_id=group_id,
                        observer_ids=observer_ids, observer_nick=observer_nick, observer_competence=observer_competence,
                        output=output, lang_key=lang_key)


def get_avalanche_evaluation(from_date, to_date, region_ids=None, location_id=None, group_id=None,
        observer_ids=None, observer_nick=None, observer_competence=None, output='List', lang_key=1):
    """Gets observations like given in AvalancheEvaluation table with RegistrationTID = 28.
    It contains avalanche problems. It is specific for snow observations.
    The table was used winter and spring 2012. Last observatins jan/beb 2013 by drift@svv..

    :param from_date:           [date] A query returns [from_date, to_date]
    :param to_date:             [date] A query returns [from_date, to_date]
    :param region_ids:          [int or list of ints] If region_ids = None, all regions are selected
    :param location_id:         [int] LocationID as given in the ObsLocation table in regObs.
    :param group_id:            [int] ObserverGroupID as given in the ObserverGroup table in regObs.
    :param observer_ids:        [int or list of ints] If observer_ids = None, all observers are selected
    :param observer_nick:       [int or list of ints] Default None gives all.
    :param observer_competence: [string] Part of a observer nick name
    :param output:              [string] Options: 'List', 'DataFrame' and 'Count'. Default 'List'.
    :param lang_key             [int] 1 is norwegian, 2 is english

    :return:
    """

    return _get_general(AvalancheEvaluation, 28, from_date=from_date, to_date=to_date,
                        region_ids=region_ids, location_id=location_id, group_id=group_id,
                        observer_ids=observer_ids, observer_nick=observer_nick, observer_competence=observer_competence,
                        output=output, lang_key=lang_key)


def get_avalanche_evaluation_2(from_date, to_date, region_ids=None, location_id=None, group_id=None,
        observer_ids=None, observer_nick=None, observer_competence=None, output='List', lang_key=1):
    """Gets observations like given in AvalancheEvaluation2 table with RegistrationTID = 30.
    It contains the avalanche problems used at the time. It is specific for snow observations.
    The table was introduced December 2012 and phased out winter 2014. It was last used May 2014.

    :param from_date:           [date] A query returns [from_date, to_date]
    :param to_date:             [date] A query returns [from_date, to_date]
    :param region_ids:          [int or list of ints] If region_ids = None, all regions are selected
    :param location_id:         [int] LocationID as given in the ObsLocation table in regObs.
    :param group_id:            [int] ObserverGroupID as given in the ObserverGroup table in regObs.
    :param observer_ids:        [int or list of ints] If observer_ids = None, all observers are selected
    :param observer_nick:       [int or list of ints] Default None gives all.
    :param observer_competence: [string] Part of a observer nick name
    :param output:              [string] Options: 'List', 'DataFrame' and 'Count'. Default 'List'.
    :param lang_key             [int] 1 is norwegian, 2 is english

    :return:
    """

    return _get_general(AvalancheEvaluation2, 30, from_date=from_date, to_date=to_date,
                        region_ids=region_ids, location_id=location_id, group_id=group_id,
                        observer_ids=observer_ids, observer_nick=observer_nick, observer_competence=observer_competence,
                        output=output, lang_key=lang_key)


def get_avalanche_evaluation_3(from_date, to_date, region_ids=None, location_id=None, group_id=None,
        observer_ids=None, observer_nick=None, observer_competence=None, output='List', lang_key=1):
    """Gets observations like given in AvalancheEvaluation3 table with RegistrationTID = 31.
    It is specific for snow observations. The table was introduced in february 2014.

    :param from_date:           [date] A query returns [from_date, to_date]
    :param to_date:             [date] A query returns [from_date, to_date]
    :param region_ids:          [int or list of ints] If region_ids = None, all regions are selected
    :param location_id:         [int] LocationID as given in the ObsLocation table in regObs.
    :param group_id:            [int] ObserverGroupID as given in the ObserverGroup table in regObs.
    :param observer_ids:        [int or list of ints] If observer_ids = None, all observers are selected
    :param observer_nick:       [int or list of ints] Default None gives all.
    :param observer_competence: [string] Part of a observer nick name
    :param output:              [string] Options: 'List', 'DataFrame' and 'Count'. Default 'List'.
    :param lang_key             [int] 1 is norwegian, 2 is english

    :return:
    """

    return _get_general(AvalancheEvaluation3, 31, from_date=from_date, to_date=to_date,
                        region_ids=region_ids, location_id=location_id, group_id=group_id,
                        observer_ids=observer_ids, observer_nick=observer_nick, observer_competence=observer_competence,
                        output=output, lang_key=lang_key)


def get_avalanche_problem_2(from_date, to_date, region_ids=None, location_id=None, group_id=None,
        observer_ids=None, observer_nick=None, observer_competence=None, output='List', lang_key=1):
    """Gets observations given in AvalancheEvalProblem2 table with RegistrationTID = 31. It is specific for snow observations.
    The table was introduced winter 2014 with the first observation was February 2014. It is currently in use (Oct 2017).

    :param from_date:           [date] A query returns [from_date, to_date]
    :param to_date:             [date] A query returns [from_date, to_date]
    :param region_ids:          [int or list of ints] If region_ids = None, all regions are selected
    :param location_id:         [int] LocationID as given in the ObsLocation table in regObs.
    :param group_id:            [int] ObserverGroupID as given in the ObserverGroup table in regObs.
    :param observer_ids:        [int or list of ints] If observer_ids = None, all observers are selected
    :param observer_nick:       [int or list of ints] Default None gives all.
    :param observer_competence: [string] Part of a observer nick name
    :param output:              [string] Options: 'List', 'DataFrame' and 'Count'. Default 'List'.
    :param lang_key             [int] 1 is norwegian, 2 is english

    :return:
    """

    return _get_general(AvalancheEvalProblem2, 32, from_date=from_date, to_date=to_date,
                        region_ids=region_ids, location_id=location_id, group_id=group_id,
                        observer_ids=observer_ids, observer_nick=observer_nick, observer_competence=observer_competence,
                        output=output, lang_key=lang_key)


def _raw_play_ground():
    """Method for testing requests to regobs web-api directly."""

    data = []  # data from one query

    # query object posted in the request
    rssquery = {'LangKey': 1,
    #            'RegId': 176528,
    #            'ObserverGuid': None,               # '4d11f3cc-07c5-4f43-837a-6597d318143c',
                'SelectedRegistrationTypes': [{'Id': 82, 'SubTypes': [36]}], #_reg_types_dict([10, 11, 12, 13]),    # list dict with type and sub type
    #            'SelectedRegions': None,
    #            'SelectedGeoHazards': [60],         # list int
    #            'ObserverNickName': None,           # "jostein",
    #            'ObserverId': None,
    #            'ObserverCompetence': None,         # list int
    #            'GroupId': None,
    #            'LocationId': None,
                'FromDate': '2018-12-13',
                'ToDate': '2018-12-16',
                'NumberOfRecords': None,            # int
    #            'TextSearch': None,                 # virker ikke
                'Offset': 0}

    url = 'https://api.nve.no/hydrology/regobs/webapi_{0}/Search/All'.format(env.web_api_version)
    # url = 'https://api.nve.no/hydrology/regobs/webapi_v3.2.0/Search/Rss?geoHazard=0'
    # url = 'http://tst-h-web03.nve.no/regobswebapi/Search/Rss?geoHazard=0'

    more_available = True

    # get data from regObs api. It returns 100 items at a time. If more, continue requesting with an offset. Paging.
    while more_available:

        r = requests.post(url, json=rssquery)
        responds = r.json()
        data += responds['Results']

        if responds['TotalMatches'] == 0:
            print('No data')
        else:
            print('{0:.2f}%'.format(len(data) / responds['TotalMatches'] * 100))

        if len(data) < responds['TotalMatches']:
            rssquery["Offset"] += 100
        else:
            more_available = False

    return data


def _example_webapi_request():
    """Method for testing requests to regobs web-api directly."""

    data = []  # data from one query

    # query object posted in the request
    rssquery = {'LangKey': 1,                       # Int. 1 is norwegian
    #             'SelectedRegistrationTypes': [{'Id': 83, 'SubTypes': [30]}],  # list of dict with observation type and sub type
    #             'SelectedRegions': None,
                'SelectedGeoHazards': [10],         # list int. 10 is snow
    #             'ObserverNickName': None,           # String. Part of observer nick name. Eg. "NGI",
    #             'ObserverCompetence': None,         # list int
                'FromDate': '2017-12-02',
                'ToDate': '2017-12-05',
                'NumberOfRecords': None,            # int. How many records are to be returned pr request. Default 100.
                'Offset': 0}

    url = 'https://api.nve.no/hydrology/regobs/webapi_v3.2.0/Search/All'

    more_available = True       # while true, request more observations

    # get data from regObs api. It returns 100 items at a time. If more, continue requesting with an offset. Paging.
    while more_available:

        r = requests.post(url, json=rssquery)
        responds = r.json()
        data += responds['Results']

        if responds['TotalMatches'] == 0:
            print('No data')
        else:
            print('{0:.2f}%'.format(len(data) / responds['TotalMatches'] * 100))

        if len(data) < responds['TotalMatches']:
            rssquery['Offset'] += 100
        else:
            more_available = False

    return data


def _the_simplest_webapi_request():
    """Example for demonstrating how simple an request to regObs web-api can be."""

    import requests as rq

    query = {'LangKey': 2,
             'FromDate': '2018-03-01',
             'ToDate': '2018-03-04',
             'NumberOfRecords': 500}

    url = 'https://api.nve.no/hydrology/' \
          'regobs/webapi_v3.2.0/' \
          'Search/Rss?geoHazard=10'

    observations = rq.post(url, json=query).json()

    a = observations
    pass


def _test_diff_in_reg_type_query():
    """Test the difference between two requests.
    """
    data1 = get_data(from_date='2017-03-01', to_date='2017-04-01', registration_types=[{'Id': 81, 'SubTypes': [13]}],
                     geohazard_tids=10, output='Nest')
    data2 = get_data(from_date='2017-03-01', to_date='2017-04-01', registration_types=[{'SubTypes': [13]}],
                     geohazard_tids=10, output='Nest')
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

    # data = get_data_as_class('2016-12-10', '2016-12-15')

    # all_data_snow = get_data('2016-12-30', '2017-01-01', geohazard_tids=10)
    # land_slides = get_land_slide_obs('2018-01-01', '2018-02-01')
    # incident = get_incident('2012-03-01', '2012-03-10')
    # new_water_levels = get_water_level_2('2017-06-01', '2018-02-01')
    # water_levels = get_water_level('2015-01-01', '2016-01-01')
    # ice_cover = get_ice_cover('2018-01-20', '2018-02-10')
    # ice_thicks = get_ice_thickness('2018-01-20', '2018-02-10')
    # columns = get_column_test('2018-01-20', '2018-02-10')
    # old_snow_profiles = get_snow_profile_picture('2018-01-25', '2018-02-05')
    # snow_profiles = get_snow_profile('2018-12-13', '2018-12-16')
    # general = _get_general(AllRegistrations, None, '2018-01-21', '2018-02-01')
    # damages = get_damage_observation('2017-01-01', '2018-02-01')
    # snow_surface = get_snow_surface_observation('2018-01-28', '2018-02-01')
    # weather = get_weather_observation('2018-01-28', '2018-02-01')
    # pictures = get_picture('2018-01-28', '2018-02-01')
    # general_obs = get_general_observation('2018-01-20', '2018-02-01')
    # danger_signs = get_danger_sign('2017-12-13', '2017-12-16', geohazard_tids=10)
    # avalanche_activity = get_avalanche_activity('2015-03-01', '2015-03-10')
    # avalanche_activity_2 = get_avalanche_activity_2('2017-03-01', '2017-03-10')
    # avalanche_obs = get_avalanche('2015-03-01', '2015-03-10')
    # problems = get_avalanche_problem_2('2017-03-01', '2017-03-10')
    # danger_signs_data = get_data('2017-03-01', '2017-04-01', geohazard_tids=10, output='Count nest', registration_types=13)
    # avalanche_evaluations_3 = get_avalanche_evaluation_3('2017-03-01', '2017-03-10')
    # avalanche_evaluations_2 = get_avalanche_evaluation_2('2013-03-01', '2013-03-10')
    # avalanche_evaluations   = get_avalanche_evaluation('2012-03-01', '2012-03-10')
    # registrations_ice = get_all_registrations(from_date='2016-10-01', to_date='2016-11-01', geohazard_tids=70)
    # count_ice = get_all_registrations(from_date='2016-10-01', to_date='2016-11-01', geohazard_tids=70, output='Count')
    # my_observations = get_all_registrations(from_date=dt.date(2015, 6, 1), to_date=dt.date(2016, 7, 1), geohazard_tids=10, observer_ids=[6, 7, 236], output='List', region_ids=[3011, 3014, 3015])
    # count_registrations_snow_10 = get_all_registrations(dt.date(2017, 6, 1), dt.date.today(), geohazard_tids=10, output='Count', observer_nick='obskorps')
    # seasonal_count_regs = get_all_registrations('2016-08-01', '2017-08-01', output='Count')
    # one_obs = get_data(reg_ids=130548)
    # two_obs = get_data(reg_ids=[130548, 130328], output='Nest')
    # two_obs_count = get_data(reg_ids=[130548, 130328],  output='Count nest')
    # two_observers = get_data(from_date='2016-12-30', to_date='2017-04-01', observer_ids=[6,10], output='Nest')
    # one_observer_count_list = get_data(from_date='2016-12-30', to_date='2017-04-01', observer_ids=6, output='Count list')
    # one_observer_count_nest = get_data(from_date='2012-01-01', to_date='2018-01-01', observer_ids=6, output='Count nest')
    # ice_data = get_data(from_date='2016-10-01', to_date='2016-11-01', geohazard_tids=70, output='Nest')

    # data = _raw_play_ground()
    # _the_simplest_webapi_request()

    pass

