# -*- coding: utf-8 -*-
__author__ = 'raek'


import datetime as dt
import requests as requests
import types as types
import pandas as pd

import fencoding as fe
import makelogs as ml
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


def _make_odata_filter(from_date, to_date, region_id, observer_id, geohazard_tid=None):
    """Based on what is requested, this mehod builds the odata filter par of the request url.

    :param from_date:       [date] A query returns [from_date, to_date>
    :param to_date:         [date] A query returns [from_date, to_date>
    :param region_ids:      [int or list of ints] If region_ids = None, all regions are selected
    :param observer_ids:    [int or list of ints] If observer_ids = None, all observers are selected
    :param geohazard_tid:   [int] 10 is snow, 20,30,40 are dirt, 60 is water and 70 is ice

    :return:                [string] filter part of request url
    """

    odata_filter = "DtObsTime gt datetime'{0}' and " \
                   "DtObsTime lt datetime'{1}' and ".format(from_date, to_date)

    if region_id is not None:
        forecast_region_kdv = kdv.get_kdv("ForecastRegionKDV")
        region_name = forecast_region_kdv[region_id].Name
        odata_filter += "ForecastRegionName eq '{0}' and ".format(region_name)

    if observer_id is not None:
        odata_filter += "ObserverId eq {0} and ".format(observer_id)

    if geohazard_tid is not None:
        odata_filter += "GeoHazardTID eq {0} and ".format(geohazard_tid)

    odata_filter += "LangKey eq 1"
    odata_filter = fe.add_norwegian_letters(odata_filter)

    return odata_filter


def _make_data_request(view, from_date, to_date, region_ids=None, observer_ids=None, geohazard_tid=None, recursive_count=5):
    """Common part of all data requests.

    :param view:            [string] Name of view in regObs
    :param from_date:       [date] A query returns [from_date, to_date>
    :param to_date:         [date] A query returns [from_date, to_date>
    :param region_ids:      [int or list of ints] If region_ids = None, all regions are selected
    :param observer_ids:    [int or list of ints] If observer_ids = None, all observers are selected
    :param geohazard_tid:   [int] 10 is snow, 20,30,40 are dirt, 60 is water and 70 is ice
    :param recursive_count  [int] by default atempt the same request 5 times before giving up

    :return:                untreated request result
    """

    # If input isn't a list, make it so
    if not isinstance(region_ids, types.ListType):
        region_ids = [region_ids]

    if not isinstance(observer_ids, types.ListType):
        observer_ids = [observer_ids]

    data_out = []
    recursive_count_default = recursive_count   # need the default for later

    for region_id in region_ids:
        for observer_id in observer_ids:

            if len(observer_ids) > 1:
                # if we are looping the initial list make sure each item gets the recursive count default
                recursive_count = recursive_count_default

            odata_query = _make_odata_filter(from_date, to_date, region_id, observer_id, geohazard_tid)
            url = "http://api.nve.no/hydrology/regobs/{0}/Odata.svc/{1}/?$filter={2}&$format=json"\
                .decode('utf8').format(env.api_version, view, odata_query)
            ml.log_and_print("getobservations.py -> _make_data_request: {0}".format(fe.remove_norwegian_letters(url)))

            try:
                result = requests.get(url).json()
                result = result['d']['results']

            except:
                # Need to improve on exception handling: http://docs.python-requests.org/en/latest/user/quickstart/#errors-and-exceptions
                ml.log_and_print("getobservations.py -> _make_data_request: EXCEPTION. RECURSIVE COUNT {0}".format(recursive_count))
                result = []
                if recursive_count > 1:
                    recursive_count -= 1        # count down
                    result = _make_data_request(view, from_date, to_date, region_id, observer_id, geohazard_tid, recursive_count=recursive_count)

            # if more than 1000 elements are requested, odata truncates data to 1000. We do more requests
            if len(result) == 1000:
                time_delta = to_date - from_date
                date_in_middle = from_date + time_delta/2
                result = _make_data_request(view, from_date, date_in_middle, region_id, observer_id, geohazard_tid) \
                         + _make_data_request(view, date_in_middle, to_date, region_id, observer_id, geohazard_tid)

            data_out += result

    env.log.append("{2} to {3}: {1} has {0} items".format(len(data_out), view, from_date, to_date))

    return data_out


