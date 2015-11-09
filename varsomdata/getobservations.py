# -*- coding: utf-8 -*-
__author__ = 'raek'


import datetime as dt
import requests as requests
import types as types

import fencoding as fe
import setenvironment as env
import getkdvelements as kdv
from getkdvelements import KDVelement


def _unix_time_2_normal(unix_date_time):
    """
    Takes in a date in unix datetime and returns a "normal date"

    :param unix_date_time:    Unix date time in milliseconds from 1.1.1970
    :return:                The date as datetime object

    Ex: date = unix_time_2_normal(int(p['DtObsTime'][6:-2]))
    """

    unix_datetime_in_seconds = unix_date_time/1000 # For some reason they are given in miliseconds
    date = dt.datetime.fromtimestamp(int(unix_datetime_in_seconds))
    return date


def _make_request(view, region_ids, from_date, to_date):
    """Common part of all data requests

    :param view:
    :param region_id:
    :param from_date:   [date]
    :param end_date:    [date]
    :return:
    """

    # If input isn't a list, make it so
    if not isinstance(region_ids, types.ListType):
        region_ids = [region_ids]

    data_out = []

    for region_id in region_ids:

        if not region_id == 0:
            forecast_region_kdv = kdv.get_kdv("ForecastRegionKDV")
            region_name = forecast_region_kdv[region_id].Name
            odata_query = "DtObsTime gt datetime'{1}' and " \
                         "DtObsTime lt datetime'{2}' and " \
                         "ForecastRegionName eq '{0}' and " \
                         "LangKey eq 1".format(region_name, from_date, to_date)
        else:
            odata_query = "DtObsTime gt datetime'{0}' and " \
                         "DtObsTime lt datetime'{1}' and " \
                         "LangKey eq 1".format(from_date, to_date)
        odata_query = fe.add_norwegian_letters(odata_query)

        url = "http://api.nve.no/hydrology/regobs/{0}/Odata.svc/{1}?$filter={2}&$format=json".decode('utf8').format(
            env.api_version, view, odata_query)

        print "getobservations.py -> _make_request: ..to {0}".format(fe.remove_norwegian_letters(url))

        result = requests.get(url).json()
        result = result['d']['results']

        # if more than 1000 elements are requested, odata truncates data to 1000. We do more requests
        if len(result) == 1000:
            time_delta = to_date - from_date
            date_in_middle = from_date + time_delta/2
            result = _make_request(view, region_id, from_date, date_in_middle) \
                   + _make_request(view, region_id, date_in_middle, to_date)

        data_out += result

    env.log.append("{2} to {3}: {1} has {0} problems".format(len(data_out), view, from_date, to_date))

    return data_out


class Registration():

    def __init__(self, RegID, DtObsTime, DtRegTime):

        self.RegID = int(RegID)
        self.DtObsTime = _unix_time_2_normal( int(DtObsTime[6:-2]) )
        self.DtRegTime = _unix_time_2_normal( int(DtRegTime[6:-2]) )

class Location():

    def __init__(self, LocationName, UTMZone, UTMEast, UTMNorth, ForecastRegionName, MunicipalName):

        self.LocationName = fe.remove_norwegian_letters(LocationName)
        self.UTMZone = int(UTMZone)
        self.UTMEast = int(UTMEast)
        self.UTMNorth = int(UTMNorth)
        self.ForecastRegionName = fe.remove_norwegian_letters(ForecastRegionName)
        self.MunicipalName = fe.remove_norwegian_letters(MunicipalName)

class Observer():

    def __init__(self, NickName, CompetenceLevelName):

        self.NickName = fe.remove_norwegian_letters(NickName)
        self.CompetenceLevelName = fe.remove_norwegian_letters(CompetenceLevelName)


class AvalancheActivityObs(Registration, Location, Observer):

    def __init__(self, d):
        Registration.__init__(self, d['RegID'], d['DtObsTime'], d['DtRegTime'])
        Location.__init__(self, d['LocationName'], d['UTMZone'], d['UTMEast'],
                                d['UTMNorth'], d['ForecastRegionName'], d['MunicipalName'])
        Observer.__init__(self, d['NickName'], d['CompetenceLevelName'])
        self.AvalancheActivityCode = d['AvalancheActivityCode']
        self.EstimatedNumName = fe.remove_norwegian_letters(d['EstimatedNumName'])
        self.DestructiveSizeName = fe.remove_norwegian_letters(d['DestructiveSizeName'])
        self.Aspect = fe.remove_norwegian_letters(d['Aspect'])
        self.HeightStartingZone = d['HeightStartingZone']
        self.AvalancheName = fe.remove_norwegian_letters(d['AvalancheName'])
        self.AvalancheTriggerName = fe.remove_norwegian_letters(d['AvalancheTriggerName'])
        self.TerrainStartingZone = fe.remove_norwegian_letters(d['TerrainStartingZone'])
        self.DtAvalancheTime = _unix_time_2_normal(int(d['DtAvalancheTime'][6:-2]))
        self.Snowline = d['Snowline']
        self.Comment = fe.remove_norwegian_letters(d['Comment'])
        self.LangKey = d['LangKey']
