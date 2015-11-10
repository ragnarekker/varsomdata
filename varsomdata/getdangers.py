# -*- coding: utf-8 -*-
__author__ = 'raek'

import getregobs as gro
import getforecastapi as gfa
import datetime as dt
import types as types
import fencoding as fe


class AvalancheDanger():


    def __init__(self, region_regobs_id_inn, region_name_inn, data_table_inn, date_inn, danger_level_inn, danger_level_name_inn):
        '''
        AvalancheDanger object since there are 3 different tables to get regObs-data from and one from the forecast

        :param region_regobs_id_inn:
        :param region_name_inn:
        :param data_table_inn:
        :param date_inn:
        :param danger_level_inn:
        :param danger_level_name_inn:
        :return:

        Other variables:
        main_message_no
        main_message_en
        nick                            [string]    Nickname of the observer/forecaster who issued the avalanche danger
        metadata:                       [{key:value}, ..]
        avalanche_problems:             [AvalancheProblem, ..]
        '''

        if region_regobs_id_inn < 100: # makes sure that it is regObs ID used in this program
            region_regobs_id_inn = region_regobs_id_inn + 100

        self.metadata = {}                                                          # [dictionary] {key:value, key:value, ..}
        self.region_regobs_id = region_regobs_id_inn                                # [int]
        self.region_name = fe.remove_norwegian_letters(region_name_inn)             # [String]
        self.data_table = fe.remove_norwegian_letters(data_table_inn)               # [String]

        if isinstance(date_inn, dt.datetime): # makes sure we only have the date
            self.add_metadata("Original datetime", date_inn)
            date_inn = date_inn.date()
        self.date = date_inn                                                        # [date]

        self.danger_level = danger_level_inn                                        # [Int]
        self.danger_level_name = fe.remove_norwegian_letters(danger_level_name_inn) # [String]

        self.main_message_no = None                                                 # [String]
        self.main_message_en = None
        self.nick = None
        self.avalanche_problems = []
        self.source = None


    def add_problem(self, problem_inn):
        self.avalanche_problems.append(problem_inn)
        self.avalanche_problems.sort(key=lambda problems: problems.order)           # make sure lowest index (main problem) is first


    def set_main_message_no(self, main_message_no_inn):
        self.main_message_no = fe.remove_norwegian_letters(main_message_no_inn)
        self.add_metadata('Original norwegian main message', main_message_no_inn)


    def add_metadata(self, key, value):
        self.metadata[key] = value


    def set_main_message_en(self, main_message_en_inn):
        self.main_message_en = fe.remove_norwegian_letters(main_message_en_inn)


    def set_nick(self, nick_inn):
        self.nick = nick_inn


    def set_source(self, source_inn):
        self.source = source_inn


def get_all_dangers(region_ids, start_date, end_date):
    """
    Gets all avalanche dangers dangers, both forecasted and observed in a given region for a given time period.
    Method does not include avalanhe problems.

    :param region_id:   [int or list of ints]
    :param start_date:  [date]
    :param end_date:    [date]

    :return:
    """

    # If input isn't a list, make it so
    if not isinstance(region_ids, types.ListType):
        region_ids = [region_ids]

    warnings = []
    observed = []

    for region_id in region_ids:
        warnings += gfa.get_warnings(region_id, start_date, end_date)
        observed += gro.get_observed_dangers(region_id, start_date, end_date)

    all_dangers = warnings + observed

    # Sort by date
    all_dangers = sorted(all_dangers, key=lambda AvalancheDanger: AvalancheDanger.date)

    return all_dangers


if __name__ == "__main__":

    region_id = 117  # Trollheimen

    # from_date = "2014-12-01"
    # to_date = "2015-02-01"
    from_date = dt.date(2015, 4, 1)
    to_date = dt.date.today()

    alle = get_all_dangers(region_id, from_date, to_date)

    a = 1