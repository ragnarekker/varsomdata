# -*- coding: utf-8 -*-
import getdangers as gd

import getkdvelements as gkdv
import setenvironment as env
import datetime as dt
import makepickle as mp
import getmisc as gm

__author__ = 'raek'


class ElrappData():

    def __init__(self, date_inn, region_inn):

        self.date = date_inn
        self.region = region_inn
        self.danger_forecast = None
        self.danger_elrapp = None
        self.regid_danger = None
        self.avalanche_index = None
        self.avalanche_observation = None
        self.regid_observation = None

    def set_danger_forecast(self, danger_forecast_inn):
        self.danger_forecast = danger_forecast_inn

    def set_danger_elrapp(self, danger_elrapp_inn):
        self.danger_elrapp = danger_elrapp_inn

    def set_index_and_observation(self, index_inn, observation_inn, regid_inn):
        self.avalanche_index = index_inn
        self.avalanche_observation = observation_inn
        self.regid_observation = regid_inn


if __name__ == "__main__":

    get_new = True
    ### Get all regions
    #region_ids = [107, 108, 110]

    region_ids = []
    ForecastRegionKDV = gkdv.get_kdv('ForecastRegionKDV')
    for k, v in ForecastRegionKDV.iteritems():
       if 99 < k < 150 and v.IsActive is True:
           region_ids.append(v.ID)

    from_date = dt.date(2015, 11, 30)
    to_date = dt.date(2016, 6, 1)
    #to_date = dt.date.today()

    drift_nick = 'drift@svv'
    #drift_id = 237
    pickle_file_name = '{0}runelrappdata.pickle'.format(env.local_storage)
    output_file = '{0}elrappdata 2015-16.csv'.format(env.output_folder)

    if get_new:
        dangers = gd.get_all_dangers(region_ids, from_date, to_date)
        forecast_danger = []
        drift_svv_danger = []
        for d in dangers:
            if 'Varsel' in d.source:
                forecast_danger.append(d)
            if d.nick is not None:
                if drift_nick in d.nick:
                    drift_svv_danger.append(d)

        aval_indexes = gm.get_avalanche_index(from_date, to_date, region_ids=region_ids)#, nick_names=drift_nick)
        drift_svv_index = []
        for i in aval_indexes:
            if drift_nick in i.observation.NickName:
                drift_svv_index.append(i)

        mp.pickle_anything([forecast_danger, drift_svv_danger, drift_svv_index], pickle_file_name)

    else:
        forecast_danger, drift_svv_danger, drift_svv_index = mp.unpickle_anything(pickle_file_name)

    # order and group by date:
    elrapp_data_list = []
    for fd in forecast_danger:
        ed = ElrappData(fd.date, fd.region_name)
        ed.set_danger_forecast(fd.danger_level_name)
        elrapp_data_list.append(ed)

    for dd in drift_svv_danger:
        for ed in elrapp_data_list:
            if ed.date == dd.date and ed.region == dd.region_name:
                ed.set_danger_elrapp(dd.danger_level_name)

    for di in drift_svv_index:
        for ed in elrapp_data_list:
            if ed.date == di.date.date() and ed.region == di.region_name:
                ed.set_index_and_observation(di.index, di.observation, di.observation.RegID)

    elrapp_compact_list = []
    for ed in elrapp_data_list:
        if ed.danger_elrapp is not None or ed.avalanche_index is not None or ed.avalanche_observation is not None:
            elrapp_compact_list.append(ed)

    # Write to .csv
    with open(output_file, "w") as  myfile:
        myfile.write('Dato;Region;Varslet faregrad;Elrapp faregrad;index;observasjon type;regObs observasjon\n')
        for ec in elrapp_compact_list:
            myfile.write('{0};{1};{2};{3};{4};{5};http://www.regobs.no/Registration/{6}\n'.format(
                ec.date, ec.region, ec.danger_forecast,
                ec.danger_elrapp, ec.avalanche_index,
                ec.avalanche_observation.__class__.__name__, ec.regid_observation))


    a = 1