def _make_count_request(view, from_date, to_date, region_ids=None, observer_ids=None, geohazard_tid=None):
    """Common part of all count requests.

    Note that some views are shared by all geohazards. In these it is also
    possible to specify geohazard_tid in the filter.

    :param view:
    :param from_date:       [date] A query returns [from_date, to_date>
    :param to_date:         [date] A query returns [from_date, to_date>
    :param region_ids:      [int or list of ints] If region_ids = None, all regions are selected
    :param observer_ids:    [int or list of ints] If observer_ids = None, all observers are selected
    :param geohazard_tid:   [int] 10 is snow, 20,30,40 are dirt, 60 is water and 70 is ice

    :return:                [int] Number of observations.
    """

    # If input isn't a list, make it so
    if not isinstance(region_ids, types.ListType):
        region_ids = [region_ids]

    if not isinstance(observer_ids, types.ListType):
        observer_ids = [observer_ids]

    count = 0
    for region_id in region_ids:
        for observer_id in observer_ids:

            odata_query = _make_odata_filter(from_date, to_date, region_id, observer_id, geohazard_tid)
            url = "http://api.nve.no/hydrology/regobs/{0}/Odata.svc/{1}/$count/?$filter={2}&$format=json"\
                .decode('utf8').format(env.api_version, view, odata_query)

            ml.log_and_print("getobservations.py -> _make_count_request: ..to {0}".format(fe.remove_norwegian_letters(url)))

            result = requests.get(url).json()
            count += result

    return count


def _make_data_frame(list):
    """Takes a list of objects and makes a Pandas data frame.

    :param list: [list of objects]
    :return:     [data frame]
    """

    if len(list) == 0:
        data_frame = pd.DataFrame()
    else:
        observation_fields = list[0].__dict__.keys()
        data_frame = pd.DataFrame(columns=observation_fields)

        i = 0
        for l in list:
            observation_values = l.__dict__.values()
            data_frame.loc[i] = observation_values
            i += 1

    return data_frame


class Registration():

    def __init__(self, d):

        self.RegID = int(d['RegID'])
        self.DtObsTime = _unix_time_2_normal( int(d['DtObsTime'][6:-2]) )
        self.DtRegTime = _unix_time_2_normal( int(d['DtRegTime'][6:-2]) )

        # DtChangeTime only given when registration has been changed.
        # If DtChangeTime ends up like None, the field is missing from the view
        if 'DtChangeTime' in d:
            if d['DtChangeTime'] is not None:
                self.DtChangeTime = _unix_time_2_normal( int(d['DtChangeTime'][6:-2]) )
            else:
                self.DtChangeTime = self.DtRegTime
        else:
            self.DtChangeTime = None


class Location():

    def __init__(self, d):

        self.LocationName = fe.remove_norwegian_letters(d['LocationName'])
        self.UTMZone = int(d['UTMZone'])
        self.UTMEast = int(d['UTMEast'])
        self.UTMNorth = int(d['UTMNorth'])
        self.ForecastRegionName = fe.remove_norwegian_letters(d['ForecastRegionName'])

        # In AllRegistrationsV MunicipalName is named Kommunenavn
        if 'MunicipalName' in d:
            self.MunicipalName = fe.remove_norwegian_letters(d['MunicipalName'])
        elif 'Kommunenavn' in d:
            self.MunicipalName = fe.remove_norwegian_letters(d['Kommunenavn'])
        else:
            self.MunicipalName = None


class Observer():

    def __init__(self, d):

        self.NickName = fe.remove_norwegian_letters(d['NickName'])
        self.CompetenceLevelName = fe.remove_norwegian_letters(d['CompetenceLevelName'])


