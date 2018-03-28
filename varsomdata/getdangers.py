# -*- coding: utf-8 -*-
__author__ = 'raek'


import datetime as dt
from varsomdata import getobservations as go
from varsomdata import makelogs as ml
from varsomdata import getmisc as gm
from varsomdata import getforecastapi as gfa
from varsomdata import setcoreenvironment as cenv


class AvalancheDanger:

    def __init__(self, region_id_inn, region_name_inn, data_table_inn, date_inn, danger_level_inn, danger_level_name_inn):
        """AvalancheDanger object tries to be common ground for three different tables in regObs and
        one from the forecast.

        Parameters part of the constructor:
        :param region_id_inn:           [int]       Region ID is as given in ForecastRegionKDV.
        :param region_name_inn:         [String]    Region name as given in ForecastRegionKDV.
        :param data_table_inn:          [String]    Which table/View in regObs-database is the data from
        :param date_inn:                [Date]      Date. If DateTime given it is parsed.
        :param danger_level_inn:        [int]       Danger level id (0-5)
        :param danger_level_name_inn:   [String]    Danger level written.
        :return:

        Other variables:
        metadata:                       [{key:value}, ..]
        avalanche_problems:             [list of gp.AvalanchProblems] There are allways problems in forecasts.
        """

        # In nov 2016 we updated all regions to have ids in th 3000´s. GIS and regObs equal.
        # Before that GIS har numbers 0-99 and regObs 100-199. Messy..
        # Convetion is regObs ids always
        if region_id_inn < 100:
            region_id_inn += 100

        self.metadata = {}                              # [dictionary] {key:value, key:value, ..}
        self.region_regobs_id = region_id_inn           # [int]
        self.region_name = region_name_inn              # [String]
        self.data_table = data_table_inn                # [String]
        self.set_date(date_inn)                         # [date]
        self.danger_level = danger_level_inn            # [Int]
        self.danger_level_name = danger_level_name_inn  # [String]

        #### Values declared when needed.
        # self.nick = None                                # [String] regObs NickName of observer or forecaster who issued the avalanche danger
        # self.source = None                              # [String] Usually 'Observasjon' or 'Varsel'
        # self.avalanche_forecast = None                  # [String] Written forecast.
        # self.avalanche_nowcast = None                   # [String] The summery of the snowcover now
        # self.municipal_name = None

        #### forecast stuff
        self.avalanche_problems = []                    # [list of gp.AvalanchProblems] In forecasts there are always problems
        # self.main_message_no = None                     # [String] The main message in norwegian
        # self.main_message_en = None                     # [String] The main message in english

        ##### obs eval 3 stuff
        # self.forecast_correct = None                    # [String] Droppdown value if the forecast is correct or no
        # self.forecast_correct_id = None                 # [int]
        # self.forecast_comment = None                    # [String] Comment from observer

    def set_regid(self, regid_inn):
        self.regid = regid_inn

    def set_date(self, date_inn):

        # makes sure we only have the date, but we keep the datetime as metadata
        if isinstance(date_inn, dt.datetime):
            self.add_metadata("Original DtObsTime", date_inn)
            date_inn = date_inn.date()

        self.date = date_inn

    def set_registration_time(self, registration_time_inn):
        # DtRegTime is when the evaluation was registered in regObs.
        self.registration_time = registration_time_inn

    def set_municipal(self, municipal_inn):
        try:
            self.municipal_name = municipal_inn
        except ValueError:
            print("Got ValueError on setting municipal name on {0} for {1}.")\
                .format(self.date, self.region_name)
        except:
            print("Got un expected error on setting municipal name on {0} for {1}.")\
                .format(self.date, self.region_name)

    def set_url(self, url_inn):
        self.url = url_inn

    def add_problem(self, problem_inn):
        self.avalanche_problems.append(problem_inn)
        # make sure lowest index (main problem) is first
        self.avalanche_problems.sort(key=lambda problems: problems.order)

    def set_main_message_no(self, main_message_no_inn):
        # Remove double spaces, tabs, newlines etc
        self.main_message_no = ' '.join(main_message_no_inn.split())

    def set_main_message_en(self, main_message_en_inn):
        # Remove double spaces, tabs, newlines etc
        self.main_message_en = ' '.join(main_message_en_inn.split())

    def set_nick(self, nick_inn):
        self.nick = nick_inn

    def set_competence_level(self, competence_level_inn):
        self.competence_level = competence_level_inn

    def set_source(self, source_inn):
        self.source = source_inn

    def set_avalanche_nowcast(self, avalanche_nowcast_inn):
        self.avalanche_nowcast = avalanche_nowcast_inn

    def set_avalanche_forecast(self, avalanche_forecast_inn):
        self.avalanche_forecast = avalanche_forecast_inn

    def set_forecast_correct(self, forecast_correct_inn, forecast_correct_id_inn=None):

        if forecast_correct_id_inn is not None:
            forecast_correct_id_inn = int(forecast_correct_id_inn)

        self.forecast_correct_id = forecast_correct_id_inn
        self.forecast_correct = forecast_correct_inn

    def set_forecast_comment(self, forecast_comment_inn):
        self.forecast_comment = forecast_comment_inn

    def add_metadata(self, key, value):
        self.metadata[key] = value


