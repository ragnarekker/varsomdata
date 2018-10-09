# -*- coding: utf-8 -*-
import sys as sys
import datetime as dt
import requests as requests
import csv as csv
from varsomdata import getobservations as go
from varsomdata import getdangers as gd
from utilities import fencoding as fe, readfile as rf, makelogs as ml
from varsomdata import getkdvelements as kdv
import setcoreenvironment as cenv
import setenvironment as env

__author__ = 'raek'


class Trip:
    """Object containing data about observer trips."""

    def __init__(self, d):
        self.TripID = int(d["TripID"])
        self.ObserverID = int(d["ObserverID"])
        self.ObsLocationID = int(d["ObsLocationID"])
        self.GeoHazardTID = int(d["GeoHazardTID"])
        self.TripTypeTID = int(d["TripTypeTID"])
        self.ObservationExpectedTime = fe.unix_time_2_normal( int(d["ObservationExpectedTime"][6:-2]) )
        self.Comment = d["Comment"]
        self.IsFinished = bool(d["IsFinished"])
        self.TripRegistrationTime = fe.unix_time_2_normal( int(d["TripRegistrationTime"][6:-2]) )
        if d["TripFinishedTime"] is not None:
            self.TripFinishedTime = fe.unix_time_2_normal( int(d["TripFinishedTime"][6:-2]) )
        else:
            self.TripFinishedTime = None
        self.DeviceID = d["DeviceID"]
        self.TripTypeName = kdv.get_name("TripTypeKDV", self.TripTypeTID)


def get_trip(from_date, to_date, geohazard_tid=None, output='List'):
    """Gets trip information and returns list of class Trip objects. Optionally .csv file is written to project
    output folder.

    :param from_date:       [date] A query returns [from_date, to_date>
    :param to_date:         [date] A query returns [from_date, to_date>
    :param geohazard_tid:   [int] 10 is snow, 20,30,40 are dirt, 60 is water and 70 is ice
    :param output:          [string]
    :return:                [list] of class Trip objects

    <entry>
        <id>http://api.nve.no/hydrology/RegObs/v0.9.9/OData.svc/Trip(1)</id>
        <category term="RegObsModel.Trip" scheme="http://schemas.microsoft.com/ado/2007/08/dataservices/scheme" />
        <link rel="edit" title="Trip" href="Trip(1)" /><link rel="http://schemas.microsoft.com/ado/2007/08/dataservices/related/Observer" type="application/atom+xml;type=entry" title="Observer" href="Trip(1)/Observer" />
        <link rel="http://schemas.microsoft.com/ado/2007/08/dataservices/related/ObsLocation" type="application/atom+xml;type=entry" title="ObsLocation" href="Trip(1)/ObsLocation" />
        <title />
        <updated>2015-12-30T20:09:16Z</updated>
        <author>
            <name />
        </author>
        <content type="application/xml">
            <m:properties>
                <d:TripID m:type="Edm.Int32">1</d:TripID>
                <d:ObserverID m:type="Edm.Int32">1077</d:ObserverID>
                <d:ObsLocationID m:type="Edm.Int32">19063</d:ObsLocationID>
                <d:GeoHazardTID m:type="Edm.Int16">10</d:GeoHazardTID>
                <d:TripTypeTID m:type="Edm.Int32">20</d:TripTypeTID>
                <d:ObservationExpectedTime m:type="Edm.DateTime">2015-01-09T11:00:00</d:ObservationExpectedTime>
                <d:Comment></d:Comment>
                <d:IsFinished m:type="Edm.Boolean">true</d:IsFinished>
                <d:TripRegistrationTime m:type="Edm.DateTime">2015-01-09T09:11:59.263</d:TripRegistrationTime>
                <d:TripFinishedTime m:type="Edm.DateTime">2015-01-09T09:18:36.653</d:TripFinishedTime>
                <d:DeviceID m:type="Edm.Guid">835f5e39-a73a-48d3-2c7f-3c81c0492b87</d:DeviceID>
            </m:properties>
        </content>
    </entry>
    """

    odata_filter = ""

    if geohazard_tid is not None:
        odata_filter += "GeoHazardTID eq {0} and ".format(geohazard_tid)

    odata_filter += "TripRegistrationTime gt datetime'{0}' and TripRegistrationTime lt datetime'{1}'".format(from_date, to_date)

    url = "http://api.nve.no/hydrology/regobs/{0}/Odata.svc/Trip/?$filter={1}&$format=json".format(cenv.odata_version, odata_filter)

    ml.log_and_print('[info] getmisc.py -> get_trip: ..to {0}'.format(url), print_it=True)

    result = requests.get(url).json()
    data = result['d']['results']

    # if more than 1000 elements are requested, odata truncates data to 1000. We do more requests
    if len(result) == 1000:
        time_delta = to_date - from_date
        date_in_middle = from_date + time_delta/2
        data_out = get_trip(from_date, date_in_middle, geohazard_tid) + get_trip(date_in_middle, to_date, geohazard_tid)
    else:
        data_out = [Trip(d) for d in data]

    if output == 'List':
        return data_out
    elif output == 'csv':
        with open('{0}trips {1}-{2}.csv'.format(env.output_folder, from_date.strftime('%Y%m%d'), to_date.strftime('%Y%m%d')), 'wb') as f:
            w = csv.DictWriter(f, data_out[0].__dict__.keys(), delimiter=";")
            w.writeheader()
            for t in data_out:
                w.writerow(t.__dict__)
        return data_out