class AllRegistrations(Registration, Location, Observer):
    '''
    <entry>
        <id>http://api.nve.no/hydrology/RegObs/v0.9.1/OData.svc/AllRegistrationsV(4L)</id>
        <category term="RegObsModel.AllRegistrationsV" scheme="http://schemas.microsoft.com/ado/2007/08/dataservices/scheme" />
        <link rel="edit" title="AllRegistrationsV" href="AllRegistrationsV(4L)" />
        <title />
        <updated>2015-12-20T21:45:41Z</updated>
        <author>
           <name />
        </author>
        <content type="application/xml">
            <m:properties>
                <d:RadNummer m:type="Edm.Int64">4</d:RadNummer>
                <d:RegID m:type="Edm.Int32" m:null="true" />
                <d:DtObsTime m:type="Edm.DateTime" m:null="true" />
                <d:DtRegTime m:type="Edm.DateTime" m:null="true" />
                <d:Kommunenr m:null="true" />
                <d:Kommunenavn m:null="true" />
                <d:ForecastRegionTID m:type="Edm.Int16" m:null="true" />
                <d:ForecastRegionName m:null="true" />
                <d:LocationName m:null="true" /><d:ObserverGroupName m:null="true" />
                <d:NickName m:null="true" />
                <d:CompetenceLevelTID m:type="Edm.Int16" m:null="true" />
                <d:CompetenceLevelName m:null="true" />
                <d:GeoHazardTID m:type="Edm.Int16">33</d:GeoHazardTID>
                <d:GeoHazardName>Leire</d:GeoHazardName>
                <d:RegistrationTID m:type="Edm.Int16">29</d:RegistrationTID>
                <d:RegistrationName m:null="true" />
                <d:TypicalValue1 m:null="true" />
                <d:TypicalValue2 m:null="true" />
                <d:LangKey m:type="Edm.Int16" m:null="true" />
                <d:ObserverId m:type="Edm.Int32" m:null="true" />
                <d:LocationID m:type="Edm.Int32" m:null="true" />
                <d:UTMZone m:type="Edm.Int16" m:null="true" />
                <d:UTMEast m:type="Edm.Int32" m:null="true" /><d:UTMNorth m:type="Edm.Int32" m:null="true" />
                <d:Area m:type="Edm.Boolean" m:null="true" /><d:ObserverGroupId m:type="Edm.Int32" m:null="true" />
                <d:Picture m:type="Edm.Int16">0</d:Picture>
                <d:DtChangeTime m:type="Edm.DateTime" m:null="true" />
            </m:properties>
        </content>
    </entry>
    '''

    def __init__(self, d):

        Registration.__init__(self, d)
        Location.__init__(self, d)
        Observer.__init__(self, d)

        self.ForecastRegionTID = int(d['ForecastRegionTID'])
        self.ObserverId = int(d['ObserverId'])

        self.RowNumber = int(d['RadNummer'])
        self.GeoHazardName = fe.remove_norwegian_letters(d['GeoHazardName'])
        self.RegistrationName = fe.remove_norwegian_letters(d['RegistrationName'])
        self.TypicalValue1 = fe.remove_norwegian_letters(d['TypicalValue1'])
        self.TypicalValue2 = fe.remove_norwegian_letters(d['TypicalValue2'])
        self.LangKey = int(d['LangKey'])
        self.Picture = d['Picture']


class AvalancheActivityObs(Registration, Location, Observer):

    def __init__(self, d):

        Registration.__init__(self, d)
        Location.__init__(self, d)
        Observer.__init__(self, d)

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


class AvalancheActivityObs2(Registration, Location, Observer):

    def __init__(self, d):

        Registration.__init__(self, d)
        Location.__init__(self, d)
        Observer.__init__(self, d)

        self.EstimatedNumTID = d['EstimatedNumTID']
        self.EstimatedNumName = fe.remove_norwegian_letters(d['EstimatedNumName'])

        #timedelta between regobs.no and database
        time_delta = dt.timedelta(hours=-2)

        if d['DtStart'] is not None:
            self.DtStart = _unix_time_2_normal(int(d['DtStart'][6:-2])) + time_delta
        else:
            # Really not sure I should assume DtStart = DtObsTime when None
            self.DtStart = (_unix_time_2_normal(int(d['DtObsTime'][6:-2]))).replace(hour=00, minute=00)

        if d['DtEnd'] is not None:
            self.DtEnd = _unix_time_2_normal(int(d['DtEnd'][6:-2])) + time_delta
        else:
            # Really not sure I should assume DtEnd = DtObsTime when None
            self.DtEnd = (_unix_time_2_normal(int(d['DtObsTime'][6:-2]))).replace(hour=23, minute=59)

        self.ValidExposition = d['ValidExposition']     # int of eight char. First char is N, second is NE etc.
        self.ExposedHeight1 = None
        if d['ExposedHeight1'] is not None: self.ExposedHeight1 = d['ExposedHeight1']      # upper height
        self.ExposedHeight2 = None
        if d['ExposedHeight2'] is not None: self.ExposedHeight2 = d['ExposedHeight2']      # lower height
        self.ExposedHeightComboTID = d['ExposedHeightComboTID']

        self.AvalancheExtName = fe.remove_norwegian_letters(d['AvalancheExtName'])
        self.AvalCauseName = fe.remove_norwegian_letters(d['AvalCauseName'])
        self.AvalTriggerSimpleName = fe.remove_norwegian_letters(d['AvalTriggerSimpleName'])
        self.DestructiveSizeName = fe.remove_norwegian_letters(d['DestructiveSizeName'])
        self.AvalPropagationName = fe.remove_norwegian_letters(d['AvalPropagationName'])
        self.Comment = fe.remove_norwegian_letters(d['Comment'])
        self.LangKey = d['LangKey']