def get_avalanche_activity(region_id, from_date, to_date):
    """Gets observations from AvalancheActivityObsV of a region og list of regions.

    :param region_id:   [int or list of ints]
    :param from_date:   [date]
    :param to_date:     [date]

    :return:
    """

    data = _make_request("AvalancheActivityObsV", region_id, from_date, to_date)
    list = []

    for d in data:
        list.append(AvalancheActivityObs(d))

    list = sorted(list, key=lambda AvalancheActivity: AvalancheActivity.DtObsTime)

    return list


class AvalancheObs(Registration, Location, Observer):

    def __init__(self, d):
        Registration.__init__(self, d['RegID'], d['DtObsTime'], d['DtRegTime'])
        Location.__init__(self, d['LocationName'], d['UTMZone'], d['UTMEast'],
                                d['UTMNorth'], d['ForecastRegionName'], d['MunicipalName'])
        Observer.__init__(self, d['NickName'], d['CompetenceLevelName'])

        self.AvalancheName = fe.remove_norwegian_letters(d['AvalancheName'])
        self.AvalancheTriggerName = fe.remove_norwegian_letters(d['AvalancheTriggerName'])
        self.Comment = fe.remove_norwegian_letters(d['Comment'])
        self.DestructiveSizeName = fe.remove_norwegian_letters(d['DestructiveSizeName'])
        self.DtAvalancheTime = _unix_time_2_normal(int(d['DtAvalancheTime'][6:-2]))
        self.HeightStartZone = d['HeigthStartZone']
        self.HeightStopZone = d['HeigthStopZone']
        self.LangKey = d['LangKey']
        self.SnowLine = d['SnowLine']
        self.TerrainStartZoneName = fe.remove_norwegian_letters(d['TerrainStartZoneName'])
        self.UTMEastStop = d['UTMEastStop']
        self.UTMNorthStop = d['UTMNorthStop']
        self.UTMZoneStop = d['UTMZoneStop']
def get_avalanche(region_id, from_date, to_date):
    """Gets observations from AvalancheObsV of a region og list of regions.

    :param region_id:   [int or list of ints]
    :param from_date:   [date]
    :param to_date:     [date]

    :return:
    """

    data = _make_request("AvalancheObsV", region_id, from_date, to_date)
    list = []

    for d in data:
        list.append(AvalancheObs(d))

    list = sorted(list, key=lambda AvalancheObs: AvalancheObs.DtObsTime)

    return list


class DangerObs(Registration, Location, Observer):

    def __init__(self, d):
        Registration.__init__(self, d['RegID'], d['DtObsTime'], d['DtRegTime'])
        Location.__init__(self, d['LocationName'], d['UTMZone'], d['UTMEast'],
                                d['UTMNorth'], d['ForecastRegionName'], d['MunicipalName'])
        Observer.__init__(self, d['NickName'], d['CompetenceLevelName'])

        self.Comment = fe.remove_norwegian_letters(d['Comment'])
        self.DangerObsID = d['DangerObsID']
        self.DangerSignName = d['DangerSignName']
        self.DangerSignTID = d['DangerSignTID']
        self.GeoHazardName = d['GeoHazardName']
        self.GeoHazardTID = d['GeoHazardTID']
        self.LangKey = d['LangKey']
def get_danger_sign(region_id, from_date, to_date):
    """Gets observations from DangerObsV of a region og list of regions.

    :param region_id:   [int or list of ints]
    :param from_date:   [date]
    :param to_date:     [date]

    :return:
    """

    data = _make_request("DangerObsV", region_id, from_date, to_date)
    list = []

    for d in data:
        list.append(DangerObs(d))

    list = sorted(list, key=lambda AvalancheObs: AvalancheObs.DtObsTime)

    return list



# incomplete
def get_weather_observation(region_id, from_date, to_date):

    data = _make_request("WeatherObservationV", region_id, from_date, to_date)

    return


if __name__ == "__main__":

    from_date = dt.date(2015, 4, 1)
    to_date = dt.date.today()

    avalanche_activity = get_avalanche_activity(116, from_date, to_date)

    log = env.log
    a = 1