class ObserverGroupMember:
    """Object containing list of users in (a) group(s)."""

    def __init__(self, d):
        self.NickName = d["NickName"]
        self.ObserverGroupDescription = d["ObserverGroupDescription"]
        self.ObserverGroupID = int(d["ObserverGroupID"])
        self.ObserverGroupName = d["ObserverGroupName"]
        self.ObserverID = int(d["ObserverID"])


def get_observer_group_member(group_id=None, output='List'):
    """Gets data on observers in a group. If no group is requested, all is retrieved.

    :param group_id:    [int]
    :param output:      [string] 'List' or 'Dict'
    :return:            [list] of class ObserverGroupMember or dictionary with observer id and observer nicks.
    """

    if group_id is None:
        url = 'http://api.nve.no/hydrology/regobs/{0}/Odata.svc/ObserverGroupMemberV/?$format=json'.format(cenv.odata_version)
    else:
        url = 'http://api.nve.no/hydrology/regobs/{0}/Odata.svc/ObserverGroupMemberV/?$filter=ObserverGroupID%20eq%20{1}&$format=json'.format(cenv.odata_version, group_id)
    ml.log_and_print("[info] getmisc.py -> get_observer_group_member: {0}".format(url))

    result = requests.get(url).json()
    data = result['d']['results']
    data_out = [ObserverGroupMember(d) for d in data]

    if output=='List':
        return data_out
    elif output=='Dict':
        observer_dict = {}
        for o in data_out:
            observer_dict[o.ObserverID] = o.NickName
        return observer_dict


class Registration:
    """Object for data on the regObs Registration table."""

    def __init__(self, d):
        self.RegID = int(d["RegID"])
        self.DtObsTime = fe.unix_time_2_normal(d["DtObsTime"])
        self.DtRegTime = fe.unix_time_2_normal(d["DtRegTime"])
        if d["DtChangeTime"] is not None:
            self.DtChangeTime = fe.unix_time_2_normal(d["DtChangeTime"])
        else:
            self.DtChangeTime = None
        if d["DeletedDate"] is not None:
            self.DeletedDate = fe.unix_time_2_normal(d["DeletedDate"])
        else:
            self.DeletedDate = None
        self.ObserverID = int(d["ObserverID"])
        self.NickName = None                                    # added later
        self.CompetenceLevelTID = int(d["CompetenceLevelTID"])
        if d["ObserverGroupID"] is not None:
            self.ObserverGroupID = int(d["ObserverGroupID"])
        else:
            self.ObserverGroupID = None
        self.GeoHazardTID = int(d['GeoHazardTID'])
        self.ObsLocationID = int(d["ObsLocationID"])
        self.ApplicationID = d["ApplicationId"]


