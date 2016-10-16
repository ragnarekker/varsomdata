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

        #forecast stuff
        self.main_message_no = None                                                 # [String]
        self.main_message_en = None
        self.nick = None
        self.avalanche_problems = []
        self.source = None
        self.avalanche_forecast = None
        self.avalanche_nowcast = None

        #obs eval 3 stuff
        self.forecast_correct = None
        self.forecast_correct_id = None


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
        self.nick = fe.remove_norwegian_letters(nick_inn)


    def set_source(self, source_inn):
        self.source = source_inn


    def set_avalanche_nowcast(self, avalanche_nowcast_inn):
        self.avalanche_nowcast = avalanche_nowcast_inn


    def set_avalanche_forecast(self, avalanche_forecast_inn):
        self.avalanche_forecast = avalanche_forecast_inn


    def set_forecast_correct(self, forecast_correct_inn, forecast_correct_id_inn):
        self.forecast_correct = fe.remove_norwegian_letters(forecast_correct_inn)
        self.forecast_correct_id = int(forecast_correct_id_inn)


def get_observed_dangers(region_id, start_date, end_date):
    """
    Gets observed avalanche dangers from AvalancheEvaluationV, AvalancheEvaluation2V and AvalancheEvaluation3V.

    :param region_id:       int
    :param start_date:
    :param end_date:
    :return:
    """

    print("Getting AvalancheWarnings for {0} from {1} til {2}").format(region_id, start_date, end_date)

    avalEval3 = gro.get_observed_danger_AvalancheEvaluation3V(region_id, start_date, end_date)
    avalEval2 = gro.get_observed_danger_AvalancheEvaluation2V(region_id, start_date, end_date)
    avalEval = gro.get_observed_danger_AvalancheEvaluationV(region_id, start_date, end_date)

    evaluations = avalEval + avalEval2 +avalEval3

    # sort list by date
    evaluations = sorted(evaluations, key=lambda AvalancheEvaluation: AvalancheEvaluation.date)

    return evaluations


def get_forecasted_dangers(region_id, start_date, end_date, include_problems=False, include_ikke_vurdert=False):
    '''Gets forecasted dangers for ONE region. If specified, the avalanche problems are included.

    :param region_id:               [int] only one region. ID as given in regObs
    :param start_date:              [date or string as yyyy-mm-dd] gets dates [from, to>
    :param end_date:                [date or string as yyyy-mm-dd] gets dates [from, to>
    :param include_problems:        [bool] if true, avalanche probelms are included. This takes more time ans additional requests.
    :param include_ikke_vurdert:    [bool] if true, it includes frocasts where danger_level = 0

    :return:
    '''

    # get all warning and problems for this region and then loop though them joining them where dates match.
    region_warnings = gfa.get_warnings(region_id, start_date, end_date)

    if include_problems:
        problems = gro.get_problems_from_AvalancheWarnProblemV(region_id, start_date, end_date)

        for i in range(0, len(region_warnings), 1):
            for j in range(0, len(problems), 1):
                if region_warnings[i].date == problems[j].date:
                    region_warnings[i].add_problem(problems[j])

        # make sure all problems are ordered from lowest id (main problem) to largest.
        for w in region_warnings:
            w.avalanche_problems = sorted(w.avalanche_problems, key=lambda AvalancheProblem: AvalancheProblem.order)

    if not include_ikke_vurdert:
        all_non_zero_warnings = []

        for w in region_warnings:
            if w.danger_level != 0:
                all_non_zero_warnings.append(w)

        region_warnings = all_non_zero_warnings

    return region_warnings


def get_all_dangers(region_ids, start_date, end_date):
    """Method does NOT include avalanhe problems. Gets all avalanche dangers dangers, both forecasted and
    observed in a given region for a given time period.

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
        observed += get_observed_dangers(region_id, start_date, end_date)

    all_dangers = warnings + observed

    # Sort by date
    all_dangers = sorted(all_dangers, key=lambda AvalancheDanger: AvalancheDanger.date)

    return all_dangers


if __name__ == "__main__":

    region_id = [117, 128]  # Trollheimen

    from_date = dt.date(2016, 01, 28)
    to_date = dt.date.today()
    to_date = dt.date(2016, 2, 3)

    alle = get_all_dangers(region_id, from_date, to_date)

    a = 1