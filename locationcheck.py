# -*- coding: utf-8 -*-
__author__ = 'raek'


from varsomdata import getmisc as gm
from varsomdata import getobservations as go
from varsomdata import makepickle as mp
from runvarsomdata import setthisenvironment as ste
import datetime as dt


class MonthlyLocationData():

    def __init__(self, year_inn, month_inn):

        self.year = year_inn
        self.month = month_inn

        self.total_regs = 0
        self.app_locations = 0
        self.old_app_locations = 0


    def add_one_to_total_regs(self):
        self.total_regs += 1

    def add_one_to_app_locations(self):
        self.app_locations += 1

    def add_one_to_old_app_locations(self):
        self.old_app_locations += 1


if __name__ == "__main__":

    from_date = dt.date(2016, 11, 1)
    to_date = dt.date.today()+dt.timedelta(days=1)
    file_name = "{0}locationcheck.pickle".format(ste.output_folder)
    make_new = True

    if make_new:
        locations = gm.get_obs_location(from_date, to_date)
        observations = go.get_all_registrations(from_date, to_date, geohazard_tids=10)
        mp.pickle_anything([locations, observations], file_name)
    else:
        locations, observations = mp.unpickle_anything(file_name)

    regobs_locations = []
    for l in locations:
        # 50 is NVDB and 30 is Click in web map
        if l.UTMSourceTID != 50: #and l.UTMSourceTID != 30:
            regobs_locations.append(l)

    regobs_observations = []
    for o in observations:
        if not "drift@svv" in o.NickName:
            regobs_observations.append(o)
    '''
    o_n_l = []

    for o in regobs_observations:
        for l in regobs_locations:
            if o.LocationID == l.ObsLocationID:
                o_n_l.append([o,l])
                break


    monthly_data = {}

    for o in regobs_observations:
        key = '{0}-{1}'.format(o.DtRegTime.year, o.DtRegTime.month)
        if key not in monthly_data.keys():
            monthly_data[key] = MonthlyLocationData(o.DtRegTime.year, o.DtRegTime.month)
        monthly_data[key].add_one_to_total_regs()

    '''

    # app_loc/(total_regs-elrapp)
    # old_app_loc/(total_regs-elrapp)
    # re_use_loc/(total_regs-elrapp)
    # avg error with max min box



    a = 1