def get_registration(from_date, to_date, output='List', geohazard_tid=None, application_id='', include_deleted=False):
    """Gets data from the Registration table. Adds observer nickname if list is requested and if not otherwise
    specified deleted registrations are taken out.

    :param from_date:
    :param to_date:
    :param output:
    :param geohazard_tid:
    :param application_id:
    :param include_deleted:
    :return:                raw data from the request or list of class Registration objects
    """

    odata_filter = ""
    if geohazard_tid is not None:
        odata_filter += "GeoHazardTID eq {0} and ".format(geohazard_tid)
    odata_filter += "DtRegTime gt datetime'{0}' and DtRegTime lt datetime'{1}'".format(from_date, to_date)
    if "Web and app" in application_id:     # does not work..
        odata_filter += " and (ApplicationId eq guid'{0}' or ApplicationId eq guid'{1}')".format('', '')

    url = 'http://api.nve.no/hydrology/regobs/{0}/Odata.svc/{1}/?$filter={2}&$format=json'.format(cenv.odata_version, 'Registration', odata_filter)
    ml.log_and_print("[info] getmisc.py -> get_registration: ..to {0}".format(url), print_it=True)

    result = requests.get(url).json()
    data = result['d']['results']

    # if more than 1000 elements are requested, odata truncates data to 1000. We do more requests
    if len(data) == 1000:
        time_delta = to_date - from_date
        date_in_middle = from_date + time_delta/2
        data = get_registration(from_date, date_in_middle, output='Raw', geohazard_tid=geohazard_tid, application_id=application_id) \
                 + get_registration(date_in_middle, to_date, output='Raw', geohazard_tid=geohazard_tid, application_id=application_id)

    if output=='Raw':
        return data
    elif output=='List':
        data_out = [Registration(d) for d in data]
        observer_nicks = get_observer_v()
        # NickName is not originally in the Registration table
        for d in data_out:
            d.NickName = observer_nicks[d.ObserverID]
            # why list??? d.NickName = [observer_nicks[d.ObserverID]]
        if include_deleted == False:
            data_out = [d for d in data_out if d.DeletedDate is None]
        return data_out


class ObsLocation:
    """Object of an ObsLocation."""

    def __init__(self, d):

        self.ObsLocationID = int(d["ObsLocationID"])
        self.DtRegTime = fe.unix_time_2_normal(d["DtRegTime"])
        self.LocationName = d["LocationName"]
        self.LocationDescription = d["LocationDescription"]
        self.UTMSourceName = d["UTMSourceName"]
        self.UTMSourceTID = d["UTMSourceTID"]
        self.UTMEast = d["UTMEast"]
        self.UTMNorth = d["UTMNorth"]
        self.UTMUncertainty = d["UTMUncertainty"]
        self.Comment = d["Comment"]
        self.ForecastRegionTID = d["ForecastRegionTID"]
        self.ForecastRegionName = d["ForecastRegionName"]
        self.MunicipalName = d["MunicipalName"]


def get_obs_location(from_date, to_date):
    """Finds obs locations submitted during a given period.

    :param from_date:
    :param to_date:
    :return locations:  [list] of class ObsLocation
    """

    odata_filter = "DtRegTime gt datetime'{0}' and DtRegTime lt datetime'{1}' and langkey eq 1".format(from_date, to_date)

    url = 'http://api.nve.no/hydrology/regobs/{0}/Odata.svc/ObsLocationV/?$filter={1}&$format=json'.format(cenv.odata_version, odata_filter)
    result = requests.get(url).json()
    data = result['d']['results']
    ml.log_and_print('[info] getmisc.py -> get_obs_location: {0}'.format(url))

    # if more than 1000 elements are requested, odata truncates data to 1000. We do more requests
    locations = [ObsLocation(d) for d in data]

    if from_date != to_date and from_date != dt.date(2016, 11, 22):
        if len(locations) == 1000:
            time_delta = to_date - from_date
            date_in_middle = from_date + time_delta / 2
            locations = get_obs_location(from_date, date_in_middle) + get_obs_location(date_in_middle, to_date)
    else:
        ml.log_and_print('[warning] getmisc.py -> get_obs_location: More than 1000 locations on 2016.11.22')

    return locations


