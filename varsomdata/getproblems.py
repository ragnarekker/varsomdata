import datetime as dt
from varsomdata import getobservations as go
from varsomdata import getforecastapi as gfa
from varsomdata import varsomclasses as vc
from utilities import makelogs as ml
import setenvironment as env

# -*- coding: utf-8 -*-
__author__ = 'raek'


def _map_eval1_to_problem(evaluations_1):
    """Maps the AvalancheEvaluations listed AvalancheEvalProblem0 object to the common AvalancheProblem object.
    The AvalancheProblem class is the common class for all generation problems and forecasts.

    :param evaluations_1:   [list of AvalancheEvaluation] These are the classes used on getobservations.py
    :return:                [list of AvalancheProblem]
    """

    problems = []

    for e in evaluations_1:
        for p in e.AvalancheProblems:

            region_id = p.ForecastRegionTID
            region_name = p.ForecastRegionName
            date = p.DtObsTime
            order = p.AvalancheProblemID
            cause_name = p.AvalancheProblemName
            source = 'Observation'

            problem = vc.AvalancheProblem(region_id, region_name, date, order, cause_name, source)

            problem.set_regobs_table('AvalancheEvaluation')
            problem.set_regid(p.RegID)
            problem.set_url('{0}{1}'.format(env.registration_basestring, p.RegID))
            problem.set_registration_time(p.DtRegTime)
            problem.set_municipal(p.MunicipalName)
            problem.set_nick_name(p.NickName)
            problem.set_competence_level(p.CompetenceLevelName)
            problem.add_metadata('Original data', p.OriginalData)
            problem.set_lang_key(p.LangKey)

            problems.append(problem)

    return problems


def _map_eval2_to_problem(evaluations_2):
    """Maps the AvalancheEvaluations2 listed AvalancheEvalProblem1 object to the common AvalancheProblem object.
    The AvalancheProblem class is the common class for all generation problems and forecasts.

    :param evaluations_2:   [list of AvalancheEvaluations] These are the classes used on getobservations.py
    :return:                [list of AvalancheProblem]
    """

    problems = []

    for e in evaluations_2:
        for p in e.AvalancheProblems:

            region_id = p.ForecastRegionTID
            region_name = p.ForecastRegionName
            date = p.DtObsTime
            order = p.AvalancheProblemID
            cause_name = '{0}, {1}'.format(p.AvalCauseName, p.AvalCauseExtName)
            source = 'Observation'

            problem = vc.AvalancheProblem(region_id, region_name, date, order, cause_name, source)

            problem.set_regobs_table('AvalancheEvalProblem')
            problem.set_regid(p.RegID)
            problem.set_url('{0}{1}'.format(env.registration_basestring, p.RegID))
            problem.set_registration_time(p.DtRegTime)
            problem.set_municipal(p.MunicipalName)
            problem.set_nick_name(p.NickName)
            problem.set_competence_level(p.CompetenceLevelName)
            problem.add_metadata('Original data', p.OriginalData)
            problem.set_lang_key(p.LangKey)

            problem.set_aval_size(p.DestructiveSizeExtName) # dont bother with the TIDs on the types no longer in use.
            problem.set_aval_type(p.AvalancheExtName)      # dont bother with the TIDs on the types no longer in use.
            problem.set_aval_trigger(p.AvalTriggerSimpleName) # dont bother with the TIDs on the types no longer in use.

            problems.append(problem)

    return problems


def _map_eval_problem_2_to_problem(eval_problem_2):
    """Maps the listed AvalancheEvalProblem2 objects from getobservations.py to the common AvalancheProblem object.
    The AvalancheProblem class is the common class for all generation problems and forecasts.

    :param evaluations_2:   [list of AvalancheEvaluations]
    :return:                [list of AvalancheProblem]
    """

    problems = []

    for p in eval_problem_2:
        region_id = p.ForecastRegionTID
        region_name = p.ForecastRegionName
        date = p.DtObsTime
        order = p.AvalancheProblemID
        cause_name = p.AvalCauseName
        source = 'Observation'

        problem = vc.AvalancheProblem(region_id, region_name, date, order, cause_name, source)

        problem.set_regobs_table('AvalancheEvalProblem2')
        problem.set_regid(p.RegID)
        problem.set_url('{0}{1}'.format(env.registration_basestring, p.RegID))
        problem.set_registration_time(p.DtRegTime)
        problem.set_municipal(p.MunicipalName)
        problem.set_nick_name(p.NickName)
        problem.set_competence_level(p.CompetenceLevelName)
        problem.add_metadata('Original data', p.OriginalData)
        problem.set_lang_key(p.LangKey)

        problem.set_cause_tid(p.AvalCauseTID)
        problem.set_aval_cause_attributes(p)

        problem.set_aval_size(p.DestructiveSizeName)
        problem.set_aval_type(p.AvalancheExtName, aval_type_tid_inn=p.AvalancheExtTID)
        problem.set_aval_trigger(p.AvalTriggerSimpleName)

        problems.append(problem)

    return problems


def _map_warning_to_problem(warnings):
    """Forcasting api returns AvalancheDanger objects where the AvalancheProblems are listed. Classification is
    tipp topp so we only need to pick out the avalanche problems and return.

    :param warnings:
    :return:
    """
    problems = []
    for w in warnings:
        problems +=  w.avalanche_problems

    return problems


def get_forecasted_problems(region_ids, from_date, to_date, add_danger_level=True, lang_key=1):
    """Function returning only forecasted problems. A specialized call of the more generic get_all_problems

    :param region_ids:
    :param from_date:
    :param to_date:
    :param add_danger_level:
    :return:
    """

    problems = get_all_problems(region_ids, from_date, to_date,
                                add_danger_level=add_danger_level,
                                problems_from='Forecast', lang_key=lang_key)

    return problems


