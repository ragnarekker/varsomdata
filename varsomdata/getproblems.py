import datetime as dt
from varsomdata import getobservations as go
from varsomdata import getforecastapi as gfa
from varsomdata import makelogs as ml
from varsomdata import setcoreenvironment as cenv

# -*- coding: utf-8 -*-
__author__ = 'raek'


class AvalancheProblem():

    def __init__(self, region_regobs_id_inn, region_name_inn, date_inn, order_inn, cause_name_inn, source_inn, problem_inn=None):
        """The AvalancheProblem object is useful since there are 3 different tables to get regObs-data from and 2 tables
        from forecasts. Thus avalanche problems are saved in 5 ways. The structure of this object is based on the
        "latest" model and the other/older ways to save avalanche problems on may be mapped to these.

        Parameters part of the constructor:
        :param region_regobs_id_inn:       [int]       Region ID is as given in ForecastRegionKDV.
        :param region_name_inn:     [String]    Region name as given in ForecastRegionKDV.
        :param date_inn:            [Date]      Date for avalanche problem.
        :param order_inn:           [int]       The index* of the avalanche problem.
        :param cause_name_inn:      [String]    Avalanche cause/weak layer. For newer problems this as given in AvalCauseKDV.
        :param source_inn:          [String]    The source of the data. Normally 'Observation' or 'Forecast'.
        :param problem_inn          [String]    The avalanche problem. Not given in observations (only forecasts) pr nov 2016.

        * Index doensnt allways start on 0 and count +1. A rule is that the higher the index the higher the priority.

        Other variables declared with initiation:
        metadata = []       [list with dictionaries [{},{},..] ]
        """

        # In nov 2016 we updated all regions to have ids in th 3000´s. GIS and regObs equal.
        # Before that GIS har numbers 0-99 and regObs 100-199. Messy..
        # Convention is regObs ids always
        if region_regobs_id_inn < 100:
            region_regobs_id_inn += 100

        self.metadata = {}              # dictionary {key:value, key:value, ..}
        self.region_regobs_id = region_regobs_id_inn
        self.region_name = region_name_inn
        self.date = None
        self.set_date(date_inn)
        self.order = order_inn
        self.cause_tid = None           # [int] Avalanche cause ID(TID in regObs). Only used in avalanche problems from dec 2014 and newer.
        self.cause_name = cause_name_inn
        self.source = source_inn
        self.problem = problem_inn
        self.problem_tid = None         # [int]       ID used in regObs
        self.main_cause = None          # [String] Problems/weaklayers are grouped into main problems the season 2014/15

        # The following variables are declared on a needed basis.

        # self.regid = None               # [int]       Registration ID in regObs.
        # self.municipal_name = None      # [String]
        self.aval_type = None           # [String]    Avalanche Type
        self.aval_type_tid = None       # [int]       ID used in regObs
        self.aval_size = None           # [String]    Avalanche Size
        self.aval_size_tid = None       # [int]       ID used in regObs
        # self.aval_trigger = None        # [String]    Avalanche Trigger
        # self.aval_trigger_tid = None    # [int]       ID used in regObs
        # self.aval_probability = None    # [String]    Probability for an avalanche to release
        # self.aval_distribution = None   # [String]    Avalanche distribution in the terrain. Named AvalPropagation in regObs.
        # self.registration_time = None   # [datetime]  DtRegTime is when problem was registrered by the regobs database.
        # self.regobs_table = None        # [String]    Table in regObs database.
        # self.url = None                 # [String]    Url to forecast or observation
        # self.nick_name = None           # [String]
        # self.competence_level = None    # [String]
        # self.danger_level = None        # [Int]       In some cases it is conveniant to add the forecasted danger level to the object.
        # self.danger_level_name = None   # [String]
        # self.eaws_problem = None        # [String]  in english
        # self.cause_attribute_crystal_tid = None   # [Int]
        # self.cause_attribute_light_tid = None     # [Int]
        # self.cause_attribute_soft_tid = None      # [Int]
        # self.cause_attribute_thin_tid = None      # [Int]
        # self.cause_attribute_crystal = None       # [String]
        # self.cause_attribute_light = None         # [String]
        # self.cause_attribute_soft = None          # [String]
        # self.cause_attribute_thin = None          # [String]

    def set_date(self, date_inn):

        # makes sure we only have the dat, but we keep the datetime as metadata
        if isinstance(date_inn, dt.datetime):
            self.add_metadata("Original DtObsTime", date_inn)
            date_inn = date_inn.date()

        self.date = date_inn

    def set_registration_time(self, registration_time_inn):
        # DtRegTime is when the problem was registered in regObs.
        self.registration_time = registration_time_inn

    def set_cause_tid(self, cause_tid_inn):
        self.cause_tid = cause_tid_inn

    def set_municipal(self, municipal_inn):
        try:
            self.municipal_name = municipal_inn
        except ValueError:
            print("Got ValueError on setting municipal name on {0} for {1}.")\
                .format(self.date, self.region_name)
        except:
            print("Got un expected error on setting municipal name on {0} for {1}.")\
                .format(self.date, self.region_name)

    def set_regid(self, regid_inn):
        self.regid = regid_inn

    def set_url(self, url_inn):
        self.url = url_inn

    def set_aval_type(self, aval_type_inn, aval_type_tid_inn=None):
        self.aval_type = aval_type_inn
        self.aval_type_tid = aval_type_tid_inn

    def set_aval_size(self, aval_size_inn, aval_size_tid_inn=None):
        self.aval_size = aval_size_inn
        self.aval_size_tid = aval_size_tid_inn

    def set_aval_trigger(self, aval_trigger_inn, aval_trigger_tid_inn=None):
        self.aval_trigger = aval_trigger_inn
        self.aval_trigger_tid = aval_trigger_tid_inn

    def set_aval_probability(self, aval_probability_inn):
        self.aval_probability = aval_probability_inn


    def set_aval_distribution(self, aval_distribution_inn):
        self.aval_distribution = aval_distribution_inn

    def set_aval_cause_attributes(self, problem_object):

        if isinstance(problem_object, go.AvalancheEvalProblem2):
            self.cause_attribute_crystal_tid = problem_object.AvalCauseAttributeCrystalTID
            self.cause_attribute_light_tid = problem_object.AvalCauseAttributeLightTID
            self.cause_attribute_soft_tid = problem_object.AvalCauseAttributeSoftTID
            self.cause_attribute_thin_tid = problem_object.AvalCauseAttributeThinTID

            self.cause_attribute_crystal = problem_object.AvalCauseAttributeCrystalName
            self.cause_attribute_light = problem_object.AvalCauseAttributeLightName
            self.cause_attribute_soft = problem_object.AvalCauseAttributeSoftName
            self.cause_attribute_thin = problem_object.AvalCauseAttributeThinName

            # This was fixed on api in nov 2017.
            # if self.lang_key == 2 and self.cause_attribute_crystal_tid > 0:
            #     self.cause_attribute_crystal = 'A big and identifiable crystal in the weak layer.'
            # if self.lang_key == 2 and self.cause_attribute_light_tid > 0:
            #     self.cause_attribute_light = 'The weak layer collapses easily and clean (easy propagation).'
            # if self.lang_key == 2 and self.cause_attribute_soft_tid > 0:
            #     self.cause_attribute_soft = 'The overlying slab is soft.'
            # if self.lang_key == 2 and self.cause_attribute_thin_tid > 0:
            #     self.cause_attribute_thin = 'The collapsing weak layer is thin < 3 cm.'

        else:
            ml.log_and_print('getproblems -> AvalancheProblem.set_aval_cause_attributes: Avalanche problem class wrong for cause attributes.')


    def set_problem(self, problem_inn, problem_tid_inn=None):
        self.problem = problem_inn
        self.problem_tid = problem_tid_inn

    def set_regobs_table(self, table_inn):
        self.regobs_table = table_inn

    def set_nick_name(self, nick_name_inn):
        self.nick_name = nick_name_inn

    def set_competence_level(self, competence_level_inn):
        self.competence_level = competence_level_inn

    def set_danger_level(self, danger_level_name_inn, danger_level_inn):
        self.danger_level = danger_level_inn
        self.danger_level_name = danger_level_name_inn

    def set_lang_key(self, lang_key_inn):
        self.lang_key = lang_key_inn

    def map_to_eaws_problems(self):
        """

        :return:

        eaws_problems = ['New snow',
                         'Wind-drifted snow',
                         'Persistent waek layers',
                         'Wet snow',
                         'Gliding snow']
        """

        # problem_tid is available in the forecasts.
        problem_tid_to_eaws_problems = {
                 0: 'Not given',
                 3: 'New snow',                # Loose dry avalanches
                 5: 'Wet snow',                # Loose wet avalanches
                 7: 'New snow',                # Storm slab avlanches
                10: 'Wind-drifted snow',       # Wind slab avalanches
                20: 'New snow',                # New snow
                30: 'Persistent weak layers',  # Persistent slab avalanches
                35: 'Persistent weak layers',  # Persistent weak layer
                37: 'Persistent weak layers',  # Persistent deep slab avalanches
                40: 'Wet snow',                # Wet snow
                45: 'Wet snow',                # Wet slab avalanches
                50: 'Gliding snow'}            # Glide avalanches

        # AvalancheExtKDV holds information on avalanche type (self.aval_type)
        # id40:Corice and id30:Slush flow not included
        # id20:Dry slab in not uniquely mapped to an avalanche problem
        avalanche_ext_tid_to_eaws_problems = {
                10: 'New snow',     # Loose dry avalanche
                15: 'Wet snow',     # Loose wet avalanche
                #20: ,              # Dry slab avalanche
                25: 'Wet snow',     # Wet slab avalanche
                27: 'Gliding snow'} # Glide avalanche
                #30: ,              # Slush avalanche
                #40: ,              # Cornice

        aval_cause_to_eaws_problems = {
                #10: ,   # Buried weak layer of new snow
                #11: ,   # Buried weak layer of surface hoar
                #12: ,   # Buried weak layer of graupel
                #13: ,   # Buried weak layer of faceted snow near surface
                #14: ,   # Poor bonding between crust and overlying snow
                15: 'Wind-drifted snow',   # Poor bonding between layers in wind deposited snow
                #16: ,   # Buried weak layer of faceted snow near the ground
                #17: ,   # Buried weak layer of faceted snow near vegetation
                #18: ,   # Buried weak layer of faceted snow above a crust
                #19: ,   # Buried weak layer of faceted snow beneath a crust
                20: 'Gliding snow',   # Wet snow / melting near the ground
                21: 'Wet snow',   # Wet snow on the surface
                22: 'Wet snow'}   # Water pooling in / above snow layers
                #23: ,   # Water - saturated snow
                #24: ,   # Loose snow
                #25: ,   # Rain / rise in temperature / solar heating

        self.eaws_problem = None

        if self.source == 'Observation':
            # first try some avalanche types that are uniquely connected to eaws problem
            if self.aval_type_tid in avalanche_ext_tid_to_eaws_problems.keys():
                self.eaws_problem = avalanche_ext_tid_to_eaws_problems[self.aval_type_tid]

            # then try some causes that are uniquely linked to eaws problems
            if self.eaws_problem is None:
                if self.cause_tid in aval_cause_to_eaws_problems.keys():
                    self.eaws_problem = aval_cause_to_eaws_problems[self.cause_tid]

            # if eaws problem still none, try some cases of dry slabs
            if self.eaws_problem is None:
                if self.aval_type_tid == 20:
                    if self.cause_tid in [10, 14]:
                        # only the AvalancheEvalProblem2 table has case attributes
                        if self.regobs_table == 'AvalancheEvalProblem2':
                            if self.cause_attribute_soft_tid > 0:
                                self.eaws_problem = 'New snow'
                            else:
                                self.eaws_problem = 'Wind-drifted snow'
                                #self.eaws_problem = None
                    if self.cause_tid in [11, 13, 16, 17, 18, 19]:
                        self.eaws_problem = 'Persistent weak layers'

        elif self.source == 'Forecast':
            if self.problem_tid is not None:
                self.eaws_problem = problem_tid_to_eaws_problems[self.problem_tid]

        else:
            ml.log_and_print('getproblems.py -> AvalancheProblem.map_to_eaws_problems: Unknown source.')

    def add_metadata(self, key, value):
        self.metadata[key] = value


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

            problem = AvalancheProblem(region_id, region_name, date, order, cause_name, source)

            problem.set_regobs_table('AvalancheEvaluation')
            problem.set_regid(p.RegID)
            problem.set_url('{0}{1}'.format(cenv.registration_basestring, p.RegID))
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

            problem = AvalancheProblem(region_id, region_name, date, order, cause_name, source)

            problem.set_regobs_table('AvalancheEvalProblem')
            problem.set_regid(p.RegID)
            problem.set_url('{0}{1}'.format(cenv.registration_basestring, p.RegID))
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

        problem = AvalancheProblem(region_id, region_name, date, order, cause_name, source)

        problem.set_regobs_table('AvalancheEvalProblem2')
        problem.set_regid(p.RegID)
        problem.set_url('{0}{1}'.format(cenv.registration_basestring, p.RegID))
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
        warnings = gfa.get_warnings(region_ids=region_ids, from_date=from_date, to_date=to_date, lang_key=lang_key)

    elif problems_from == 'Forecast':
        evaluations_1 = []
        evaluations_2 = []
        eval_problems_2 = []
        warnings = gfa.get_warnings(region_ids=region_ids, from_date=from_date, to_date=to_date, lang_key=lang_key)

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
            warnings = gfa.get_warnings(region_ids=region_ids, from_date=from_date, to_date=to_date, lang_key=lang_key)

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