class AvalancheIndex:

    def __init__(self):

        self.estimated_num = None
        self.destructive_size = None
        self.index = 0          # avalanche index 0 is an avalanche observation with insufficient data

        self.date = None
        self.region_name = None
        self.observation = None


    def set_num_and_size_and_index(self, estimated_num_inn, destructive_size_inn, index_definition):

        self.estimated_num = estimated_num_inn
        self.destructive_size = destructive_size_inn

        if "Ingen skredaktivitet" in self.estimated_num:
            self.set_no_avalanche_activity()
        elif self.estimated_num is not None:
            if self.destructive_size is not None:
                for i in index_definition:
                    if i.estimated_num in self.estimated_num and i.destructive_size in self.destructive_size:
                        self.index = int(i.index)
            else:
                # If there is observed avalanaches but not given sizes, count the observations as a dangersign
                self.set_avalanches_as_dangersign()


    def set_no_avalanche_activity(self):
        self.estimated_num = "Ingen skredaktivitet"
        self.index = 1


    def set_avalanches_as_dangersign(self):
        self.estimated_num = 'Ferske skred'
        self.destructive_size = 'Ferske skred'
        self.index = 2


    def set_date_region_observation(self, date_inn, region_name_inn, observation_inn):

        self.date = date_inn
        self.region_name = region_name_inn
        self.observation = observation_inn


    def add_configuration_row(self, row):
        """Used for reading the definition file. Method called from readfile.py.

        :param row:
        :return:
        """

        self.estimated_num = row[0]
        self.destructive_size = row[1]
        self.index = row[2]

        return


def get_avalanche_index(from_date, to_date, region_ids=None, observer_ids=None):
    """All tables in regObs containing information on avalanche activity is mapped to an avalanche index. These
    are AvalancheActivityObs, AvalancheActivityObs2, AvalanchObs and DangerObs. The definition of the index is
    found in the input/aval_dl_order_of_size_and_num.csv configuration file.

    :param from_date:
    :param to_date:
    :param region_ids:
    :param observer_ids:
    :return avalanche_indexes:  [list] of class AvalanchIndex
    """

    # get all data
    avalanche_activities = go.get_avalanche_activity(from_date, to_date, region_ids=region_ids, observer_ids=observer_ids)
    avalanche_activities_2 = go.get_avalanche_activity_2(from_date, to_date, region_ids=region_ids, observer_ids=observer_ids)
    avalanches = go.get_avalanche(from_date, to_date, region_ids=region_ids, observer_ids=observer_ids)
    danger_signs = go.get_danger_sign(from_date, to_date, region_ids=region_ids, observer_ids=observer_ids)

    # get index definition
    index_definition = rf.read_configuration_file('{0}aval_dl_order_of_size_and_num.csv'.format(cenv.input_folder), AvalancheIndex)

    avalanche_indexes = []

    for aa in avalanche_activities:

        ai = AvalancheIndex()
        ai.set_num_and_size_and_index(aa.EstimatedNumName, aa.DestructiveSizeName, index_definition)
        ai.set_date_region_observation(aa.DtAvalancheTime, aa.ForecastRegionName, aa)
        avalanche_indexes.append(ai)

    for aa in avalanche_activities_2:

        if aa.DtStart and aa.DtEnd:
            ai = AvalancheIndex()
            ai.set_num_and_size_and_index(aa.EstimatedNumName, aa.DestructiveSizeName, index_definition)
            # Activity date is the avarage of DtStart and DtEnd
            activity_date = aa.DtStart+(aa.DtEnd-aa.DtStart)/2
            ai.set_date_region_observation(activity_date.date(), aa.ForecastRegionName, aa)
            avalanche_indexes.append(ai)

    for aa in avalanches:

        ai = AvalancheIndex()
        # Make sure size is not None
        ai.set_num_and_size_and_index("Ett (1)", aa.DestructiveSizeName, index_definition)
        ai.set_date_region_observation(aa.DtAvalancheTime, aa.ForecastRegionName, aa)
        avalanche_indexes.append(ai)

    for ds in danger_signs:

        ai = AvalancheIndex()
        if 'Ferske skred' in ds.DangerSignName:
            ai.set_avalanches_as_dangersign()
        elif 'Ingen faretegn observert' in ds.DangerSignName:
            ai.set_no_avalanche_activity()
        else:
            continue
        ai.set_date_region_observation(ds.DtObsTime, ds.ForecastRegionName, ds)
        avalanche_indexes.append(ai)

    return avalanche_indexes