class AvalancheObs(Registration, Location, Observer):

    def __init__(self, d):

        Registration.__init__(self, d)
        Location.__init__(self, d)
        Observer.__init__(self, d)

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


class DangerObs(Registration, Location, Observer):

    def __init__(self, d):

        Registration.__init__(self, d)
        Location.__init__(self, d)
        Observer.__init__(self, d)

        self.Comment = fe.remove_norwegian_letters(d['Comment'])
        self.DangerObsID = d['DangerObsID']
        self.DangerSignName = d['DangerSignName']
        self.DangerSignTID = d['DangerSignTID']
        self.GeoHazardName = d['GeoHazardName']
        self.GeoHazardTID = d['GeoHazardTID']
        self.LangKey = d['LangKey']


def get_all_registrations(from_date, to_date, region_ids=None, observer_ids=None, output='List', geohazard_tid=None):
    """Gets observations from AllRegistrationsV.

    View is shared by all the geohazards so the filter includes geohazard_tid if only one geohazard is needed.

    :param from_date:       [date] A query returns [from_date, to_date>
    :param to_date:         [date] A query returns [from_date, to_date>
    :param region_ids:      [int or list of ints] If region_ids = None, all regions are selected
    :param observer_ids:    [int or list of ints] If observer_ids = None, all observers are selected
    :param output:          [string] Options: 'List', 'DataFrame' and 'Count'. Default 'List'.
    :param geohazard_tid    [int] 10 is snow, 20,30,40 are dirt, 60 is water and 70 is ice

    :return:
    """

    if output == 'List' or output == 'DataFrame':
        data = _make_data_request("AllRegistrationsV", from_date, to_date, region_ids, observer_ids, geohazard_tid)
        list = [AllRegistrations(d) for d in data]
        list = sorted(list, key=lambda AllRegistrations: AllRegistrations.DtObsTime)

        if output == 'List':
            return list

        elif output == 'DataFrame':
            return _make_data_frame(list)

    elif output == 'Count':
        count = _make_count_request("AllRegistrationsV", from_date, to_date, region_ids, observer_ids, geohazard_tid)
        return count

    else:
        ml.log_and_print('getobservations.py -> get_all_registrations: Illegal output option.')
        return None


def get_avalanche_activity(from_date, to_date, region_ids=None, observer_ids=None, output='List'):
    """Gets observations from AvalancheActivityObsV.

    :param from_date:       [date] A query returns [from_date, to_date>
    :param to_date:         [date] A query returns [from_date, to_date>
    :param region_ids:      [int or list of ints] If region_ids = None, all regions are selected
    :param observer_ids:    [int or list of ints] If observer_ids = None, all observers are selected
    :param output:          [string] Options: 'List', 'DataFrame' and 'Count'. Default 'List'.

    :return:
    """

    if output == 'List' or output == 'DataFrame':
        data = _make_data_request("AvalancheActivityObsV", from_date, to_date, region_ids, observer_ids)
        list = [AvalancheActivityObs(d) for d in data]
        list = sorted(list, key=lambda AvalancheActivityObs: AvalancheActivityObs.DtObsTime)

        if output == 'List':
            return list

        elif output == 'DataFrame':
            return _make_data_frame(list)

    elif output == 'Count':
        count = _make_count_request("AvalancheActivityObsV", from_date, to_date, region_ids, observer_ids)
        return count

    else:
        ml.log_and_print('getobservations.py -> get_avalanche_activity: Illegal output option.')
        return None


