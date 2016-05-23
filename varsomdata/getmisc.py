# -*- coding: utf-8 -*-
__author__ = 'raek'


import datetime as dt
import requests as requests
import csv as csv
import getobservations as go
import readfile as rf
import operator
import fencoding as fe
import setenvironment as env
import getkdvelements as kdv



class Trip():

    def __init__(self, d):

        self.TripID = int(d["TripID"])
        self.ObserverID = int(d["ObserverID"])
        self.ObsLocationID = int(d["ObsLocationID"])
        self.GeoHazardTID = int(d["GeoHazardTID"])
        self.TripTypeTID = int(d["TripTypeTID"])
        self.ObservationExpectedTime = fe.unix_time_2_normal( int(d["ObservationExpectedTime"][6:-2]) )
        self.Comment = fe.remove_norwegian_letters(d["Comment"])
        self.IsFinished = bool(d["IsFinished"])
        self.TripRegistrationTime = fe.unix_time_2_normal( int(d["TripRegistrationTime"][6:-2]) )
        if d["TripFinishedTime"] is not None:
            self.TripFinishedTime = fe.unix_time_2_normal( int(d["TripFinishedTime"][6:-2]) )
        else:
            self.TripFinishedTime = None
        self.DeviceID = d["DeviceID"]

        self.TripTypeName = kdv.get_name("TripTypeKDV", self.TripTypeTID)