def get_observer_v():
    """Selects all data from the ObserverV view.

    :return: a dictionary of key/ObserverID : value/NickName

    Eg. request: https://api.nve.no/hydrology/regobs/v3.0.6/Odata.svc/ObserverV/?$filter=ObserverId%20lt%203000&$format=json
    """

    url_1 = 'http://api.nve.no/hydrology/regobs/{0}/Odata.svc/ObserverV/?$filter=ObserverId lt 3000&$format=json'.format(cenv.odata_version)
    result_1 = requests.get(url_1).json()
    data_1 = result_1['d']['results']

    url_2 = 'http://api.nve.no/hydrology/regobs/{0}/Odata.svc/ObserverV/?$filter=ObserverId gt 2999 and ObserverId lt 6000&$format=json'.format(cenv.odata_version)
    result_2 = requests.get(url_2).json()
    data_2 = result_2['d']['results']

    url_3 = 'http://api.nve.no/hydrology/regobs/{0}/Odata.svc/ObserverV/?$filter=ObserverId gt 5999&$format=json'.format(cenv.odata_version)
    result_3 = requests.get(url_3).json()
    data_3 = result_3['d']['results']

    data = data_1 + data_2 + data_3

    observer_nicks = {}
    for d in data:
        key = d['ObserverId']
        val = d['NickName']
        observer_nicks[key] = val

    return observer_nicks


def get_forecast_dates(year, padding=dt.timedelta(days=0)):
    """Get valid periods we have had forecasts.

    :param year:        [string] Year interval 'YYYY-YY'
    :param padding:     [timedelta] Adds days before and after the original forecast dates
    :return:
    """

    if year == '2012-13':
        # http://api01.nve.no/hydrology/forecast/avalanche/v3.0.0/api/AvalancheWarningByRegion/Detail/13/1/2013-01-11/2013-05-31
        from_date = dt.date(2013, 1, 11)
        to_date = dt.date(2013, 5, 31)
    elif year == '2013-14':
        # http://api01.nve.no/hydrology/forecast/avalanche/v3.0.0/api/AvalancheWarningByRegion/Detail/13/1/2013-12-02/2014-06-01
        from_date = dt.date(2013, 12, 2)
        to_date = dt.date(2014, 6, 1)
    elif year == '2014-15':
        from_date = dt.date(2014, 11, 10)
        to_date = dt.date(2015, 6, 21)
    elif year == '2015-16':
        from_date = dt.date(2015, 11, 10)
        to_date = dt.date(2016, 6, 21)
    elif year == '2016-17':
        from_date = dt.date(2016, 11, 10)
        to_date = dt.date(2017, 6, 21)
    elif year == '2017-18':
        from_date = dt.date(2017, 11, 1)
        to_date = dt.date.today() + dt.timedelta(days=2)
    else:
        from_date = "Undefined dates"
        to_date = "Undefined dates"

    from_date -= padding
    to_date += padding

    return from_date, to_date


def get_observation_dates(year, padding=dt.timedelta(days=0)):
    """Get valid periods we have had observations. Default 11-01 to 07-01

    :param year:        [string] Year interval 'YYYY-YY'
    :param padding:     [timedelta] Adds days before and after the original forecast dates
    :return:
    """

    if year == '2012-13':
        from_date = dt.date(2012, 11, 1)
        to_date = dt.date(2013, 7, 1)
    elif year == '2013-14':
        from_date = dt.date(2013, 11, 1)
        to_date = dt.date(2014, 7, 1)
    elif year == '2014-15':
        from_date = dt.date(2014, 11, 1)
        to_date = dt.date(2015, 7, 1)
    elif year == '2015-16':
        from_date = dt.date(2015, 11, 1)
        to_date = dt.date(2016, 7, 1)
    elif year == '2016-17':
        from_date = dt.date(2016, 11, 1)
        to_date = dt.date(2017, 7, 1)
    elif year == '2017-18':
        from_date = dt.date(2017, 11, 1)
        to_date = dt.date.today() + dt.timedelta(days=2)
    else:
        from_date = "Undefined dates"
        to_date = "Undefined dates"

    from_date -= padding
    to_date += padding

    return from_date, to_date