def get_avalanche_activity_2(from_date, to_date, region_ids=None, observer_ids=None, output='List'):
    """Gets observations from AvalancheActivityObs2V.

    :param from_date:       [date] A query returns [from_date, to_date>
    :param to_date:         [date] A query returns [from_date, to_date>
    :param region_ids:      [int or list of ints] If region_ids = None, all regions are selected
    :param observer_ids:    [int or list of ints] If observer_ids = None, all observers are selected
    :param output:          [string] Options: 'List', 'DataFrame' and 'Count'. Default 'List'.

    :return:
    """

    if output == 'List' or output == 'DataFrame':
        data = _make_data_request("AvalancheActivityObs2V", from_date, to_date, region_ids, observer_ids)
        list = [AvalancheActivityObs2(d) for d in data]
        list = sorted(list, key=lambda AvalancheActivityObs2: AvalancheActivityObs2.DtObsTime)

        if output == 'List':
            return list

        elif output == 'DataFrame':
            return _make_data_frame(list)

    elif output == 'Count':
        count = _make_count_request("AvalancheActivityObs2V", from_date, to_date, region_ids, observer_ids)
        return count

    else:
        ml.log_and_print('getobservations.py -> get_avalanche_activity_2: Illegal output option.')
        return None


def get_avalanche(from_date, to_date, region_ids=None, observer_ids=None, output='List'):
    """Gets observations from AvalancheObsV.

    :param from_date:       [date] A query returns [from_date, to_date>
    :param to_date:         [date] A query returns [from_date, to_date>
    :param region_ids:      [int or list of ints] If region_ids = None, all regions are selected
    :param observer_ids:    [int or list of ints] If observer_ids = None, all observers are selected
    :param output:          [string] Options: 'List', 'DataFrame' and 'Count'. Default 'List'.

    :return:
    """

    if output == 'List' or output == 'DataFrame':

        data = _make_data_request("AvalancheObsV", from_date, to_date, region_ids, observer_ids)
        list = [AvalancheObs(d) for d in data]
        list = sorted(list, key=lambda AvalancheObs: AvalancheObs.DtObsTime)

        if output == 'List':
            return list

        elif output == 'DataFrame':
            return _make_data_frame(list)

    elif output == 'Count':
        count = _make_count_request("AvalancheObsV", from_date, to_date, region_ids, observer_ids)
        return count

    else:
        ml.log_and_print('getobservations.py -> get_avalanche: Illegal output option.')
        return None


def get_danger_sign(from_date, to_date, region_ids=None, observer_ids=None, output='List', geohazard_tid=None):
    """Gets observations from DangerObsV. View is shared by all the geohazards so the filter includes
    geohazard_tid if only one geohazard is needed.

    :param from_date:       [date] A query returns [from_date, to_date>
    :param to_date:         [date] A query returns [from_date, to_date>
    :param region_ids:      [int or list of ints] If region_ids = None, all regions are selected
    :param observer_ids:    [int or list of ints] If observer_ids = None, all observers are selected
    :param output:          [string] Options: 'List', 'DataFrame' and 'Count'. Default 'List'.
    :param geohazard_tid    [int] 10 is snow, 20,30,40 are dirt, 60 is water and 70 is ice

    :return:
    """

    if output == 'List' or output == 'DataFrame':
        data = _make_data_request("DangerObsV", from_date, to_date, region_ids, observer_ids, geohazard_tid)
        list = [DangerObs(d)for d in data]
        list = sorted(list, key=lambda DangerObs: DangerObs.DtObsTime)

        if output == 'List':
            return list

        elif output == 'DataFrame':
            return _make_data_frame(list)

    elif output == 'Count':
        count = _make_count_request("DangerObsV", from_date, to_date, region_ids, observer_ids, geohazard_tid)
        return count

    else:
        ml.log_and_print('getobservations.py -> get_danger_sign: Illegal output option.')
        return None