def get_observed_problems(region_ids, from_date, to_date, add_danger_level=False, lang_key=1):
    """Special case of get_all_problems selecting only from observations.

    :param region_ids:          [int or list of ints] ForecastRegionTID
    :param from_date:           [date or string as "YYYY-MM-DD"]
    :param to_date:             [date or string as "YYYY-MM-DD"]
    :param add_danger_level:    [bool] If false danger level will not be added to the problem
    :return:
    """

    problems = get_all_problems(region_ids, from_date, to_date, add_danger_level=add_danger_level,
                                problems_from='Observation', lang_key=lang_key)

    return problems


def get_all_problems(region_ids, from_date, to_date, add_danger_level=True, problems_from='All', lang_key=1):
    """Method returns all avalanche problems on views AvalancheProblemV, AvalancheEvalProblemV,
    AvalancheEvalProblem2V, AvalancheWarningV and AvalancheWarnProblemV. Method takes the
    region ID as used in ForecastRegionKDV.

    Note: the queries in Odata goes from a date (but not including) this date. Mathematically <from, to].

    :param region_ids:          [int or list of ints] ForecastRegionTID
    :param from_date:           [date or string as "YYYY-MM-DD"]
    :param to_date:             [date or string as "YYYY-MM-DD"]
    :param add_danger_level:    [bool] If false danger level will not be added to the problem
    :param problems_from:       [string] 'All', 'Forecast' or 'Observation'

    :return all_problems:       [list] List of AvalancheProblem objects
    """

    # If input isn't a list, make it so
    if not isinstance(region_ids, list):
        region_ids = [region_ids]

    if problems_from == 'All':
        evaluations_1 = go.get_avalanche_evaluation(region_ids=region_ids, from_date=from_date, to_date=to_date, lang_key=lang_key)
        evaluations_2 = go.get_avalanche_evaluation_2(region_ids=region_ids, from_date=from_date, to_date=to_date, lang_key=lang_key)
        eval_problems_2 = go.get_avalanche_problem_2(region_ids=region_ids, from_date=from_date, to_date=to_date, lang_key=lang_key)
        warnings = gfa.get_avalanche_warnings_deprecated(region_ids=region_ids, from_date=from_date, to_date=to_date, lang_key=lang_key)

    elif problems_from == 'Forecast':
        evaluations_1 = []
        evaluations_2 = []
        eval_problems_2 = []
        warnings = gfa.get_avalanche_warnings_deprecated(region_ids=region_ids, from_date=from_date, to_date=to_date, lang_key=lang_key)

    elif problems_from == 'Observation':
        evaluations_1 = go.get_avalanche_evaluation(region_ids=region_ids, from_date=from_date, to_date=to_date, lang_key=lang_key)
        evaluations_2 = go.get_avalanche_evaluation_2(region_ids=region_ids, from_date=from_date, to_date=to_date, lang_key=lang_key)
        eval_problems_2 = go.get_avalanche_problem_2(region_ids=region_ids, from_date=from_date, to_date=to_date, lang_key=lang_key)
        warnings = []

    else:
        ml.log_and_print('getproblems.py -> get_all_problems: Unknown request problems_from={0}'.format(problems_from))
        return 'Unknown request problems_from={0}'.format(problems_from)

    problem_0 = _map_eval1_to_problem(evaluations_1)
    problem_1 = _map_eval2_to_problem(evaluations_2)
    problem_2 = _map_eval_problem_2_to_problem(eval_problems_2)
    problem_warn = _map_warning_to_problem(warnings)

    all_problems = problem_0 + problem_1 + problem_2 + problem_warn
    all_problems.sort(key=lambda AvalancheProblem: AvalancheProblem.date)

    # Will add all forecasted danger levels to the problems.
    if add_danger_level:

        # If only looking for observations, warnings with danger level not got.
        if problems_from == 'Observation':
            warnings = gfa.get_avalanche_warnings_deprecated(region_ids=region_ids, from_date=from_date, to_date=to_date, lang_key=lang_key)

        all_non_zero_warnings = [w for w in warnings if w.danger_level != 0]
        all_non_zero_warnings.sort(key=lambda AvalancheDanger: AvalancheDanger.date)

        # Lots of looping. Be smart. Keep track of last index since both lists are ordered by date. Break inner loop and go to next problem if forecasts are older than the problem.
        last_i = 0
        for p in all_problems:
            for i in range(last_i, len(all_non_zero_warnings), 1):

                if all_non_zero_warnings[i].date > p.date:
                    last_i = max(0, i-1-len(region_ids))
                    break

                elif p.date == all_non_zero_warnings[i].date and p.region_regobs_id == all_non_zero_warnings[i].region_regobs_id:
                    p.set_danger_level(all_non_zero_warnings[i].danger_level_name, all_non_zero_warnings[i].danger_level)

    return all_problems


if __name__ == "__main__":

    from varsomdata import getmisc as gm

    region_ids = gm.get_forecast_regions('2016-17')
    from_date = '2017-11-21'
    to_date = '2017-11-28'
    problems = get_observed_problems(region_ids, from_date, to_date, lang_key=2)

    for p in problems:
        p.map_to_eaws_problems()

    region_id = [3007]                  # Vestfinnmark
    from_date = dt.date(2017, 3, 10)
    to_date = dt.date(2017, 3, 20)

    all_problems_with_danger = get_all_problems(region_id, from_date, to_date, add_danger_level=True)

    a = 1