def get_forecast_regions(year, get_b_regions=False):
    """Get valid forecast region ids for a given year.

    :param year:                 [String] as YYYY-YY
    :param get_b_regions:        [Bool] Before te rest of norway was th counties, but now they are called B-regions.

    :return:

    From email describing the region shapes:
    You’ll find 4 shape sets:

    One from January 2013. These are the initial regions we had.

    One from March 2014. The region definitions in the original shape was adjusted and was extended with Svartisen
    which has forecasting from April 2014. This shape contains Nordenskioldland, but forecasting was not tested
    here before the season after.

    One from December 2014. This valid for seasons 2014-15 and 2015-16, but we didn’t start Salten forecasting
    before march 2015. Nordenskioldland was tested for 2 weeks in 2015. Note also in 2014-15 we started forecasting
    for all of Norway if there was a possibility of danger level 4 or 5. Also outside of regular forecasting
    from December through May.

    The shape from December 2016 was a total makeover.
    """

    if year == '2012-13':
        # varsling startet januar 2013
        region_ids = [106, 107, 108, 109, 110, 111, 112, 113, 114, 115, 116, 117, 118, 119, 120, 121, 122, 123, 124, 125, 126, 127, 128, 129]
    elif year == '2013-14':
        # Svartisen (131) was started in april 2014
        # Nordenskioldland (130) and Hallingdal (132) was established in april 2014, but not used before th season after.
        region_ids = [106, 107, 108, 109, 110, 111, 112, 113, 114, 115, 116, 117, 118, 119, 120, 121, 122, 123, 124, 125, 126, 127, 128, 129, 130, 131, 132]
    elif year == '2014-15':
        # Salten (133) was started in mars 2015.
        # We tested Nordeskioldland (130) in may 2015.
        region_ids = [106, 107, 108, 109, 110, 111, 112, 114, 115, 116, 117, 118, 119, 121, 122, 123, 124, 127, 128, 129, 130, 131, 132, 133]
        if get_b_regions:
            region_ids += [n for n in range(151, 171, 1)]
    elif year == '2015-16':
        region_ids = [106, 107, 108, 109, 110, 111, 112, 114, 115, 116, 117, 118, 119, 121, 122, 123, 124, 127, 128, 129, 130, 131, 132, 133]
        if get_b_regions:
            region_ids += [n for n in range(151, 171, 1)]
    elif year == '2016-17' or year == '2017-18':
        # Total makeover in november 2016
        region_ids = [3003, 3007, 3009, 3010, 3011, 3012, 3013, 3014, 3015, 3016, 3017, 3022, 3023, 3024, 3027, 3028, 3029, 3031, 3032, 3034, 3035]
        if get_b_regions:
            region_ids += [3001, 3002, 3004, 3005, 3006, 3008, 3018, 3019, 3020, 3021, 3025, 3026, 3030, 3033, 3036, 3037, 3038, 3039, 3040, 3041, 3042, 3043, 3044, 3045, 3046]
    else:
        region_ids = "No valid period given."

    return region_ids


def get_dates_from_season(year):
    """Get dates for hydrological year [1st sept, 31st aug] given a season as string.

    :param year:        [string] Year interval 'YYYY-YY'
    :return:            [date] from_date, to_date
    """

    if year == '2012-13':
        from_date = dt.date(2012, 9, 1)
        to_date = dt.date(2013, 8, 31)
    elif year == '2013-14':
        from_date = dt.date(2013, 9, 1)
        to_date = dt.date(2014, 8, 31)
    elif year == '2014-15':
        from_date = dt.date(2014, 9, 1)
        to_date = dt.date(2015, 8, 31)
    elif year == '2015-16':
        from_date = dt.date(2015, 9, 1)
        to_date = dt.date(2016, 8, 31)
    elif year == '2016-17':
        from_date = dt.date(2016, 9, 1)
        to_date = dt.date(2017, 8, 31)
    elif year == '2017-18':
        from_date = dt.date(2017, 9, 1)
        to_date = dt.date.today()
    else:
        from_date = 'Undefined dates'
        to_date = 'Undefined dates'

    return from_date, to_date


def get_season_from_date(date_inn):
    """A date belongs to a season. This method returns it."""

    if date_inn >= dt.date(2017, 9, 1) and date_inn < dt.date(2018, 9, 1):
        return '2017-18'
    elif date_inn >= dt.date(2016, 9, 1) and date_inn < dt.date(2017, 9, 1):
        return '2016-17'
    elif date_inn >= dt.date(2015, 9, 1) and date_inn < dt.date(2016, 9, 1):
        return '2015-16'
    elif date_inn >= dt.date(2014, 9, 1) and date_inn < dt.date(2015, 9, 1):
        return '2014-15'
    elif date_inn >= dt.date(2013, 9, 1) and date_inn < dt.date(2014, 9, 1):
        return '2013-14'
    elif date_inn >= dt.date(2012, 9, 1) and date_inn < dt.date(2013, 9, 1):
        return '2014-13'
    elif date_inn >= dt.date(2011, 9, 1) and date_inn < dt.date(2012, 9, 1):
        return '2011-12'
    else:
        return 'Requested date is before the beginning of time.'