# incomplete
def get_weather_observation(from_date, to_date, region_ids = None, observer_ids = None):

    data = _make_data_request("WeatherObservationV", from_date, to_date, region_ids = None, observer_ids = None)

    return


def _view_test():
    '''Method tests if views show observartions made by Ragnar on a test location the last fiew days.
    The purpose is to test if views correctly remove deleted items.

    :return:
    '''

    views = ['AllRegistrationsV',
             'AllRegistrationsIceV',
             'AllRegistrationsLandslideV',
             'AllRegistrationsSnowV',
             'AllRegistrationsWaterV',
             'DangerObsV',
             'IncidentV',
             'GeneralObservationV',
             'PictureV',
             'AvalancheObsV',
             'AvalancheActivityObsV',
             # 'AvalancheActivityObs2V',
             'AvalancheDangerObsV',
             'AvalancheEvaluationV',
             'AvalancheEvaluation2V',
             'AvalancheEvaluation3V',
             'AvalancheEvalProblem2V',
             'WeatherObservationV',
             'ColumnTestV',
             # 'DangerSignV',
             # 'WeakLayerV',
             'SnowCoverObsV',
             'SnowSurfaceObservationV',
             'IceCoverObsV',
             'IceThicknessV',
             'LandSlideObsV',
             'WaterLevelV',
             ]


    log = env.log
    view_test = []

    for v in views:
        view_test += _make_data_request(v, 0, dt.date.today() - dt.timedelta(days=1), dt.date.today() + dt.timedelta(days=1))

    for o in view_test:
        if 'Ragnar' in o['NickName'] and 'Test' in o['LocationName']:
            ml.log_and_print('{0: <30} with RegID    {3: <7} has observations by    {1: <20} on location    {2}.'.format(o['__metadata']['type'], o['NickName'], o['LocationName'], o['RegID']),
                             print_it=True, log_it=True)



    a = 1


if __name__ == "__main__":

    from_date = dt.date(2016, 4, 1)
    from_date = dt.date.today()-dt.timedelta(days=150)
    to_date = dt.date.today()+dt.timedelta(days=1)
    region_ids = 116
    observer_ids = None


    # requesten bør returnere tom liste. Hvordan går det?
    '''my_observations = get_all_registrations(from_date=dt.date(2015, 6, 1),
                                            to_date=dt.date(2016, 7, 1),
                                            geohazard_tid=10,
                                            observer_ids=[6, 7, 236],
                                            output='List',
                                            region_ids=[121, 122, 123])
    '''

    #all_observations = get_all_registrations(from_date, to_date, output='DataFrame')
    # print(all_observations)

    # geo_hazard_kdv = kdv.get_kdv('GeoHazardKDV')

    # all_registrations_snow = get_all_registrations(from_date, to_date, geohazard_tid=10)
    # all_registrations_ice = get_all_registrations(from_date, to_date, geohazard_tid=70)
    # all_registrations = get_all_registrations(from_date, to_date)
    #
    # count_registrations_snow = get_all_registrations(from_date, to_date, geohazard_tid=10, output='Count')
    # count_registrations_ice = get_all_registrations(from_date, to_date, geohazard_tid=70, output='Count')
    # count_registrations = get_all_registrations(from_date, to_date, output='Count')
    #
    avalanche_activity = get_avalanche_activity(from_date, to_date, 116)
    avalanche_activity_2 = get_avalanche_activity_2(from_date, to_date, 116)
    # avalanche = get_avalanche(from_date, to_date, region_ids)
    # danger_sign = get_danger_sign(from_date, to_date, observer_ids)

    count_registrations_snow_10 = get_all_registrations(dt.date(2015, 12, 1), dt.date.today(), geohazard_tid=10, output='Count', observer_ids=10)


    # _view_test()
    all_registrations = get_all_registrations(from_date, to_date)
    for a in all_registrations:
        ml.log_and_print(
            "{0}\t{1}\t{2:<6}\t{3:<15}\t{4:<20}\t{5:<20}\t{6}".format(a.RegID, a.DtRegTime, a.GeoHazardName, a.MunicipalName,
                                                                      a.ForecastRegionName, a.NickName, a.RegistrationName),
            print_it=True, log_it=True)


    a = 1