def get_trip(from_date, to_date, geohazard_tid=None, output='List'):
    """
    :param from_date:       [date] A query returns [from_date, to_date>
    :param to_date:         [date] A query returns [from_date, to_date>
    :param geohazard_tid:   [int] 10 is snow, 20,30,40 are dirt, 60 is water and 70 is ice

    :return:

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


    odata_filter = fe.add_norwegian_letters(odata_filter)

    url = "http://api.nve.no/hydrology/regobs/{0}/Odata.svc/Trip/?$filter={1}&$format=json"\
        .decode('utf8').format(env.api_version, odata_filter)

    print "getmisc.py -> get_trip: ..to {0}".format(fe.remove_norwegian_letters(url))

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
        return


class ObserverGroupMember():

    def __init__(self, d):

        self.NickName = fe.remove_norwegian_letters(d["NickName"])
        self.ObserverGroupDescription = fe.remove_norwegian_letters(d["ObserverGroupDescription"])
        self.ObserverGroupID = int(d["ObserverGroupID"])
        self.ObserverGroupName = fe.remove_norwegian_letters(d["ObserverGroupName"])
        self.ObserverID = int(d["ObserverID"])


def get_observer_group_member(group_id=None, output='List'):

    if group_id is None:
        url = 'http://api.nve.no/hydrology/regobs/v0.9.9/Odata.svc/ObserverGroupMemberV/?$format=json'
    else:
        url = 'http://api.nve.no/hydrology/regobs/v0.9.9/Odata.svc/ObserverGroupMemberV/?$filter=ObserverGroupID%20eq%20{0}&$format=json'.format(group_id)
    print "getmisc.py -> get_trip: ..to {0}".format(fe.remove_norwegian_letters(url))

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


class Registration():

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


def get_registration(from_date, to_date, output='List', geohazard_tid=None, ApplicationID='', include_deleted=False):
    '''Gets data from the Registration table. Adds observer nickname if list is requested and if not otherwize
    specified deleted registrations are taken out.

    :param from_date:
    :param to_date:
    :param output:
    :param geohazard_tid:
    :param ApplicationID:
    :param include_deleted:
    :return:
    '''

    odata_filter = ""
    if geohazard_tid is not None:
        odata_filter += "GeoHazardTID eq {0} and ".format(geohazard_tid)
    odata_filter += "DtRegTime gt datetime'{0}' and DtRegTime lt datetime'{1}'".format(from_date, to_date)
    if "Web and app" in ApplicationID: # does not work..
        odata_filter += " and (ApplicationId eq guid'{0}' or ApplicationId eq guid'{1}')".format('','')

    url = 'http://api.nve.no/hydrology/regobs/{0}/Odata.svc/{1}/?$filter={2}&$format=json'.format(env.api_version, "Registration", odata_filter)
    print "getmisc.py -> get_registration: ..to {0}".format(fe.remove_norwegian_letters(url))

    result = requests.get(url).json()
    data = result['d']['results']

    # if more than 1000 elements are requested, odata truncates data to 1000. We do more requests
    if len(data) == 1000:
        time_delta = to_date - from_date
        date_in_middle = from_date + time_delta/2
        data = get_registration(from_date, date_in_middle, output='Raw', geohazard_tid=geohazard_tid, ApplicationID=ApplicationID) \
                 + get_registration(date_in_middle, to_date, output='Raw', geohazard_tid=geohazard_tid, ApplicationID=ApplicationID)

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


class AvalancheIndex():

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
        elif self.estimated_num is not None and self.destructive_size is not None:
            for i in index_definition:
                if i.estimated_num in self.estimated_num and i.destructive_size in self.destructive_size:
                    self.index = int(i.index)


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
    '''

    :param from_date:
    :param to_date:
    :param region_ids:
    :param observer_ids:
    :return:
    '''

    # get all data
    avalanche_activities = go.get_avalanche_activity(from_date, to_date, region_ids=region_ids, observer_ids=observer_ids)
    avalanche_activities_2 = go.get_avalanche_activity_2(from_date, to_date, region_ids=region_ids, observer_ids=observer_ids)
    avalanches = go.get_avalanche(from_date, to_date, region_ids=region_ids, observer_ids=observer_ids)
    danger_signs = go.get_danger_sign(from_date, to_date, region_ids=region_ids, observer_ids=observer_ids)

    # get index definition
    index_definition = rf.read_configuration_file('{0}aval_dl_order_of_size_and_num.csv'.format(env.input_folder), AvalancheIndex)

    avalanche_indexes = []

    for aa in avalanche_activities:

        ai = AvalancheIndex()
        ai.set_num_and_size_and_index(aa.EstimatedNumName, aa.DestructiveSizeName, index_definition)
        ai.set_date_region_observation(aa.DtAvalancheTime, aa.ForecastRegionName, aa)
        avalanche_indexes.append(ai)

    for aa in avalanche_activities_2:

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
    """Selects all data from the ObserverV view. Returns all observers. Not only the topp 1000 for some reason.

    :return: a dictionary of key/ObserverID : value/NickName
    """

    url = 'http://api.nve.no/hydrology/regobs/{0}/Odata.svc/ObserverV?$format=json'.format(env.api_version)
    result = requests.get(url).json()
    data = result['d']['results']

    observer_nicks = {}
    for d in data:
        key = d['ObserverId']
        val = fe.remove_norwegian_letters(d['NickName'])
        observer_nicks[key] = val

    return observer_nicks


def get_active_forecast_regions():
    '''Get all active forecast regions. IsActive = True in ForecastRegionKDV
    '''

    region_ids = []
    ForecastRegionKDV = kdv.get_kdv('ForecastRegionKDV')
    for k, v in ForecastRegionKDV.iteritems():
        if 100 < k < 150 and v.IsActive is True:
            region_ids.append(v.ID)

    return region_ids


def get_observer_nicks_given_ids(observer_ids):

    all_observers = get_observer_v()
    list_of_nicks = []

    for k,v in all_observers.iteritems():
        if k in observer_ids:
            list_of_nicks.append(v)

    return list_of_nicks


def get_observer_dict_for_2015_16_ploting():
    '''Returns a dict og observer id : observer nick.

    '''

    from_date = dt.date(2015, 12, 1)
    to_date = dt.date.today()+dt.timedelta(days=1)

    # get all registrations (all forecasts and elrapp also. Filter does not work)
    registration = get_registration(from_date, to_date, geohazard_tid=10)

    # make dict of all observers and how much they contributed
    observers_dict = {}
    for r in registration:
        if r.ObserverID not in observers_dict.keys():
            observers_dict[r.ObserverID] = 1
        else:
            observers_dict[r.ObserverID] += 1

    # list of all observerids and their nicks
    observer_nicks = get_observer_v()

    # only the worthy are selected. More than 5 registrations and not elrapp.
    observers_dict_select = {}
    for k,v in observers_dict.iteritems():
        if v > 5:
            if k is not 237:        # not elrapp
                observers_dict_select[k] = observer_nicks[k]

    return observers_dict_select


if __name__ == "__main__":

    from_date = dt.date(2016, 4, 1)
    #from_date = dt.date.today()-dt.timedelta(days=1)
    to_date = dt.date.today()+dt.timedelta(days=1)

    region_ids = [116, 117]
    avalanche_indexes = get_avalanche_index(from_date, to_date, region_ids)

    # observer_list = [1090, 79, 43, 1084, 33, 119, 67, 101, 952, 41, 34, 125, 126, 8, 384, 955, 14, 841, 50, 175, 1123, 199, 1068, 1598, 1646, 637, 1664, 1307, 135, 307, 1212, 1279, 1310]
    # nicks = get_observer_nicks_given_ids(observer_list)
    # print nicks

    '''
    observer_list = get_observer_dict_for_2015_16_ploting()
    import makepickle as mp
    mp.pickle_anything(observer_list, '{0}observerlist.pickle'.format(env.web_root_folder))
    '''
    # observer_nicks = get_observer_v()
    # trips = get_trip(from_date, to_date, output='csv')
    # observers = get_observer_group_member(group_id=51, output='Dict')
    registration = get_registration(from_date, to_date, geohazard_tid=10)

    a = 1