def get_forecast_region_for_regid(reg_id):
    """Returns the forecast region used at a given place in a given season.

    :param reg_id: [int]            regid in regObs
    :return:       [int]            ForecastRegionTID from regObs
                   [string]         ForecastRegionName from regObs
                   [observation]    The full observation on this regID
    """

    region_id, region_name, observation = None, None, None

    try:
        observation = go.get_data_as_class(reg_ids=reg_id)
        utm33x = observation[0].UTMEast
        utm33y = observation[0].UTMNorth
        date = observation[0].DtObsTime
        season = get_season_from_date(date.date())

        region_id, region_name = get_forecast_region_for_coordinate(utm33x, utm33y, season)

    except:
        error_msg = sys.exc_info()[0]
        ml.log_and_print('[error] getmisc.py -> get_forecast_region_for_regid: Exception on RegID={0}: {1}.'.format(reg_id, error_msg))

    return region_id, region_name, observation


def get_forecast_region_for_coordinate(utm33x, utm33y, year):
    """Maps an observation to the forecast regions used at the time the observation was made

    :param utm33x:
    :param utm33y:
    :param year:
    :return region_id, region_name:

    ## osx requires
    pip install pyshp
    pip install shapely

    ## windows requires
    pip install pyshp
    conda config --add channels conda-forge
    conda install shapely

    Helpful pages
    https://pypi.python.org/pypi/pyshp
    https://chrishavlin.wordpress.com/2016/11/16/shapefiles-tutorial/
    https://streamhacker.com/2010/03/23/python-point-in-polygon-shapely/
    """

    from shapely import geometry as gty
    import shapefile as sf

    if year == '2012-13':
        # varsling startet januar 2013
        file_name = 'VarslingsOmrF_fra_2013_jan'
        id_offset = 100
    elif year == '2013-14' or year == '2014-15' or year == '2015-16':
        # Svartisen (131) was started in april 2014
        # Nordenskioldland (130) and Hallingdal (132) was established in april 2014, but not used before the season after.
        # Salten (133) was started in mars 2015.
        # We tested Nordeskioldland (130) in may 2015.
        file_name = 'VarslingsOmrF_fra_2014_mars'
        id_offset = 100
    elif year == '2016-17' or year == '2017-18':
        # total makeover season 2016-17. Introducing A and B regions. Ids at 3000.
        file_name = 'VarslingsOmrF_fra_2016_des'
        id_offset = 0
    else:
        ml.log_and_print('[warning] getmisc.py -> get_forecast_region_for_coordinate: No valid year given.')
        file_name = 'VarslingsOmrF_fra_2016_des'
        id_offset = 0

    shape_file = sf.Reader('{0}{1}'.format(cenv.forecast_region_shapes, file_name))
    point = gty.MultiPoint([(utm33x, utm33y)]).convex_hull
    count = 0
    region = None

    for shape in shape_file.iterShapes():
        poly = gty.Polygon(shape.points)
        if point.within(poly):
            region = shape_file.records()[count]
        count += 1

    # records = sf.records()

    if region is None:
        region_name = 'Ikke gitt'
        region_id = 0
    else:
        region_name = region[1]
        region_id = region[0]+id_offset

    return region_id, region_name


def get_observer_nicks_given_ids(observer_ids):

    all_observers = get_observer_v()
    list_of_nicks = []

    for k,v in all_observers.items():
        if k in observer_ids:
            list_of_nicks.append(v)

    return list_of_nicks


class VarsomIncident:
    """The method get_varsom_incidents reads a csv file and this is the class each row is mapped into."""

    def __init__(self, row):

        self.date = dt.datetime.strptime(row[0], '%d.%m.%y').date() # 'dd.mm.yy'
        self.fatalities = int(row[1])
        self.people_involved = int(row[2])
        self.activity = row[3]
        self.trigger = row[4]
        self.location = row[5]
        self.municipality = row[6]
        self.county = row[7]
        regids = row[8].split(',')
        self.regid = []
        for r in regids:
            if r is not '':
                self.regid.append(int(r))
        self.varsom_news_url = row[9]
        self.comment = row[10]

        self.observations = []
        self.forecast = None
        self.region_id = None
        self.region_name = None

    def add_forecast_region(self, region_id_inn, region_name_inn):
        self.region_id = region_id_inn
        self.region_name = region_name_inn

    def add_forecast(self, forecast_inn):
        self.forecast = forecast_inn

    def add_observation(self, observation_inn):
        self.observations.append(observation_inn)