def _make_eval1_conform(evaluations_1):
    """Maps the AvalancheEvaluation to the conformity of a common AvalancheDanger object.

    :param evaluations_1:   [list of AvalancheEvaluation] These are the classes used on getobservations.py
    :return:                [list of AvalancheDanger]
    """

    dangers = []

    for e in evaluations_1:
        region_id = e.ForecastRegionTID
        region_name = e.ForecastRegionName
        data_table = 'AvalancheEvaluation'
        date = e.DtObsTime
        danger_level = e.AvalancheDangerTID
        danger_level_name = e.AvalancheDangerName

        danger = AvalancheDanger(region_id, region_name, data_table, date, danger_level, danger_level_name)

        danger.set_avalanche_nowcast(e.AvalancheEvaluation)

        danger.set_regid(e.RegID)
        danger.set_source('Observation')
        danger.set_url('{0}{1}'.format(cenv.registration_basestring, e.RegID))
        danger.set_registration_time(e.DtRegTime)
        danger.set_municipal(e.MunicipalName)
        danger.set_nick(e.NickName)
        danger.set_competence_level(e.CompetenceLevelName)
        danger.add_metadata('Original data', e)

        dangers.append(danger)

    return dangers


def _make_eval2_conform(evaluations_2):
    """Maps the AvalancheEvaluation2 to the conformity of a common AvalancheDanger object.

    :param evaluations_2:   [list of AvalancheEvaluation2] These are the classes used on getobservations.py
    :return:                [list of AvalancheDanger]
    """

    dangers = []

    for e in evaluations_2:
        region_id = e.ForecastRegionTID
        region_name = e.ForecastRegionName
        data_table = 'AvalancheEvaluation2'
        date = e.DtObsTime
        danger_level = e.AvalancheDangerTID
        danger_level_name = e.AvalancheDangerName


        danger = AvalancheDanger(region_id, region_name, data_table, date, danger_level, danger_level_name)

        danger.set_avalanche_nowcast(e.AvalancheEvaluation)
        danger.set_avalanche_forecast(e.AvalancheDevelopment)

        danger.set_regid(e.RegID)
        danger.set_source('Observation')
        danger.set_url('{0}{1}'.format(cenv.registration_basestring, e.RegID))
        danger.set_registration_time(e.DtRegTime)
        danger.set_municipal(e.MunicipalName)
        danger.set_nick(e.NickName)
        danger.set_competence_level(e.CompetenceLevelName)
        danger.add_metadata('Original data', e)

        dangers.append(danger)

    return dangers


