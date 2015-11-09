# -*- coding: utf-8 -*-
__author__ = 'raek'

import getdangers as gd
import getobservations as go
import getkdvelements as gkdv
import setenvironment as env
import datetime as dt
import readfile as rf
import makepickle as mp


class ActivityAndDanger():

    def __init__(self):

        self.danger_level = None        # in current region at current date

        self.avalanche_trigger = []
        self.destructive_size = None
        self.estimated_number = None

        self.observation_count = 0

        self.x = None
        self.y = None

        self.cell_colour = None

    def add_configuration_row(self, row):

        self.danger_level = row[0]
        self.destructive_size = row[2]
        self.estimated_number = row[1]

        self.x = row[5]
        self.y = row[6]

        self.cell_colour = row[7]

        return


class DataOnDateInRegion():

    def __init__(self, date, region_name):

        self.date = date
        self.region_name = region_name

        self.forecast = []
        self.danger_sign = []
        self.avalanche = []
        self.avalanche_activity = []

        self.most_valued_observation = None
        self.highest_value = -1


class OrderOfSizeAndNumber():


    def __init__(self):
        self.estimated_num = None
        self.destructive_size = None
        self.que_number = None


    def add_configuration_row(self, row):
        self.estimated_num = row[0]
        self.destructive_size = row[1]
        self.que_number = row[2]
        return


def make_data_set(region_id, from_date, to_date):
    """Makes the dataset of all observed avalanche activity (inl signs and isingle avalanches obs) and mapps
    to forecasts for those days.

    :param region_id:   [int or list of ints]
    :param from_date:   [date]
    :param to_date:     [date]
    :return:
    """

    # get all data
    dangers = gd.get_all_dangers(region_id, from_date, to_date)
    avalanches = go.get_avalanche_activity(region_id, from_date, to_date)
    single_avalanches = go.get_avalanche(region_id, from_date, to_date)
    danger_signs = go.get_danger_sign(region_id, from_date, to_date)

    # List of only forecasts
    forecasted_dangers = []
    for d in dangers:
        if 'Forecast' in d.data_table and d.danger_level != 0:
            forecasted_dangers.append(d)

    # List of only valid activity observations
    observed_activity = []
    for a in avalanches:
        if not 'Ikke gitt' in a.EstimatedNumName:
            observed_activity.append(a)

    # list of relevant danger observations
    danger_sign_avalanches = []
    for ds in danger_signs:
        if 'Ferske skred' in ds.DangerSignName or 'Ingen faretegn observert' in ds.DangerSignName:
            danger_sign_avalanches.append(ds)

    # list of relevant singel avalanches
    observed_avalanche = []
    for sa in single_avalanches:
        if not 'Ikke gitt' in sa.DestructiveSizeName:
            observed_avalanche.append(sa)

    # Make list of all regions pr date and append forecasts and observations.
    data_date_region = []
    for d in forecasted_dangers:
        danger_date = d.date
        print '{0}'.format(danger_date)
        danger_region_name = d.region_name

        data = DataOnDateInRegion(danger_date, danger_region_name)
        data.forecast.append(d)

        for a in observed_activity:
            aval_date = a.DtAvalancheTime.date()
            aval_region_name = a.ForecastRegionName
            if aval_date == danger_date and aval_region_name == danger_region_name:
                data.avalanche_activity.append(a)

        for da in danger_sign_avalanches:
            aval_date = da.DtObsTime.date()
            aval_region_name = da.ForecastRegionName
            if aval_date == danger_date and aval_region_name == danger_region_name:
                data.danger_sign.append(da)

        for oa in observed_avalanche:
            aval_date = oa.DtAvalancheTime.date()
            aval_region_name = oa.ForecastRegionName
            if aval_date == danger_date and aval_region_name == danger_region_name:
                data.avalanche.append(oa)

        data_date_region.append(data)

    # discard days and regions where no observations present
    date_region = []
    for d in data_date_region:
        if not len(d.avalanche_activity) == 0 or not len(d.danger_sign) == 0 or not len(d.avalanche) == 0:
            date_region.append(d)

    return date_region, forecasted_dangers


def find_most_valued_observations(date_region):

    order = rf.read_configuration_file('{0}aval_dl_order_of_size_and_num.csv'.format(env.input_folder), OrderOfSizeAndNumber)
    for d in date_region:

        for aa in d.avalanche_activity:
            que_number = 0
            for o in order:
                if o.estimated_num in aa.EstimatedNumName and o.destructive_size in aa.DestructiveSizeName:
                    que_number = o.que_number
            if d.highest_value < que_number:
                d.highest_value = que_number
                d.most_valued_observation = aa

        for a in d.avalanche:
            que_number = 0
            for o in order:
                if o.estimated_num in 'Ett (1)' and o.destructive_size in a.DestructiveSizeName:
                    que_number = o.que_number
            if d.highest_value < que_number:
                d.highest_value = que_number
                d.most_valued_observation = a

        for ds in d.danger_sign:
            if 'Ferske skred' in ds.DangerSignName:
                if d.highest_value < 2:
                    d.highest_value = 2
                    d.most_valued_observation = ds
            if 'Ingen faretegn observert' in ds.DangerSignName:
                if d.highest_value < 1:
                    d.highest_value = 1
                    d.most_valued_observation = ds

    return date_region


if __name__ == "__main__":

    # master igjen?
    region_id = [112, 117, 116, 128]

    #### Get all regions
    # region_id = []
    # ForecastRegionKDV = gkdv.get_kdv('ForecastRegionKDV')
    # for k, v in ForecastRegionKDV.iteritems():
    #     if 99 < k < 150 and v.IsActive is True:
    #         region_id.append(v.ID)

    from_date = dt.date(2014, 11, 30)
    to_date = dt.date(2015, 6, 1)
    #to_date = dt.date.today()

    #### get and make the data set
    # date_region, forecasted_dangers = make_data_set(region_id, from_date, to_date)
    # mp.pickle_anything([date_region, forecasted_dangers], '{0}runforavalancheactivity.pickle'.format(env.local_storage))

    #### Find the observaton of highest value pr region pr date
    # date_region, forecasted_dangers = mp.unpickle_anything('{0}runforavalancheactivity.pickle'.format(env.local_storage))
    # date_region = find_most_valued_observations(date_region)
    # mp.pickle_anything([date_region, forecasted_dangers], '{0}runforavalancheactivity_with_most_valued.pickle'.format(env.local_storage))

    #### ready to add to the elements of the plot?
    date_region, forecasted_dangers = mp.unpickle_anything('{0}runforavalancheactivity_with_most_valued.pickle'.format(env.local_storage))
    elements = rf.read_configuration_file('{0}aval_dl_configuration.csv'.format(env.input_folder), ActivityAndDanger)


    '''
    for d in data_date_region:
        for e in elements:
            if danger in e.danger_level:
                if size in e.destructive_size:
                    if number in e.estimated_number:
                        e.observation_count += 1
                        e.avalanche_trigger.append(a.AvalancheTriggerName)

    used_elements = []
    for e in elements:
        if e.observation_count is not 0:
            used_elements.append(e)
    '''


    a = 1