def get_varsom_incidents(add_forecast_regions=False, add_observations=False, add_forecasts=False):
    """Returns the incidents shown on varsom.no in a list of VarsomIncident objects.
    Data input is a utf-8 formatted csv file in input folder. Original file might have newlines and
    semicolons (;) in the cells. These need to be removed before saving as csv.

    :param add_forecast_regions:    [bool] If true the regid is used to get coordinates and the forecast region at the
                                    observation date is added. Note, if true, some time is to be expected getting data.
    :param add_observations:        [bool] If true the observation is added when looking up the region name. This
                                    option is only taken into account if add_forecast_regions is true.
    :param add_forecasts:           [bool] If true the forecast at that time and place is added to the incident. This
                                    option is only taken into account if add_forecast_regions is true.
    """

    incidents_file = '{}varsomsineskredulykker.csv'.format(cenv.input_folder)
    varsom_incidents = rf.read_csv_file(incidents_file, VarsomIncident)

    # map incident to forecast region
    if add_forecast_regions:
        for i in varsom_incidents:
            if i.regid == []:
                ml.log_and_print("[warning] getmisc.py -> get_varsom_incidents: No regid on incident on {}. No forecast region found.".format(i.date))
            else:
                region_id, region_name, observation = get_forecast_region_for_regid(i.regid[0])
                i.add_forecast_region(region_id, region_name)
                print("regid {}: {}".format(i.regid[0], i.date))

                if add_observations:
                    i.add_observation(observation[0])
                    if len(i.regid) > 1:
                        observations = go.get_data_as_class(reg_ids=i.regid[1:])
                        for o in observations:
                            i.add_observation(o)

        if add_forecasts:
            years = ['2014-15', '2015-16', '2016-17', '2017-18']        # the years with data

            all_forecasts = []
            for y in years:
                region_ids = get_forecast_regions(year=y)
                from_date, to_date = get_forecast_dates(y)
                all_forecasts += gd.get_forecasted_dangers(region_ids, from_date, to_date)

            for i in varsom_incidents:
                incident_date = i.date
                incident_region_id = i.region_id
                print("{}: {}".format(i.location, incident_date))
                for f in all_forecasts:
                    forecast_date = f.date
                    forecast_region_id = f.region_regobs_id
                    if incident_date == forecast_date:
                        if incident_region_id == forecast_region_id:
                            i.add_forecast(f)

    return varsom_incidents


if __name__ == "__main__":

    # included_observers = get_observer_dict_for_2017_18_plotting(5)
    # id1, region1 = get_forecast_region_for_coordinate(499335, 7576105, '2014-15')  # Lofoten?
    # id2, region2 = get_forecast_region_for_coordinate(687380, 7672286, '2012-13') # Tamok
    # a = get_observer_v()

    from_date = dt.date(2018, 1, 21)
    # from_date = dt.date.today()-dt.timedelta(days=1)
    to_date = dt.date.today()+dt.timedelta(days=1)

    region_ids = get_forecast_regions(year='2017-18')
    # region_ids = [116, 117]

    avalanche_indexes = get_avalanche_index(from_date, to_date, region_ids)

    # a = get_obs_location(from_date, to_date)

    # observer_list = [1090, 79, 43, 1084, 33, 119, 67, 101, 952, 41, 34, 125, 126, 8, 384, 955, 14, 841, 50, 175, 1123, 199, 1068, 1598, 1646, 637, 1664, 1307, 135, 307, 1212, 1279, 1310]
    # nicks = get_observer_nicks_given_ids(observer_list)
    # print(nicks)

    # observer_list = get_observer_dict_for_2015_16_ploting()
    # import makepickle as mp
    # mp.pickle_anything(observer_list, '{0}observerlist.pickle'.format(cenv.web_root_folder))

    # observer_nicks = get_observer_v()
    # trips = get_trip(from_date, to_date, output='csv')
    # observers = get_observer_group_member(group_id=51, output='Dict')
    # registration = get_registration(from_date, to_date, geohazard_tid=10)

    a = 1