def _make_eval3_conform(evaluations_3):
    """Maps the AvalancheEvaluation3 to the conformity of a common AvalancheDanger object.

    :param evaluations_3:   [list of AvalancheEvaluation3] These are the classes used on getobservations.py
    :return:                [list of AvalancheDanger]
    """

    dangers = []

    for e in evaluations_3:
        region_id = e.ForecastRegionTID
        region_name = e.ForecastRegionName
        data_table = 'AvalancheEvaluation3'
        date = e.DtObsTime
        danger_level = e.AvalancheDangerTID
        danger_level_name = e.AvalancheDangerName

        danger = AvalancheDanger(region_id, region_name, data_table, date, danger_level, danger_level_name)

        danger.set_avalanche_nowcast(e.AvalancheEvaluation)
        danger.set_avalanche_forecast(e.AvalancheDevelopment)
        danger.set_forecast_correct(e.ForecastCorrectName, e.ForecastCorrectTID)
        danger.set_forecast_comment(e.ForecastComment)

        danger.set_regid(e.RegID)
        danger.set_source('Observation')
        danger.set_url('{0}{1}'.format(cenv.registration_basestring, e.RegID))
        danger.set_registration_time(e.DtRegTime)
        danger.set_municipal(e.MunicipalName)
        danger.set_nick(e.NickName)
        danger.set_competence_level(e.CompetenceLevelName)
        danger.add_metadata('Original data', e)

        dangers.append(danger)

    return dangers


def get_observed_dangers(region_ids, from_date, to_date, lang_key=1):
    """Gets observed avalanche dangers from AvalancheEvaluationV, AvalancheEvaluation2V and AvalancheEvaluation3V.

    :param region_ids:          [int or list of ints] ForecastRegionTID
    :param from_date:           [date or string as "YYYY-MM-DD"]
    :param to_date:             [date or string as "YYYY-MM-DD"]

    :return:
    """

    evaluations_1 = go.get_avalanche_evaluation(region_ids=region_ids, from_date=from_date, to_date=to_date, lang_key=lang_key)
    evaluations_2 = go.get_avalanche_evaluation_2(region_ids=region_ids, from_date=from_date, to_date=to_date, lang_key=lang_key)
    evaluations_3 = go.get_avalanche_evaluation_3(region_ids=region_ids, from_date=from_date, to_date=to_date, lang_key=lang_key)

    conform_evals_1 = _make_eval1_conform(evaluations_1)
    conform_evals_2 = _make_eval2_conform(evaluations_2)
    conform_evals_3 = _make_eval3_conform(evaluations_3)

    evaluations = conform_evals_1 + conform_evals_2 + conform_evals_3

    # sort list by date
    evaluations = sorted(evaluations, key=lambda AvalancheEvaluation: AvalancheEvaluation.date)

    return evaluations


def get_forecasted_dangers(region_ids, from_date, to_date, include_ikke_vurdert=False, lang_key=1):
    """Gets forecasted dangers for multiple regions.

    :param region_id:               [int] only one region. ID as given in regObs
    :param from_date:               [date or string as yyyy-mm-dd] gets dates [from, to>
    :param to_date:                 [date or string as yyyy-mm-dd] gets dates [from, to>
    :param include_ikke_vurdert:    [bool] if true, it includes forecasts where danger_level = 0

    :return:
    """

    # get all warning and problems for this region and then loop though them joining them where dates match.
    region_warnings = gfa.get_warnings(region_ids, from_date, to_date, lang_key=lang_key)

    if not include_ikke_vurdert:
        all_non_zero_warnings = []

        for w in region_warnings:
            if w.danger_level != 0:
                all_non_zero_warnings.append(w)

        region_warnings = all_non_zero_warnings

    return region_warnings


def get_all_dangers(region_ids, from_date, to_date, lang_key=1):
    """Method does NOT include avalanche problems. Gets all avalanche dangers dangers, both forecasted and
    observed in given regions for a given time period.

    :param region_ids:          [int or list of ints]
    :param from_date:           [date or string as "YYYY-MM-DD"]
    :param to_date:             [date or string as "YYYY-MM-DD"]

    :return:
    """

    warnings = get_forecasted_dangers(region_ids, from_date, to_date, lang_key=lang_key)
    observed = get_observed_dangers(region_ids, from_date, to_date, lang_key=lang_key)

    all_dangers = warnings + observed

    # Sort by date
    all_dangers = sorted(all_dangers, key=lambda AvalancheDanger: AvalancheDanger.date)

    return all_dangers


if __name__ == "__main__":

    region_ids = [3010, 3011]   # Lyngen, Tromsø

    from_date = dt.date(2018, 1, 1)
    to_date = dt.date(2018, 1, 20)

    observed_dangers = get_observed_dangers(region_ids, from_date, to_date)
    forecasted_dangers = get_forecasted_dangers(region_ids, from_date, to_date)

    all = get_all_dangers(region_ids, from_date, to_date)
