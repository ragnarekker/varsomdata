# -*- coding: utf-8 -*-
__author__ = 'raek'


import getregobs as gro
import fencoding as fe
import datetime
import getkdvelements as gkdv


class AvalancheProblem():


    def __init__(self, region_id_inn, region_name_inn, date_inn, order_inn, cause_name_inn, source_inn):
        '''
        The AvalancheProblem object is useful since there are 3 different tables to get regObs-data from and 2 tables
        from forecasts. Thus avalanche problems are saved in 5 ways. The structure of this object is based on the
        "latest" model and the other/older ways to save avalanche problems on may be mapped to these.

        Parameters part of the constructor:
        :param region_id_inn:       [int]       Region ID is as given in ForecastRegionKDV.
        :param region_name_inn:     [String]    Region name as given in ForecastRegionKDV.
        :param date_inn:            [Date]      Date for avalanche problem.
        :param order_inn:           [int]       The order* of the avalanche problem.
        :param cause_name_inn:      [String]    Avalanche cause. For newer problems this as given in AvalCauseKDV.
        :param source_inn:          [String]    The source of the data. Normally 'Observasjon' og 'Varsel'.

        * Order should be indexed from 0 (main problem) and up, but I see that they often start on higher indexes
          and don't always have a step of +1. A rule is that the higher the order the higher the priority.

        Other variables:
        regid               [int]
        municipal_name      [String]
        cause_tid           [int]           Is only used in avalanche problems from dec 2014 and newer
        main_cause          [String]        Avalanche causes are grouped in main causes
        aval_type           [String]
        aval_size           [String]
        aval_trigger        [String]
        aval_probability    [String]
        aval_distribution   [String]        Named AvalPropagation in regObs
        problem_combined    [String]
        regobs_view         [String]
        url = None          [String]
        metadata = []       [list with dictionaries [{},{},..] ]
        '''

        self.metadata = {}              # dictionary {key:value, key:value, ..}
        self.region_id = region_id_inn
        self.region_name = fe.remove_norwegian_letters(region_name_inn)
        self.set_date(date_inn)
        self.order = order_inn
        self.cause_tid = None           # [int]     Avalanche cause ID (in regObs TID)
        self.set_cause_name(cause_name_inn)
        self.source = fe.remove_norwegian_letters(source_inn)

        self.regid = None               # int
        self.municipal_name = None      # [String]
        self.main_cause = None          # [String]
        self.aval_type = None           # [String]
        self.aval_size = None           # [String]
        self.aval_trigger = None        # [String]
        self.aval_probability = None    # [String]
        self.aval_distribution = None   # [String]
        self.problem_combined = None    # [String]
        self.regobs_view = None         # [String]
        self.url = None                 # [String]
        self.nick_name = None           # [String]


    def set_date(self, date_inn):

        # makes sure we only have the date
        if isinstance(date_inn, datetime.datetime):
            self.add_metadata("Original datetime", date_inn)
            date_inn = date_inn.date()

        self.date = date_inn


    def set_cause_name(self, cause_name_inn):
        # Map wrong use of IDs in AvalCauseKDV in forecasts 2014-15

        aval_cause_kdv = gkdv.get_kdv('AvalCauseKDV')
        cause_name_inn = fe.remove_norwegian_letters(cause_name_inn)

        if (cause_name_inn == aval_cause_kdv[26].Name):
            self.add_metadata('Original AvalCauseName', cause_name_inn)
            cause_name_inn = aval_cause_kdv[20]
        if (cause_name_inn == aval_cause_kdv[27].Name):
            self.add_metadata('Original AvalCauseName', cause_name_inn)
            cause_name_inn = aval_cause_kdv[23]
        if (cause_name_inn == aval_cause_kdv[28].Name):
            self.add_metadata('Original AvalCauseName', cause_name_inn)
            cause_name_inn = aval_cause_kdv[24]
        if (cause_name_inn == aval_cause_kdv[29].Name):
            self.add_metadata('Original AvalCauseName', cause_name_inn)
            cause_name_inn = aval_cause_kdv[25].Name

        self.cause_name = cause_name_inn


    def set_cause_tid(self, cause_tid_inn):
        # Map wrong use of IDs in AvalCauseKDV in forecasts 2014-15

        if cause_tid_inn == 29:
            self.add_metadata('Original AvalCauseTID', cause_tid_inn)
            cause_tid_inn = 25
        if cause_tid_inn == 28:
            self.add_metadata('Original AvalCauseTID', cause_tid_inn)
            cause_tid_inn = 24
        if cause_tid_inn == 27:
            self.add_metadata('Original AvalCauseTID', cause_tid_inn)
            cause_tid_inn = 23
        if cause_tid_inn == 26:
            self.add_metadata('Original AvalCauseTID', cause_tid_inn)
            cause_tid_inn = 20

        self.cause_tid = cause_tid_inn


    def set_main_cause(self, cause_name_inn):
        '''
        aval_cause_kdv{
            0: 'Ikke gitt',
            1: 'Regn',
            2: 'Oppvarming',
            3: 'Ingen gjenfrysing',
            4: 'Paalagring',
            5: 'Svake lag',
            6: 'Regn + oppvarming',
            7: 'Regn + oppvarm + ingen gj.frys',
            8: 'Vind',
            9: 'Oppvarm + ingen gj.frys',
            10: 'Lag med loes nysnoe',
            11: 'Lag med overflaterim',
            12: 'Lag med sproehagl',
            13: 'Lag med kantkornet snoe',
            14: 'Glatt skare',
            15: 'I fokksnoeen',
            16: 'Kantkornet ved bakken',
            17: 'Kantkornet rundt vegetasjon',
            18: 'Kantkornet over skaren',
            19: 'Kantkornet under skaren',
            20: 'Gjennomfuktet fra bakken',
            21: 'Gjennomfuktet fra overflaten',
            22: 'Opphopning over skaren',
            23: 'Snoedekket er overmettet av vann',
            24: 'Ubundet loes snoe',
            25: 'Regn/temperaturstigning',
            26: 'Smelting fra bakken',
            27: 'Vannmettet snoe',
            28: 'Loes toerr snoe',
            29: 'Regn / temperaturstigning / soloppvarming'
        }'''

        if self.cause_tid in [24, 28]:
            self.main_cause = 'Nysnoe'
        elif self.cause_tid in [10, 15]:
            self.main_cause = 'Fokksnoe'
        elif self.cause_tid in [11, 12, 13, 14, 16, 17, 18, 19]:
            self.main_cause = 'Vedvarende svakt lag'
        elif self.cause_tid in [20, 21, 22, 23, 25, 26, 27, 29]:
            self.main_cause = 'Vaat snoe'
        else:
            self.main_cause = 'Ingen funnet for AvalCauseTID={0}'.format(self.cause_tid)


    def set_municipal(self, municipal_inn):
        try:
            self.municipal_name = fe.remove_norwegian_letters(municipal_inn)
        except ValueError:
            print "Got ValueError on setting municipal name on {0} for {1}."\
                .format(self.date, self.region_name)
        except:
            print "Got un expected error on setting municipal name on {0} for {1}."\
                .format(self.date, self.region_name)


    def set_regid(self, regid_inn):
        self.regid = regid_inn


    def set_url(self, url_inn):
        self.url = url_inn


    def set_aval_type(self, aval_type_inn):
        aval_type = fe.remove_norwegian_letters(aval_type_inn)
        if aval_type != "Ikke gitt":
            self.aval_type = aval_type


    def set_aval_size(self, aval_size_inn):
        aval_size = fe.remove_norwegian_letters(aval_size_inn)
        if aval_size != "Ikke gitt":
            self.aval_size = aval_size


    def set_aval_trigger(self, aval_trigger_inn):
        self.aval_trigger = aval_trigger_inn


    def set_aval_probability(self, aval_probability_inn):
        self.aval_probability = aval_probability_inn


    def set_aval_distribution(self, aval_distribution_inn):
        self.aval_distribution = aval_distribution_inn


    def set_problem_combined(self, problem_inn):
        self.problem_combined = fe.remove_norwegian_letters(problem_inn)


    def set_regobs_view(self, view_inn):
        self.regobs_view = view_inn


    def add_metadata(self, key, value):
        self.metadata[key] = value


    def set_nick_name(self, nick_name_inn):
        self.nick_name = nick_name_inn


def get_all_problems(region_id, start_date, end_date, max_time_span=200):
    '''
    Method points to getregobs.py. Comment below is copied from there.

    Method returns all avalanche problems on views AvalancheProblemV, AvalancheEvalProblemV, AvalancheEvalProblem2V,
    AvalancheWarningV and AvalancheWarnProblemV.

    Method takes the region ID as used in ForecastRegionKDV.

    Note: the queries in Odata goes from a date (but not including) this date. Mathematically <from, to].

    :param region_id:
    :param start_str:
    :param end_str:
    :param max_time_span:   [int]   To avoid datacropping in the requests to OData a max time span can be given.
                                    If your request is greater than this value, multiple queries are made.

    :return problems:       [list]  List of AvalancheProblem objects
    '''

    return gro.get_all_problems_with_date(region_id, start_date, end_date, max_time_span=max_time_span)


if __name__ == "__main__":

    region_id = 129
    start_date = "2015-04-09"
    end_date = "2015-05-10"

    #all_problems_step10 = get_all_problems(region_id, start_date, end_date, max_time_span=10)
    all_problems_step100 = get_all_problems(region_id, start_date, end_date, max_time_span=100)

    a = 1